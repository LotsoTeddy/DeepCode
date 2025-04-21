import os
from string import Template

from core.bus.DataBus import DataBus
from core.config import TEMPRORY_DIR
from core.event import event
from core.utils import get_time


class MdProcessor(object):
    """docstring for MdProcessor."""

    def __init__(self, data_bus: DataBus, event_bus):
        self.data_bus = data_bus
        self.event_bus = event_bus

        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "templates", "document.md"
        )

        self.dump_path = ""

    def _build_filetree(self, path_dict: dict):
        tree = {}
        for path in path_dict:
            parts = [p for p in path.split("/") if p]
            node = tree
            for part in parts:
                if part not in node:
                    node[part] = {}
                node = node[part]

        def build_md(node, current_path="", depth=0):
            md = ""
            for name, children in sorted(node.items()):
                full_path = f"{current_path}/{name}" if current_path else f"/{name}"

                desc = ""
                if depth > 0:
                    desc = path_dict.get(full_path, "")
                    desc = f" {desc}" if desc else ""

                indent = "    " * (depth - 1) if depth > 0 else ""
                bullet = "-" if depth == 0 else "    -"
                desc = desc.replace("\n", "")
                md += f"{indent}{bullet} `{name}`{desc}\n"

                if children:
                    md += build_md(children, full_path, depth + 1)
            return md

        return build_md(tree)

    def _build_md_string(self, params: dict = None):
        with open(self.template_path, "r") as f:
            template = Template(f.read())
        return template.safe_substitute(params)

    def _dump_md_file(self, md_string: str):
        if os.path.exists(self.dump_path):
            os.remove(self.dump_path)

        with open(self.dump_path, "a", encoding="utf-8") as f:
            f.write(md_string)

        self.data_bus.md_local_path = self.dump_path

    @event("构建Markdown文件")
    def process(self):
        self.dump_path = f"{TEMPRORY_DIR}/{self.data_bus.owner}_{self.data_bus.repo}.md"

        self.data_bus.filetree = self._build_filetree(self.data_bus.filetree)
        self.data_bus.end_time = get_time()
        md_string = self._build_md_string(self.data_bus.dump())

        self._dump_md_file(md_string)
        return self.dump_path
