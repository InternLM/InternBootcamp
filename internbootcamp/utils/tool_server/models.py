#!/usr/bin/env python3
"""
数据模型定义
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


class WorkerRegistrationData(BaseModel):
    """Worker注册数据模型"""
    worker_id: str
    worker_url: str
    tools: List[str]
    host_info: Optional[Dict] = None


class CreateInput(BaseModel):
    """工具创建输入模型"""
    instance_id: Optional[str] = None
    identity: Optional[dict] = None 