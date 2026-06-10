import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4
import random

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

from internbootcamp.bootcamps.bot_bootcamp import ips

import requests

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class createSession(BaseTool):
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "history": [],
            "operation_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        try:
            if "case_id" not in parameters:
                return f"错误: 需要指定 case_id", -0.1, {} 

            PAYLOAD = {
                "case_id": parameters["case_id"] 
                }
            try:           
                response = requests.post(f"{random.choice(ips)}/create_session", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=200)     
            except requests.exceptions.RequestException as e:
                return f"Request failed, {e}", -0.1, {"error": str(e)} 

            if not response.ok:
                return f"Server returned status {response.status_code}", -0.1, {"error": str(response.status_code)} 

            try:
                result = response.json()
            except ValueError:
                return f"Response is not json format, {response.text}", -0.1, {"error": str(response.text)} 

            if not result["success"]:
                return result["info"], -0.1, {}

            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "case_id": parameters["case_id"],
                "result": result["info"]
            })
            
            # 构建响应
            response = result["info"]
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "case_id": parameters["case_id"],
                "result": result["info"],
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"createSession执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}


class CheckCollision(BaseTool):
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "history": [],
            "operation_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        try:
            missed = []
            for para in ["case_id", "pin", "joint_angles"]:
                if para not in parameters:
                    missed.append(para)
            if len(missed):
                return f"错误: 参数缺失 {missed}", -0.1, {} 

            PAYLOAD = {
                "case_id": parameters["case_id"],
                "pin": parameters["pin"],
                "joint_angles": parameters["joint_angles"]
                }
            try:           
                response = requests.post(f"{random.choice(ips)}/check_collision", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=200)     
            except requests.exceptions.RequestException as e:
                return f"Request failed, {e}", -0.1, {"error": str(e)} 

            if not response.ok:
                return f"Server returned status {response.status_code}", -0.1, {"error": str(response.status_code)} 

            try:
                result = response.json()
            except ValueError:
                return f"Response is not json format, {response.text}", -0.1, {"error": str(response.text)} 

            if result["success"]:
                response = "{}发生碰撞，当前机械臂末端坐标为：{}".format("" if result["is_collision"] else "未", result["coord"])
            else:
                response = result["feedback"]

            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "case_id": parameters["case_id"],
                "pin": parameters["pin"],
                "joint_angles": parameters["joint_angles"],
                "result": response
            })
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "case_id": parameters["case_id"],
                "pin": parameters["pin"],
                "joint_angles": parameters["joint_angles"],
                "result": response,
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"CheckCollision执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}
