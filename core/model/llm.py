from typing import Dict, List

import litellm
from litellm import batch_completion

from core.bus.DataBus import DataBus
from core.config.config import (
    LLM_API_BASE,
    LLM_API_KEY,
    LLM_FALLBACK_MODELS,
    LLM_MODEL,
    LLM_PREFIX,
)
from core.fs.DirNode import DirNode
from core.model.prompts import *


class LLM:
    def __init__(self, data_bus: DataBus, event_bus):
        self.data_bus = data_bus
        self.event_bus = event_bus

        # we set this to avoid supporter checking
        litellm.suppress_debug_info = True
        litellm.logging = False

        # LLM-related configurations
        litellm.api_base = LLM_API_BASE
        litellm.api_key = LLM_API_KEY

    def _build_summary_dir_message(self, node: DirNode):
        repo = self.data_bus.repo
        system_prompt = DIR_PROCESS_SYS_PROMPT.format(repo=repo, dirpath=node.pure_path)

        user_prompt = ""
        for sub_node in list(node.children):
            if sub_node.isdir:
                user_prompt += SUB_DIR_SUMMARY.format(
                    dirname=sub_node.name, smmary=sub_node.summary
                )
        for sub_node in list(node.children):
            if sub_node.isfile:
                user_prompt += SINGLE_FILE.format(
                    filename=sub_node.name.split("/")[-1],
                    filepath=sub_node.pure_path,
                    content=sub_node.content,
                )

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        return messages

    def _build_summary_files_message(self, nodes: List[DirNode]):
        messages = []

        for node in nodes:
            file = SINGLE_FILE.format(
                filename=node.name,
                filepath=node.pure_path,
                content=node.content,
            )
            message = [
                {
                    "role": "system",
                    "content": FILE_PROCESS_SYS_PROMPT.format(repo=self.data_bus.repo),
                },
                {
                    "role": "user",
                    "content": file,
                },
            ]
            messages.append(message)

        return messages

    def _completion(self, messages: List[dict], model: str = "") -> str:
        response = litellm.completion(
            model=LLM_PREFIX + LLM_MODEL if model == "" else LLM_PREFIX + model,
            messages=messages,
            api_key=LLM_API_KEY,
            api_base=LLM_API_BASE,
            fallbacks=[LLM_PREFIX + m for m in LLM_FALLBACK_MODELS],
            num_retries=60,  # for avoid TPM
            max_retries=60,
        )
        return response.choices[0].message.content

    def _batch_completion(self, messages: List[dict]) -> List[str]:
        responses = batch_completion(
            model=LLM_PREFIX + LLM_MODEL,
            messages=messages,
            api_key=LLM_API_KEY,
            api_base=LLM_API_BASE,
            fallbacks=[LLM_PREFIX + m for m in LLM_FALLBACK_MODELS],
            num_retries=60,
            max_retries=60,
        )

        return [response.choices[0].message.content for response in responses]

    def summary_cons(self, path_to_summary: Dict[str, str], model: str = ""):
        messages = [
            {"role": "system", "content": SUMMARY_CONS.format(repo=self.data_bus.repo)},
            {
                "role": "user",
                "content": str(path_to_summary).replace("'", '"'),
            },
        ]

        self.data_bus.cons = self._completion(messages, model)

    def summary_pros(self, path_to_summary: Dict[str, str], model: str = ""):
        messages = [
            {"role": "system", "content": SUMMARY_PROS.format(repo=self.data_bus.repo)},
            {
                "role": "user",
                "content": str(path_to_summary).replace("'", '"'),
            },
        ]

        self.data_bus.pros = self._completion(messages, model)

    def summary_dir(self, node: DirNode) -> str:
        messages = self._build_summary_dir_message(node)
        node.summary = self._completion(messages)

    def summary_files(self, nodes: List[DirNode]):
        messages = self._build_summary_files_message(nodes)
        responses = self._batch_completion(messages)
        for node in nodes:
            node.summary = responses[nodes.index(node)]
