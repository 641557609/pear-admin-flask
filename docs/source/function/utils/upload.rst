:mod:`upload` -- 文件上传模块
==================================

:mod:`upload` 模块源代码在文件 `applications/common/utils/upload.py` 下，主要用于文件上传，目前主要用于图片上传。

.. module:: upload

函数
---------------

.. function:: get_photo(page, limit)

   分页获取图片列表，并按创建时间降序排列。

   :param page: 当前页码。
   :param limit: 每页显示的图片数量。
   :return: 返回图片列表和图片总数。


.. function:: upload_one(photo, mime)

   上传一张图片，并保存图片信息到数据库。

   :param photo: 图片文件对象。
   :param mime: 图片的 MIME 类型。
   :return: 返回图片的访问 URL。


.. function:: delete_photo_by_id(_id)

   根据图片 ID 删除图片及其记录。

   :param _id: 图片 ID。
   :return: 返回删除操作的结果（数据库中删除的个数，成功非0）。