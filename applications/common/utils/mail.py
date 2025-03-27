"""
集成了对 Pear Admin Flask 二次开发的邮件操作模块，并提供了相应的示例。
"""
from flask import current_app
from flask_mail import Message

from applications.common.curd import model_to_dicts
from applications.common.helper import ModelFilter
from applications.extensions import db, flask_mail
from applications.models import Mail
from applications.schemas import MailOutSchema


def get_all(receiver=None, subject=None, content=None):
    """
    获取邮件列表，支持根据接收者、主题和内容进行筛选。

    返回的列表中的字典结构如下::

        {
            "content": "",  # HTML 内容
            "create_at": "2022-12-25T10:51:17",  # 创建时间
            "id": 17,  # 邮件ID
            "realname": "超级管理",  # 创建者姓名
            "receiver": "",  # 接收者
            "subject": ""  # 邮件主题
        }

    :param receiver: 接收者邮箱地址，支持模糊查询。
    :param subject: 邮件主题，支持模糊查询。
    :param content: 邮件内容，支持模糊查询。
    :return: 返回符合条件的邮件列表。
    """
    # 构造查询条件
    mf = ModelFilter()
    if receiver:
        mf.contains(field_name="receiver", value=receiver)
    if subject:
        mf.contains(field_name="subject", value=subject)
    if content:
        mf.exact(field_name="content", value=content)

    # 查询邮件数据并分页
    mail = Mail.query.filter(mf.get_filter(Mail)).layui_paginate()
    return model_to_dicts(schema=MailOutSchema, data=mail.items)


def add(receiver, subject, content, user_id):
    """
    发送一封邮件，并将发送记录保存到数据库。 **该方法被邮件发送的视图函数调用。**

    :param receiver: 接收者邮箱地址，多个邮箱用英文分号隔开。
    :param subject: 邮件主题。
    :param content: 邮件内容（HTML 格式）。
    :param user_id: 发送者用户ID，表示谁发送了这封邮件。
                   可以使用 `from flask_login import current_user; current_user.id` 获取当前登录用户的ID。
    :return: 发送成功返回 True，失败报错。
    """
    send_mail(subject=subject, recipients=receiver.split(";"), content=content)

    # 保存邮件记录到数据库
    mail = Mail(receiver=receiver, subject=subject, content=content, user_id=user_id)
    db.session.add(mail)
    db.session.commit()
    return True


def delete(id):
    """
    删除指定的邮件记录。

    :param id: 邮件ID。
    :return: 删除成功返回 True，失败返回 False。
    """
    res = Mail.query.filter_by(id=id).delete()
    if not res:
        return False
    db.session.commit()
    return True


def send_mail(subject, recipients, content):
    """
    发送邮件（不记录发送日志）。

    注意：如果发送失败会抛出异常，请使用 try-except 进行捕获。

    :param subject: 邮件主题。
    :param recipients: 接收者邮箱地址，多个邮箱用英文分号隔开。
    :param content: 邮件内容（HTML 格式）。
    """
    message = Message(subject=subject, recipients=recipients, html=content)
    flask_mail.send(message)
