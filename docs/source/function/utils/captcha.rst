:mod:`captcha` -- 验证码生成模块
==================================

:mod:`captcha` 模块源代码在文件 `applications/common/utils/captcha.py` 下，主要用于生成验证码图片。

.. module:: captcha

类
------

.. class:: vieCode

    生成验证码图片。

    .. py:attribute:: __fontSize
        :type: int

        字体大小，默认为 20。

    .. py:attribute:: __width
        :type: int

        画布宽度，默认为 120。

    .. py:attribute:: __heigth
        :type: int

        画布高度，默认为 45。

    .. py:attribute:: __length
        :type: int

        验证码长度，默认为 4。

    .. py:attribute:: __draw
        :type: ImageDraw.Draw

        画布对象。

    .. py:attribute:: __img
        :type: Image.Image

        图片对象。

    .. py:attribute:: __code
        :type: list

        验证码字符。

    .. py:attribute:: __str
        :type: str

        自定义验证码字符集。

    .. py:attribute:: __inCurve
        :type: bool

        是否绘制干扰曲线，默认为 True。

    .. py:attribute:: __inNoise
        :type: bool

        是否绘制干扰点，默认为 True。

    .. py:attribute:: __type
        :type: int

        验证码类型：1-纯字母，2-数字字母混合，默认为 2。

    .. py:attribute:: __fontPatn
        :type: str

        字体路径，默认为 ``applications/common/utils/fonts/captcha.ttf``。

    .. method:: GetCodeImage(size=80, length=4)

        生成验证码图片及其对应的验证码字符。

        :param size: 验证码字体大小，默认为 80。
        :param length: 验证码字符长度，默认为 4。
        :return: 返回验证码图片对象和验证码字符。

        **示例：**

        .. code-block:: python

            vc = vieCode()
            img, code = vc.GetCodeImage(size=60, length=6)
            img.show()  # 显示验证码图片
            print("验证码:", code)  # 输出验证码字符

    .. method:: __cerateFilter()

        对验证码图片进行模糊处理，增加识别难度。

    .. method:: __createCode()

        生成验证码字符。

    .. method:: __createImage()

        创建画布并设置背景颜色。

    .. method:: __createNoise()

        在验证码图片上绘制干扰点。

    .. method:: __createCurve()

        在验证码图片上绘制干扰曲线。

    .. method:: __printString()

        在画布上打印验证码字符。