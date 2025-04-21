from functools import wraps

from core.utils import get_time


def event(content: str, mode: str = "append"):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            self = args[0] if args else None
            if hasattr(self, "event_bus"):
                if self.event_bus.bot_processor.chat_id is not None:
                    self.event_bus.bot_processor.update_card(
                        f"[{get_time()}] {content}", mode=mode
                    )
                else:
                    print(f"[{get_time()}] {content}", end="")
            result = func(*args, **kwargs)
            return result

        return wrapper

    return actual_decorator
