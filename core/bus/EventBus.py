from core.processor import BotProcessor


class EventBus(object):
    """docstring for EventBus."""

    def __init__(self, data_bus, chat_id: str = None):
        self.data_bus = data_bus
        self.chat_id = chat_id

        self.bot_processor = BotProcessor(data_bus=data_bus, chat_id=chat_id)

    def start_task(self):
        if self.chat_id is not None:
            self.bot_processor.send_card()
        else:
            print(
                f"开始分析仓库：{self.data_bus.owner}/{self.data_bus.repo}，当前模型：{self.data_bus.model}"
            )

    def finish_task(self, lark_file_id: str):
        if self.chat_id is not None:
            self.bot_processor.send_message(
                f"🎉 {self.data_bus.owner}/{self.data_bus.repo} 仓库分析文档已生成：https://bytedance.larkoffice.com/docx/{lark_file_id}"
            )
        else:
            print(
                f"🎉 {self.data_bus.owner}/{self.data_bus.repo} 仓库分析文档已生成：https://bytedance.larkoffice.com/docx/{lark_file_id}"
            )
