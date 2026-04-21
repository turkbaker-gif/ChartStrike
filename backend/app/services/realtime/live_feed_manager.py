import asyncio
import json
from datetime import datetime, date
from decimal import Decimal
from typing import Any

from fastapi import WebSocket


def _json_default(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


class LiveFeedManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)

    async def broadcast(self, event_type: str, payload: Any) -> None:
        message = json.dumps(
            {
                "type": event_type,
                "payload": payload,
            },
            default=_json_default,
        )

        stale: list[WebSocket] = []

        async with self._lock:
            for connection in self.active_connections:
                try:
                    await connection.send_text(message)
                except Exception:
                    stale.append(connection)

            for connection in stale:
                if connection in self.active_connections:
                    self.active_connections.remove(connection)


live_feed_manager = LiveFeedManager()