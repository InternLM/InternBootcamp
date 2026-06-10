import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4
import random

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

from internbootcamp.bootcamps.mole_bootcamp import ips

import requests

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CreateSession(BaseTool):
    """创建会话工具"""
    
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
            if "env_id" not in parameters:
                return f"错误: 需要指定 env_id", -0.1, {} 

            PAYLOAD = {
                "env_id": parameters["env_id"] 
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
                "env_id": parameters["env_id"],
                "result": result["info"]
            })
            
            # 构建响应
            response_text = result["info"]
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "env_id": parameters["env_id"],
                "result": result["info"],
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response_text, reward, metrics
            
        except Exception as e:
            logger.error(f"CreateSession执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}


class MeasurePoint(BaseTool):
    """测量点工具"""
    
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
            for para in ["env_id", "pin", "x", "y"]:
                if para not in parameters:
                    missed.append(para)
            if len(missed):
                return f"错误: 参数缺失 {missed}", -0.1, {} 

            PAYLOAD = {
                "env_id": parameters["env_id"],
                "pin": parameters["pin"],
                "x": parameters["x"],
                "y": parameters["y"]
            }
            
            try:           
                response = requests.post(f"{random.choice(ips)}/measure_point", 
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
                response_text = f"测量完成。坐标: {result['coord']}, 能量: {result['energy']} kJ/mol, 受力: {result['force_vector']}"
            else:
                response_text = result["feedback"]

            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "env_id": parameters["env_id"],
                "pin": parameters["pin"],
                "x": parameters["x"],
                "y": parameters["y"],
                "result": response_text
            })
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "env_id": parameters["env_id"],
                "pin": parameters["pin"],
                "x": parameters["x"],
                "y": parameters["y"],
                "result": response_text,
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response_text, reward, metrics
            
        except Exception as e:
            logger.error(f"MeasurePoint执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}


class RunLocalMinimization(BaseTool):
    """局部优化工具"""
    
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
            for para in ["env_id", "pin", "start_x", "start_y"]:
                if para not in parameters:
                    missed.append(para)
            if len(missed):
                return f"错误: 参数缺失 {missed}", -0.1, {} 

            PAYLOAD = {
                "env_id": parameters["env_id"],
                "pin": parameters["pin"],
                "start_x": parameters["start_x"],
                "start_y": parameters["start_y"]
            }
            
            try:           
                response = requests.post(f"{random.choice(ips)}/run_local_minimization", 
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
                response_text = f"局部优化完成。起点: {result['start']}, 终点: {result['final_coords']}, 最终能量: {result['final_energy']} kJ/mol"
            else:
                response_text = result["feedback"]

            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "env_id": parameters["env_id"],
                "pin": parameters["pin"],
                "start_x": parameters["start_x"],
                "start_y": parameters["start_y"],
                "result": response_text
            })
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "env_id": parameters["env_id"],
                "pin": parameters["pin"],
                "start_x": parameters["start_x"],
                "start_y": parameters["start_y"],
                "result": response_text,
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response_text, reward, metrics
            
        except Exception as e:
            logger.error(f"RunLocalMinimization执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}
