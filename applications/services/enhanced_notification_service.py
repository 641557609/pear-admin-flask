from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
from pathlib import Path
from notification_service import NotificationService
from flask import current_app

# 通知服务扩展模块
@dataclass
class NotificationRecord:
    """发送记录数据结构"""
    timestamp: datetime
    channel: str
    file_path: str
    receivers: List[str]
    success_count: int
    failed_receivers: List[str]
    error_message: str = ""
    request_id: str = None
    retry_count: int = 0

class ReceiverValidator:
    """接收人管理增强模块"""
    def __init__(self):
        self.active_user_cache = {}  # 用户状态缓存
        self.cache_expiry = 3600  # 缓存有效期（秒）

    def validate_receivers(self, receiver_ids: List[str]) -> Tuple[List[str], List[str]]:
        """
        验证接收人有效性
        :return: (有效接收人列表, 无效接收人列表)
        """
        if not receiver_ids:
            return [], []

        # 检查缓存
        current_time = datetime.now()
        if self.active_user_cache.get("expiry", current_time) < current_time:
            self._refresh_user_cache()

        valid_users = []
        invalid_users = []

        for user_id in receiver_ids:
            if user_id in self.active_user_cache:
                valid_users.append(user_id)
            else:
                invalid_users.append(user_id)

        return valid_users, invalid_users

    def _refresh_user_cache(self):
        """刷新用户状态缓存"""
        # 这里调用HR系统接口或数据库获取在职用户列表
        # 示例：假设我们有一个获取在职用户的函数
        active_users = self._fetch_active_users_from_hr()
        self.active_user_cache = {
            "users": set(active_users),
            "expiry": datetime.now() + timedelta(seconds=self.cache_expiry)
        }

    def _fetch_active_users_from_hr(self) -> List[str]:
        """从HR系统获取在职用户列表"""
        # 实现实际的接口调用逻辑
        # 返回示例：["1001", "1002", "1003"]
        return []

class NotificationTracker:
    """发送记录追踪模块"""
    def __init__(self):
        self.history = []  # 所有发送记录
        self.stats = defaultdict(int)  # 发送统计

    def add_record(self, record: NotificationRecord):
        """添加发送记录"""
        self.history.append(record)
        self._update_stats(record)

    def get_recent_records(self, limit: int = 100) -> List[NotificationRecord]:
        """获取最近的发送记录"""
        return sorted(
            self.history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]

    def get_failed_records(self) -> List[NotificationRecord]:
        """获取失败的发送记录"""
        return [r for r in self.history if r.failed_receivers]

    def get_channel_stats(self) -> Dict[str, Dict]:
        """获取各渠道发送统计"""
        return {
            channel: {
                "total": self.stats[f"{channel}_total"],
                "success": self.stats[f"{channel}_success"],
                "failed": self.stats[f"{channel}_failed"]
            }
            for channel in set(r.channel for r in self.history)
        }

    def _update_stats(self, record: NotificationRecord):
        """更新统计信息"""
        channel = record.channel
        self.stats[f"{channel}_total"] += 1
        if record.failed_receivers:
            self.stats[f"{channel}_failed"] += 1
        else:
            self.stats[f"{channel}_success"] += 1

class EnhancedNotificationService(NotificationService):
    """增强版通知服务"""
    def __init__(self):
        super().__init__()
        self.validator = ReceiverValidator()
        self.tracker = NotificationTracker()

    def send_report(
        self,
        file_path: Path,
        receivers: List[str],
        channel: str = "dingtalk",
        max_retries: int = 3,
        **kwargs
    ) -> Dict:
        """
        增强版发送接口
        :param file_path: 文件路径
        :param receivers: 接收人列表
        :param channel: 通知渠道
        :param max_retries: 最大重试次数
        """
        # 验证接收人
        valid_receivers, invalid_receivers = self.validator.validate_receivers(receivers)
        if invalid_receivers:
            current_app.logger.warning(f"发现无效接收人: {invalid_receivers}")

        # 初始化记录
        record = NotificationRecord(
            timestamp=datetime.now(),
            channel=channel,
            file_path=str(file_path),
            receivers=valid_receivers,
            success_count=0,
            failed_receivers=[]
        )

        # 带重试的发送
        for attempt in range(max_retries):
            try:
                result = super().send_report(
                    file_path=file_path,
                    receivers=valid_receivers,
                    channel=channel,
                    **kwargs
                )

                # 更新记录
                record.success_count = len(valid_receivers) - len(result["failed_receivers"])
                record.failed_receivers = result["failed_receivers"]
                record.error_message = result["message"]
                record.request_id = result["request_id"]
                record.retry_count = attempt

                # 记录发送结果
                self.tracker.add_record(record)
                return result

            except Exception as e:
                record.error_message = str(e)
                if attempt == max_retries - 1:
                    self.tracker.add_record(record)
                    raise

    def get_send_statistics(self) -> Dict:
        """获取发送统计"""
        return self.tracker.get_channel_stats()

    def get_failed_notifications(self) -> List[Dict]:
        """获取失败记录详情"""
        return [
            {
                "timestamp": r.timestamp.isoformat(),
                "file": r.file_path,
                "channel": r.channel,
                "failed_receivers": r.failed_receivers,
                "error": r.error_message
            }
            for r in self.tracker.get_failed_records()
        ]