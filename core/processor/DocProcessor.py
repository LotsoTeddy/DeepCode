import json
import os

import lark_oapi as lark
import requests
from core.bus.DataBus import DataBus
from core.config.config import LARK_APP_ID, LARK_APP_SECRET, LARK_CLOUD_FOLDER_ID
from core.event import event
from lark_oapi.api.docx.v1 import *
from lark_oapi.api.drive.v1 import *
from lark_oapi.api.im.v1 import *
from requests_toolbelt import MultipartEncoder


class DocProcessor(object):
    """DocProcessor responses the interaction of lark cloud document."""

    def __init__(self, data_bus: DataBus, event_bus):
        self.data_bus = data_bus
        self.event_bus = event_bus

        self.lark_client = (
            lark.Client.builder()
            .app_id(LARK_APP_ID)
            .app_secret(LARK_APP_SECRET)
            .build()
        )

    def _get_u_id(self):
        data = {
            "app_id": LARK_APP_ID,
            "app_secret": LARK_APP_SECRET,
        }
        url = (
            "https://open.larkoffice.com/open-apis/auth/v3/tenant_access_token/internal"
        )
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if result.get("code") == 0:
                return result.get("tenant_access_token")
            else:
                print(f"Error: {result.get('msg')}")
                return None
        else:
            print(f"Request failed with status code: {response.status_code}")
            return None

    @event("上传至飞书云空间")
    def _upload_to_lark(self, local_path: str):
        file_size = os.path.getsize(local_path)

        url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        form = {
            "file_name": local_path,
            "parent_type": "explorer",
            "parent_node": LARK_CLOUD_FOLDER_ID,
            "size": str(file_size),
            "file": (open(local_path, "rb")),
        }
        multi_form = MultipartEncoder(form)
        headers = {
            "Authorization": f"Bearer {self._get_u_id()}",
        }
        headers["Content-Type"] = multi_form.content_type

        response = requests.request("POST", url, headers=headers, data=multi_form)
        return response.json().get("data").get("file_token")

    @event("转化为飞书文档")
    def _convert_to_lark_doc(self, file_token: str, filename: str):
        request: CreateImportTaskRequest = (
            CreateImportTaskRequest.builder()
            .request_body(
                ImportTask.builder()
                .file_extension("md")
                .file_token(file_token)
                .type("docx")
                .file_name(filename)
                .point(
                    ImportTaskMountPoint.builder()
                    .mount_type(1)
                    .mount_key(LARK_CLOUD_FOLDER_ID)
                    .build()
                )
                .build()
            )
            .build()
        )

        response: CreateImportTaskResponse = (
            self.lark_client.drive.v1.import_task.create(request)
        )
        if not response.success():
            lark.logger.error(
                f"client.drive.v1.import_task.create failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
            )
            return
        return response.data.ticket

    @event("转化状态查询")
    def _check_convert_status(self, ticket: str):
        while True:
            request: GetImportTaskRequest = (
                GetImportTaskRequest.builder().ticket(ticket).build()
            )

            # 发起请求
            response: GetImportTaskResponse = self.lark_client.drive.v1.import_task.get(
                request
            )

            if not response.success():
                lark.logger.error(
                    f"client.drive.v1.import_task.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
                )
                break

            if response.data.result.job_status == 0:
                return response.data.result.token

    def process(self, local_path: str):
        """Process the local file and upload it to lark cloud.

        Args:
            local_path (str): The local Markdown file path.
        Returns:
            str: The lark cloud file id.
        """
        file_token = self._upload_to_lark(local_path=local_path)

        ticket = self._convert_to_lark_doc(
            file_token=file_token,
            filename=f"{self.data_bus.owner}/{self.data_bus.repo}分析文档",
        )

        lark_file_id = self._check_convert_status(ticket=ticket)
        return lark_file_id
