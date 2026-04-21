import asyncio

from app.services.realtime.live_feed_manager import live_feed_manager


class LiveEventService:
    @staticmethod
    def emit(event_type: str, payload):
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(live_feed_manager.broadcast(event_type, payload))
        except RuntimeError:
            asyncio.run(live_feed_manager.broadcast(event_type, payload))