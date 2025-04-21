import os
import threading
from collections import defaultdict

from anytree import LevelOrderIter, PostOrderIter

from core.bus.DataBus import DataBus
from core.config.config import BYTEDANCE_HTTP_PROXY, TEMPRORY_DIR
from core.fs.DirNode import DirNode
from core.model.llm import LLM
from core.utils import read_file


class RepoProcessor(object):
    """docstring for RepoProcessor."""

    def __init__(self, data_bus: DataBus, event_bus):
        self.data_bus = data_bus
        self.event_bus = event_bus

        self.owner = None
        self.repo = None
        self.local_path = None

        self.llm = LLM(data_bus=self.data_bus, event_bus=self.event_bus)

        self.root_node = None
        self.filetree = {}

    def _build_filetree(self):
        root_path = self.local_path
        root_node = DirNode(name=f"{self.repo}", parent=None, real_path=root_path)
        path_to_node: dict[str, DirNode] = {root_path: root_node}
        for path, dirs, files in os.walk(root_path):
            current_node = path_to_node.get(path)
            for dir in dirs:
                child_path = os.path.join(path, dir)
                child_node = DirNode(
                    name=dir, parent=current_node, real_path=child_path
                )
                path_to_node[child_path] = child_node
            for file in files:
                child_path = os.path.join(path, file)
                child_node = DirNode(
                    name=file, parent=current_node, real_path=child_path
                )
                if child_node.need_content:
                    child_node.content = read_file(child_path)
                path_to_node[child_path] = child_node
        self.root_node = root_node

    @self.event_bus.event("拉取仓库", mode="append")
    def _clone_repo(self):
        remote_path = f"https://github.com/{self.owner}/{self.repo}.git"
        self.data_bus.repo_remote_url = remote_path.replace(".git", "")
        if os.path.exists(self.local_path):
            os.system(f"rm -rf {self.local_path}")
        os.system(
            f"git clone {remote_path} {self.local_path} -q -c http.proxy={BYTEDANCE_HTTP_PROXY}"
        )

    def _summary_dir(self):
        root_node = self.root_node
        depth_map = defaultdict(list)
        for node in LevelOrderIter(root_node):
            depth_map[node.depth].append(node)
        # 层序遍历，从最底层到最高层
        level_nodes = [depth_map[d] for d in sorted(depth_map, reverse=True)]
        for nodes in level_nodes:
            threads = []
            for node in nodes:
                if node.isdir and node.need_summary and node.summary == "":
                    t = threading.Thread(
                        target=self.llm.summary_dir,
                        args=(node,),
                    )
                    threads.append(t)
                    t.start()
            for t in threads:
                t.join()

    def _summary_file(self):
        root_node = self.root_node
        nodes = []
        for node in PostOrderIter(root_node):
            if node.isfile and node.need_summary:
                nodes.append(node)
        self.llm.summary_files(nodes)

    def _summary_repo(self):
        threads = []
        for f in [self._summary_dir, self._summary_file]:
            t = threading.Thread(
                target=f,
                args=(),
            )
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        path_to_summary = {}
        for node in PostOrderIter(self.root_node):
            path_to_summary[node.pure_path] = node.summary
        self.filetree = {k: path_to_summary[k] for k in sorted(path_to_summary)}

    def _summary_cons_and_pros(self):
        threads = []
        for f in [self.llm.summary_cons, self.llm.summary_pros]:
            t = threading.Thread(
                target=f,
                args=(self.filetree,),  # we temporarily use the thinking model here
            )
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def _write_to_data_bus(self):
        _, self.data_bus.readme = next(iter(self.filetree.items()))
        self.data_bus.filetree = self.filetree
        self.data_bus.repo_local_path = self.local_path

    def process(self, owner: str, repo: str, local_path: str = None) -> DirNode:
        self.owner = owner
        self.repo = repo

        if local_path is None:
            self.local_path = os.path.join(TEMPRORY_DIR, self.repo)
            self.event_bus.event = {"content": "拉取仓库", "mode": "append"}
            self._clone_repo()
        else:
            self.local_path = local_path

        self.event_bus.event = {"content": "构建文件系统树", "mode": "append"}
        self._build_filetree()

        self.event_bus.event = {"content": "生成摘要", "mode": "append"}
        self._summary_repo()

        self.event_bus.event = {"content": "生成仓库优缺点分析", "mode": "append"}
        self._summary_cons_and_pros()

        self._write_to_data_bus()
