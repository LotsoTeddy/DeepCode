class DataBus(object):
    """docstring for DataBus."""

    def __init__(self):
        # ====== repo medadata ======
        self.repo = ""
        self.owner = ""
        self.branch = "default: main"
        self.repo_remote_url = ""

        self.total_num_dirs = 0
        self.total_num_files = 0
        self.total_num_summary_dirs = 0
        self.total_num_summary_files = 0

        self.model = ""

        # ====== document content ======
        self.start_time = ""
        self.end_time = ""

        self.readme = ""
        self.filetree = None
        self.pros = ""
        self.cons = ""

        # ====== local paths ======
        # we record these for cleaning
        self.repo_local_path = ""
        self.md_local_path = ""

    def dump(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if not k.startswith("__")}
