# 消息发送逻辑
import base64
from typing import Dict, List
import requests
from pathlib import Path
from flask import current_app
from applications.config import BaseConfig

class NotificationProvider:
    """通知服务抽象基类"""

    def send_file(self, file_path: Path, receivers: List[str], **kwargs) -> Dict:
        """
        发送文件基础接口
        :param file_path: 文件路径对象
        :param receivers: 接收人ID列表
        :return: 发送结果字典
        """
        raise NotImplementedError

    def send_message(self, content: str, receivers: List[str], **kwargs) -> Dict:
        """发送消息抽象方法（预留）"""
        raise NotImplementedError

class TeenrunERPProvider(NotificationProvider):
    """添润ERP接口实现"""

    def __init__(self):
        """获取添润接口url"""
        self.base_url = BaseConfig.TEENRUN_API_URL
    def _prepare_file_data(self, file_path: Path) -> str:
        """准备文件数据（包含格式验证,编码处理）"""
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB限制
            raise ValueError("文件大小超过限制")

        with file_path.open('rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def _validate_receivers(self, receivers: List[str]):
        """验证接收人格式"""
        # 可根据实际需求扩展验证逻辑
        if not receivers:
            raise ValueError("接收人列表不能为空")
        if not all(r for r in receivers):
            raise ValueError("无效的接收人编号格式")


    def send_file(self, file_path: Path, receivers: List[str], **kwargs) -> Dict:
        """
        发送文件核心实现
        :return: {
            "success": bool,
            "message": str,
            "failed_receivers": List[str],
            "request_id": Optional[str]
        }
        """
        result_template = {
            "success": False,
            "message": "",
            "failed_receivers": [],
            "success_receivers": []
        }

        try:
            # 验证接收人格式
            self._validate_receivers(receivers)
            # 准备文件数据
            file_data = self._prepare_file_data(file_path)
            # 构建请求参数
            payload = {
                "fileName": file_path.name,
                "streamfileData": file_data,
                "jobNumbers": ",".join(receivers)
            }

            # 发送请求
            try:
                response = requests.post(
                    f"{self.base_url}/dingtalkservice.asmx/SendFileByte",
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                response.raise_for_status()
                result_template.update(self._parse_response(response.json()))
                result_template["success_receivers"] = [r for r in receivers ]
            except requests.exceptions.RequestException as e:
                raise ServiceUnavailableError(f"服务不可用: {str(e)}")

        except Exception as e:
            result_template.update({
                "message": str(e),
                "failed_receivers": receivers.copy()
            })
        return result_template

    def _parse_response(self, response_data: Dict) -> Dict:
        """解析ERP接口响应"""
        # 示例解析逻辑，需根据实际接口响应调整
        print(response_data)

        if "d" not in response_data:
            raise InvalidResponseError("无效的接口响应格式")

        return {
            "success": "成功" in response_data["d"] or "推送完成" in response_data["d"],
            "message": response_data["d"],
        }


class ThirdPartyDingTalkProvider(NotificationProvider):
    """第三方钉钉服务实现"""
    pass



class NotificationService:
    """统一通知服务入口"""

    def __init__(self):
        self.providers = {
            "dingtalk": ThirdPartyDingTalkProvider(),
            "teenrun": TeenrunERPProvider(),
            # 后续可扩展其他渠道
        }

    def send_report(
            self,
            file_path: Path,
            receivers: List[str],
            channel: str,
            **kwargs
    ) -> Dict:
        """
        发送报表文件统一接口
        :param file_path: 文件路径
        :param receivers: 接收人列表
        :param channel: 通知渠道
        """
        provider = self.providers.get(channel)
        if not provider:
            raise ValueError(f"不支持的通知渠道: {channel}")

        return provider.send_file(file_path, receivers, **kwargs)

    # 后续扩展方法
    # def send_message(self, content, receivers, channel="dingtalk"):


class ServiceUnavailableError(Exception):
    """自定义服务异常"""
    pass


class InvalidResponseError(Exception):
    """响应格式异常"""
    pass

