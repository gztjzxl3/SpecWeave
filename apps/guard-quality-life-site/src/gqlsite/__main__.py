"""支持 ``python -m gqlsite`` 直接启动 uvicorn 开发服务器。"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("gqlsite.main:app", host="127.0.0.1", port=8000, reload=True)