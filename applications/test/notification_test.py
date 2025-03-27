from ..services.notification_service import NotificationService
import unittest
from pathlib import Path

class TestNotificationService(unittest.TestCase):
    def test_init(self, path):
        notification_service = NotificationService()

        result = notification_service.send_report(
            file_path=Path(path),
            receivers=["WIN3678"],
            channel="teenrun"
        )

        if result["success"]:
            print(f"发送成功，请求ID: {result['request_id']}")
        else:
            print(f"发送失败: {result['message']}")
            if result["failed_receivers"]:
                print(f"需重新发送的接收人: {result['failed_receivers']}")