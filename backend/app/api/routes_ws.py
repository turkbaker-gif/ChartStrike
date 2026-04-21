from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.services.realtime.live_feed_manager import live_feed_manager

router = APIRouter()


@router.websocket("/ws/live")
async def websocket_live_feed(websocket: WebSocket):
    await live_feed_manager.connect(websocket)

    try:
        while True:
            # Keep the socket open. Client may optionally send pings/subscriptions later.
            await websocket.receive_text()
    except WebSocketDisconnect:
        await live_feed_manager.disconnect(websocket)
    except Exception:
        await live_feed_manager.disconnect(websocket)