import os

from anytree import Node
from core.config import FS_IGNORE_CHARS, FS_SUPPORTED_SUFFIX


class DirNode(Node):
    """docstring for DirNode."""

    def __init__(self, name: str, real_path: str, parent=None):
        super(DirNode, self).__init__(
            name=name,
            parent=parent,
        )

        self.real_path = real_path
        self.pure_path = "/" + "/".join([p.name for p in self.path])
        self.isdir = os.path.isdir(self.real_path)
        self.isfile = os.path.isfile(self.real_path)

        self.supported_suffix = FS_SUPPORTED_SUFFIX
        self.ignore_chars = FS_IGNORE_CHARS

        self.summary = ""
        self.content = ""
        if self.isdir:
            self.need_summary = self._check_dir_need_summary()
        else:
            self.need_content = self._check_file_need_content()
            self.need_summary = self._check_file_need_summary()

    def _check_file_need_summary(self):
        return self.need_content

    def _check_file_need_content(self):
        if self.pure_path.endswith(tuple(self.supported_suffix)):
            path_without_suffix, _ = os.path.splitext(self.pure_path)
            if any(char in path_without_suffix for char in self.ignore_chars):
                return False
            return True
        return False

    def _check_dir_need_summary(self):
        if any(char in self.pure_path for char in self.ignore_chars):
            return False
        return True
