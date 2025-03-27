构建文档
==================

本章节讲述如何构建文档，构建文档使用到 Python 中的 sphinx 工具，需要使用 Python 进行安装。

安装必要依赖
~~~~~~~~~~~~~~~

文档位置位于 `docs` 文件夹，所以先切换到 `docs` 文件。

.. code-block:: bash

    cd docs
    pip install -r requirements.txt

构建文档
~~~~~~~~~~~~~~~

使用 `sphinx-build .\source .\_build` 进行构建文档。

编辑文档
~~~~~~~~~~~~~~~

如果修改文档，请在 `source` 中修改并重新构建。