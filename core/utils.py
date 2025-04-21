from datetime import datetime


def get_time():
    now = datetime.now()
    return f"{now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"


def get_thread_id():
    import threading

    return str(threading.current_thread().ident)


def read_file(abs_path: str):
    with open(abs_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


def extract_repo_metadata(repo_url: str):
    url = repo_url.split("/")
    for u in url:
        if "github.com" in u:
            owner = url[url.index(u) + 1]
            repo = url[url.index(u) + 2]
            return owner, repo
    raise ValueError("Invalid repo URL format. Please provide a valid GitHub URL.")
