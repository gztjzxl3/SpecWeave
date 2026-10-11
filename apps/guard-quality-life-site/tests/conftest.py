"""pytest 公共夹具：隔离数据库路径，避免测试污染仓库 .data。"""

import os

import pytest


@pytest.fixture(autouse=True, scope="session")
def _isolate_db(tmp_path_factory):
    """把 GQLSITE_DB 指向临时文件，使 signals 读写不影响仓库自身数据。"""
    db_file = tmp_path_factory.mktemp("gqlsite") / "test.db"
    os.environ["GQLSITE_DB"] = str(db_file)
    yield
    os.environ.pop("GQLSITE_DB", None)