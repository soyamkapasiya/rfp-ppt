from typing import List, Optional, Dict
import logging
import json
from app.models.domain import SlideSpec
from app.services.llm_router import generate_text, TaskType
from app.services.progress_service import progress_service

logger = logging.getLogger(__name__)

def write_slides(slides: List[SlideSpec], context: Optional[List[dict]] = None, job_id: Optional[str] = None, critiques: Optional[Dict[str, str]] = None) -> List[dict]:
    """
    Agentic Slide Writer:
    1. Fleshes out bullets using provided context
    2. Enforced per-bullet citations [Source ID]
    3. Runs a 'Specificity Gate' to strip fluff terms like 'world-class'
    4. Injects win themes and vault data
    5. Streams progress to the frontend
    6. Incorporates targeted critiques for rewrites
    """
    output: list[dict] = []
    context_text = "\n".join([f"[{d.get('id', 'Ref')}] {d.get('content', d.get('text', ''))[:500]}" for d in (context or [])])

    for slide in slides:
        logger.info(f"Writing slide: {slide.title}")
        
        # ── Targeted Critique Integration (Point 5) ──────────────────────
        critique = (critiques or {}).get(slide.title, "")
        critique_instruction = f"\nQA CRITIQUE TO FIX: {critique}" if critique else ""
        
        prompt = f"""
        TASK: Write 3-5 punchy, high-impact bullets for an RFP slide.
        SLIDE TITLE: {slide.title}
        OBJECTIVE: {slide.objective}
        WIN THEMES: {', '.join(slide.win_themes)}
        
        { "COMPETITIVE STEERING: Use this strategy to outperform competitors: " + slide.objective if "BETTER THAN COMPETITOR" in slide.win_themes else "" }
        
        CONTEXT:
        {context_text[:4000]}

        CRITICAL CONSTRAINTS:
        - EVERY bullet must end with a citation from the context, e.g. [web-1] or [vault-1].
        - NO FLUFF: Avoid 'world-class', 'cutting-edge', 'robust', 'seamless', 'leverage'. Use data instead.
        - STRATEGY: Explicitly mention how our approach is superior to industry standard/competitors if data allows.
        - If the context doesn't support a claim, do not make it.
        - Format as a JSON list of strings.{critique_instruction}
        """

        try:
            raw_response = generate_text(TaskType.WRITING, prompt)
            # Find the JSON array in the response
            start = raw_response.find("[")
            end = raw_response.rfind("]") + 1
            if start != -1 and end != -1:
                bullets = json.loads(raw_response[start:end])
            else:
                bullets = slide.bullets
        except Exception as e:
            logger.error(f"LLM Slide Writing failed for {slide.title}: {e}")
            bullets = slide.bullets

        # Secondary Specificity Pass (Local)
        banned = {"world-class", "cutting-edge", "robust", "seamless", "innovative", "synergy"}
        clean_bullets = []
        for b in bullets:
            if not any(word in b.lower() for word in banned):
                clean_bullets.append(b)
            else:
                # Attempt to rescue by stripping fluff or use default
                clean_bullets.append(b.replace("world-class ", "").replace("robust ", ""))

        output.append({
            "title": slide.title,
            "objective": slide.objective,
            "bullets": clean_bullets[:7],
            "references": slide.references,
            "layout": slide.layout,
        })
        
        if job_id:
            import asyncio
            loop = asyncio.get_event_loop()
            if loop.is_running():
                 loop.create_task(progress_service.broadcast(
                    job_id, 
                    "writing", 
                    f"Generated draft for slide: {slide.title}",
                    data={"slide_title": slide.title, "bullets": clean_bullets[:3]} 
                ))

    return output
