import json
import threading

import lark_oapi as lark
from core.config import LARK_APP_ID, LARK_APP_SECRET
from core.worker import Worker
from lark_oapi.api.im.v1 import *


class Controller(object):
    def __init__(self):
        # ====== 1. System control ======
        self.event_handler = (
            lark.EventDispatcherHandler.builder("", "")
            .register_p2_im_message_receive_v1(self.handle_message)
            .build()
        )
        self.wsClient = lark.ws.Client(
            app_id=LARK_APP_ID,
            app_secret=LARK_APP_SECRET,
            event_handler=self.event_handler,
            log_level=lark.LogLevel.DEBUG,
        )

        self.received_messages: List[str] = []

        # ====== 2. Worker definition ======
        self.workers: dict[str:Worker] = {}

    def _need_process_message(self, data: P2ImMessageReceiveV1) -> bool:
        if (
            data.event.message.chat_type == "p2p"
            and data.event.message.message_id not in self.received_messages
        ):
            return True
        return False

    def _preprocess_message(self, data: P2ImMessageReceiveV1):
        chat_id = data.event.message.chat_id
        message_id = data.event.message.message_id
        message_text = json.loads(data.event.message.content)["text"]
        return chat_id, message_id, message_text

    def handle_message(self, data: P2ImMessageReceiveV1) -> None:
        if not self._need_process_message(data):
            return
        chat_id, message_id, message_text = self._preprocess_message(data)

        threading.Thread(
            target=self.run_worker,
            args=(message_text, chat_id),
        ).start()

    def run_worker(self, message_text: str, chat_id: str) -> None:
        worker = Worker(chat_id=chat_id)
        worker.run(url=message_text)

    def run(self):
        self.wsClient.start()
