import json

import lark_oapi as lark
from lark_oapi.api.im.v1 import *

from core.bus.DataBus import DataBus
from core.config import LARK_APP_ID, LARK_APP_SECRET
from core.templates.card import card_template


class BotProcessor(object):
    """docstring for BotProcessor."""

    def __init__(self, data_bus: DataBus, chat_id: str):
        self.data_bus = data_bus

        self.lark_client = (
            lark.Client.builder()
            .app_id(LARK_APP_ID)
            .app_secret(LARK_APP_SECRET)
            .build()
        )
        self.chat_id = chat_id

        self.card = card_template
        self.card_id = ""

    def send_emoji(self, emoji_code: str):
        pass

    def send_message(self, content: str):
        content = json.dumps({"text": content})

        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(self.chat_id)
                .msg_type("text")
                .content(content)
                .build()
            )
            .build()
        )
        response: CreateMessageResponse = self.lark_client.im.v1.message.create(request)
        if not response.success():
            raise Exception(
                f"Send message failed, code: {response.code}, msg: {response.msg}"
            )
        return response.data.message_id

    def send_card(self):
        self.card["header"]["subtitle"][
            "content"
        ] = f"{self.data_bus.owner}/{self.data_bus.repo} 仓库"
        self.card["body"]["elements"][0]["content"] = f"当前模型：{self.data_bus.model}"
        content = json.dumps(self.card)

        request = (
            CreateMessageRequest.builder()
            .receive_id_type("chat_id")
            .request_body(
                CreateMessageRequestBody.builder()
                .receive_id(self.chat_id)
                .msg_type("interactive")
                .content(content)
                .build()
            )
            .build()
        )
        response: CreateMessageResponse = self.lark_client.im.v1.message.create(request)
        if not response.success():
            raise Exception(
                f"Send card failed, code: {response.code}, msg: {response.msg}"
            )
        self.card_id = response.data.message_id

    def update_card(self, content: str, mode: str):
        if self.card_id == "":
            raise Exception("Card not sent yet, please send a card first.")
        if mode == "append":
            self.card["body"]["elements"].append(
                {
                    "tag": "markdown",
                    "content": content,
                    "text_align": "left",
                    "text_size": "normal",
                    "margin": "0px 0px 0px 0px",
                }
            )
        elif mode == "replace":
            self.card["body"]["elements"][-1]["content"] = content
        content = json.dumps(self.card)

        request: PatchMessageRequest = (
            PatchMessageRequest.builder()
            .message_id(self.card_id)
            .request_body(PatchMessageRequestBody.builder().content(content).build())
            .build()
        )
        response: PatchMessageResponse = self.lark_client.im.v1.message.patch(request)
        if not response.success():
            lark.logger.error(
                f"client.im.v1.message.patch failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
            )
            return
