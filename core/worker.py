import os
import shutil

from core.bus.DataBus import DataBus
from core.bus.EventBus import EventBus
from core.config import LLM_MODEL
from core.processor import DocProcessor, MdProcessor, RepoProcessor
from core.utils import extract_repo_metadata, get_time


class Worker(object):
    """docstring for Worker."""

    def __init__(self, chat_id: str = None):

        self.data_bus = DataBus()
        self.event_bus = EventBus(data_bus=self.data_bus, chat_id=chat_id)

        self.repo_processor = RepoProcessor(
            data_bus=self.data_bus, event_bus=self.event_bus
        )
        self.md_processor = MdProcessor(
            data_bus=self.data_bus, event_bus=self.event_bus
        )
        self.doc_processor = DocProcessor(
            data_bus=self.data_bus, event_bus=self.event_bus
        )

        self.chat_id = chat_id

    def _clean(self):
        # NOTE(nkfyz): we cannot remove the tmporary lark cloud file, cause we have no permission
        shutil.rmtree(self.data_bus.repo_local_path)
        os.remove(self.data_bus.md_local_path)

    def run(self, url: str):
        self.data_bus.start_time = get_time()
        owner, repo = extract_repo_metadata(url)
        self.data_bus.owner = owner
        self.data_bus.repo = repo
        self.data_bus.model = LLM_MODEL

        self.event_bus.start_task()

        self.repo_processor.process(owner=owner, repo=repo)
        local_md_path = self.md_processor.process()
        lark_file_id = self.doc_processor.process(local_path=local_md_path)

        self.event_bus.finish_task(lark_file_id=lark_file_id)

        self._clean()

    # this function is for analyze local repo such as byted
    def run_on_local_path(self, local_path: str):
        self.data_bus.start_time = get_time()
        owner, repo = local_path.split("/")[-1], local_path.split("/")[-1]
        self.data_bus.owner = owner
        self.data_bus.repo = repo
        self.data_bus.model = LLM_MODEL

        self.repo_processor.process(owner=owner, repo=repo, local_path=local_path)
        local_md_path = self.md_processor.process()
        lark_file_id = self.doc_processor.process(local_path=local_md_path)

        self.event_bus.finish_task(lark_file_id=lark_file_id)

        self._clean()
