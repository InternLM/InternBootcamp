"""
基础 FastAPI 工具服务器类
"""
from typing import Any, Optional
from fastapi import FastAPI
import uvicorn


class BaseFastApiToolServer:
    """FastAPI 工具服务器基类"""
    
    def __init__(self, tool: Any, host: str = "0.0.0.0", port: int = 8000):
        """
        初始化服务器
        
        Args:
            tool: 工具实例
            host: 服务器主机地址
            port: 服务器端口
        """
        self.tool = tool
        self.host = host
        self.port = port
        self.app = FastAPI(title="Tool Server")
        self._setup_routes()
    
    def _setup_routes(self):
        """设置路由，由子类实现"""
        raise NotImplementedError("Subclasses must implement _setup_routes()")
    
    def run(self, **kwargs):
        """运行服务器"""
        uvicorn.run(self.app, host=self.host, port=self.port, **kwargs)

