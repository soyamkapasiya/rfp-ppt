"""
manus_service.py – Agentic presentation generation via Manus AI.

This service integrates with the Manus AI API to generate high-end, 
premium slide decks based on the RFP research and planning findings.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings

logger = logging.getLogger(__name__)

class ManusService:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.manus_api_key
        self.base_url = "https://api.manus.ai/v1"
        
        # Manus AI API headers - including variations as seen in different docs
        headers = {
            "API_KEY": self.api_key,
            "X-API-KEY": self.api_key,
            "API-KEY": self.api_key,
            "api-key": self.api_key,
            "manus-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        self.client = httpx.AsyncClient(
            headers=headers,
            timeout=60.0,
            follow_redirects=True
        )

    async def create_slides_task(self, project_name: str, refined_content: str, slide_count: int = 15) -> str:
        """
        Starts a task on Manus AI to generate a professional PPT deck.
        
        We provide the 'best way' prompt which includes all our local research 
        and structured planning so Manus can focus on world-class layout and design.
        """
        if not self.api_key or self.api_key in {"", "xxx"}:
            raise ValueError("MANUS_API_KEY is not configured. Please replace 'xxx' in your .env file with a valid key from manus.im.")

        prompt = (
            f"Generate a premium, professional RFP response presentation for the project: '{project_name}'.\n\n"
            f"CONTEXT AND RESEARCH DATA:\n{refined_content}\n\n"
            f"REQUIREMENTS:\n"
            f"- Create approximately {slide_count} slides.\n"
            f"- Use a corporate, trust-building aesthetic (deep navy, gold, and clean white).\n"
            f"- IMPORTANT: Use ONLY 'Times New Roman' as the primary font for all text, headings, and titles. This is essential for 100% compatibility and professional legal/business standards.\n"
            f"- CRITICAL: Strictly avoid any decorative, geometric, or abstract display fonts. Every letter must be rendered correctly in Times New Roman without any symbol substitutions.\n"
            f"- Include a title slide, executive summary, technical architecture, and next steps.\n"
            f"- ORGANIZATION BRANDING:\n"
            f"  * Organization Name: shivanski technology llp\n"
            f"  * Contact Email: sales@shiavnski.in\n"
            f"  * Contact Phone: +91 7880058811\n"
            f"  * Website: https://www.shiavnski.in/\n"
            f"- Ensure all placeholders like '[Your Organization Name]' or 'solutions@organization.com' are replaced with the details above.\n"
            f"- Ensure every slide has punchy, readable bullets and high-end visual elements.\n"
            f"- Export the final result as a PowerPoint (.pptx) file."
        )

        try:
            response = await self.client.post(
                f"{self.base_url}/tasks",
                json={
                    "prompt": prompt,
                    "mode": "presentation",
                    "files": [] # Could include branding guidelines here if available
                }
            )
            response.raise_for_status()
            data = response.json()
            task_id = data.get("task_id") or data.get("id")
            
            if not task_id:
                logger.error("Manus API response missing task_id: %s", data)
                raise RuntimeError(f"Failed to get task_id from Manus API: {data}")
                
            logger.info("Manus AI task created: %s", task_id)
            return task_id
        except Exception as e:
            logger.error("Failed to create Manus AI task: %s", e)
            raise

    async def poll_task_result(self, task_id: str, job_id: str, timeout_mins: int = 10) -> Dict[str, Any]:
        """Polls the Manus API until the task is complete or times out."""
        from app.services.progress_service import progress_service
        
        start_time = asyncio.get_event_loop().time()
        max_duration = timeout_mins * 60
        
        # Propagation delay: Wait for the task to be indexed in the Manus backend
        logger.info("Task %s created. Waiting 5s for propagation...", task_id)
        await asyncio.sleep(5)

        logger.info("Started polling Manus task: %s for job %s", task_id, job_id)
        await progress_service.broadcast(job_id, "manus", f"Manus AI is thinking... (Task ID: {task_id})")

        while (asyncio.get_event_loop().time() - start_time) < max_duration:
            elapsed_total = asyncio.get_event_loop().time() - start_time
            try:
                response = await self.client.get(f"{self.base_url}/tasks/{task_id}")
                
                # Handle propagation lag (404) gracefully in the first 60 seconds
                if response.status_code == 404 and elapsed_total < 60:
                    logger.debug("Manus task %s not yet found (404). Retrying...", task_id)
                    await asyncio.sleep(10)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                status = data.get("status", "unknown").lower()
                logger.debug("Manus task %s status: %s", task_id, status)

                if status in {"completed", "success", "finished", "done"}:
                    logger.info("Manus AI task %s reached terminal state: %s", task_id, status)
                    await progress_service.broadcast(job_id, "manus", "Manus AI has finished the premium design!")
                    
                    # ── Extraction strategy: Search multiple result keys ─────────
                    url = data.get("download_url") or data.get("result_url") or data.get("url")
                    
                    if not url and isinstance(data.get("result"), dict):
                        res = data["result"]
                        url = res.get("download_url") or res.get("url") or res.get("pptx_url")
                    
                    if not url and data.get("files"):
                        pptx_files = [f for f in data["files"] if f.get("name", "").endswith(".pptx")]
                        if pptx_files:
                            url = pptx_files[0].get("download_url") or pptx_files[0].get("url")

                    # NEW: Search in 'output' for 'output_file' types (Modern Manus API)
                    if not url and data.get("output"):
                        for msg in data["output"]:
                            if not isinstance(msg, dict) or msg.get("role") != "assistant":
                                continue
                            for content_item in msg.get("content", []):
                                if not isinstance(content_item, dict): continue
                                if content_item.get("type") == "output_file":
                                    f_url = content_item.get("fileUrl")
                                    f_name = content_item.get("fileName", "")
                                    if f_url and f_name.endswith(".pptx"):
                                        url = f_url
                                        break
                            if url: break
                    
                    if url:
                        data["download_url"] = url
                        logger.info("Found Manus result URL: %s", url)
                    else:
                        logger.warning("Terminal state reached but no PPTX URL found in response: %s", data)
                    
                    return data
                
                elif status in {"failed", "error", "cancelled"}:
                    error = data.get("error") or data.get("message") or "Unknown Manus error"
                    logger.error("Manus AI task %s failed with status %s: %s", task_id, status, error)
                    raise RuntimeError(f"Manus AI Error ({status}): {error}")
                
                # Update progress
                m_elapsed = int(elapsed_total / 60)
                await progress_service.broadcast(job_id, "manus", f"Manus AI design in progress ({status})... {m_elapsed}m elapsed")
                
                await asyncio.sleep(20) # Slower polling frequency to be polite
            except Exception as e:
                if isinstance(e, RuntimeError): raise
                
                # Silent retry for 404s within propagation window
                if hasattr(e, 'response') and getattr(e.response, 'status_code', None) == 404 and elapsed_total < 60:
                    await asyncio.sleep(10)
                    continue
                    
                logger.warning("Error polling Manus task %s: %s", task_id, e)
                await asyncio.sleep(15)
        
        raise TimeoutError(f"Manus AI task {task_id} timed out after {timeout_mins} minutes")

    async def download_pptx(self, download_url: str, output_path: str) -> str:
        """Downloads the generated PPTX from Manus and saves it locally."""
        try:
            response = await self.client.get(download_url)
            response.raise_for_status()
            
            with open(output_path, "wb") as f:
                f.write(response.content)
            
            logger.info("Manus PPTX saved to %s", output_path)
            return output_path
        except Exception as e:
            logger.error("Failed to download Manus PPTX: %s", e)
            raise

    async def close(self):
        await self.client.aclose()
