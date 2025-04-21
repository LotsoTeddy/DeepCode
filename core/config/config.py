import os

from dotenv import load_dotenv

load_dotenv()

# temporary directory for storing temporary github repositories and markdown file
TEMPRORY_DIR = "/tmp/"

# file-system filter
FS_SUPPORTED_SUFFIX = [".py", ".md", ".json", ".js", ".tsx", ".ts", ".java"]
FS_IGNORE_CHARS = [".", "__", "test"]

# bytedance http proxy from VIP service
BYTEDANCE_HTTP_PROXY = "http://100.64.120.176:3128"

# LLM-related configurations
LLM_API_BASE = "https://ark.cn-beijing.volces.com/api/v3/"
LLM_API_KEY = os.getenv("LLM_API_KEY")

LLM_PREFIX = "openai/"  # the `openai/` is necessary required by Litellm
LLM_MODEL = "doubao-1-5-pro-256k-250115"
LLM_FALLBACK_MODELS = [
    "doubao-1-5-pro-32k-250115",
    "deepseek-v3-250324",
    "doubao-1-5-thinking-pro-250415",
    "deepseek-r1-250120",
    "doubao-pro-32k-241215",
    "doubao-lite-32k-240828",
]

# Lark API related configurations
LARK_APP_ID = os.getenv("LARK_APP_ID")
LARK_APP_SECRET = os.getenv("LARK_APP_SECRET")
LARK_CLOUD_FOLDER_ID = os.getenv("LARK_CLOUD_FOLDER_ID")
