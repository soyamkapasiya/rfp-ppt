import asyncio
import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class ProgressBroadcaster:
    """Manages WebSocket connections to stream AI pipeline progress."""
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, job_id: str, websocket: WebSocket):
        await websocket.accept()
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        self.active_connections[job_id].append(websocket)
        logger.debug("WebSocket connected for job %s", job_id)

    def disconnect(self, job_id: str, websocket: WebSocket):
        if job_id in self.active_connections:
            self.active_connections[job_id].remove(websocket)
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        logger.debug("WebSocket disconnected for job %s", job_id)

    async def broadcast(self, job_id: str, stage: str, message: str, data: dict = None):
        if job_id not in self.active_connections:
            return

        payload = {
            "job_id": job_id,
            "stage": stage,
            "message": message,
            "data": data or {}
        }
        
        dead_connections = []
        for connection in self.active_connections[job_id]:
            try:
                await connection.send_text(json.dumps(payload))
            except Exception:
                dead_connections.append(connection)
        
        for dead in dead_connections:
            self.disconnect(job_id, dead)

progress_service = ProgressBroadcaster()
