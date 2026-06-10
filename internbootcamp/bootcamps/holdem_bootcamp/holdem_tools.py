import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4
import random

from internbootcamp.src.base_tool import BaseTool
from internbootcamp.src.img2base64 import encode_image_file_to_base64
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

from internbootcamp.bootcamps.holdem_bootcamp import ips

import requests
from PIL import Image
from io import BytesIO
import base64

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class createGameSession(BaseTool):
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
            if "game_id" not in parameters:
                return f"错误: 需要指定 game_id", -0.1, {} 

            PAYLOAD = {"game_id": parameters["game_id"]}
            try:           
                response = requests.post(f"{random.choice(ips)}/createGameSession", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=120)     
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
                "game_id": parameters["game_id"],
                "result": {"text": result["info"], "images": result["init_actions"]}
            })
            
            # 构建响应
            content = [{"type": "text", "text": result["info"]}]
            for image_path in result["init_actions"]:
                base64_image = encode_image_file_to_base64(image_path)
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "game_id": parameters["game_id"],
                "result": {"text": result["info"], "images": result["init_actions"]},
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return content, reward, metrics
            
        except Exception as e:
            logger.error(f"createGameSession执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}


class applyAction(BaseTool):
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
            for para in ["game_id", "pin", "action"]:
                if para not in parameters:
                    missed.append(para)
            if len(missed):
                return f"错误: 参数缺失 {missed}", -0.1, {} 

            PAYLOAD = {
                "game_id": parameters["game_id"],
                "pin": parameters["pin"],
                "action": parameters["action"]
            }
            ip = random.choice(ips)
            try:           
                response = requests.post(f"{ip}/applyAction", 
                                        headers={"Content-Type": "application/json"}, 
                                        json=PAYLOAD, 
                                        timeout=120)     
            except requests.exceptions.RequestException as e:
                return f"Request failed, {e}", -0.1, {"error": str(e)} 

            if not response.ok:
                return f"Server returned status {response.status_code}", -0.1, {"error": str(response.status_code)} 

            try:
                result = response.json()
            except ValueError:
                return f"Response is not json format, {response.text}", -0.1, {"error": str(response.text)} 

            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "game_id": parameters["game_id"],
                "result": {"text": result["message"], "images": result["obs"]}
            })
            
            # 构建响应
            content = [{"type": "text", "text": result["message"]}]
            for image_path in result["obs"]:
                with open(image_path, 'rb') as image_file:
                    image_data = image_file.read()
                base64_image = base64.b64encode(image_data).decode('utf-8')
                content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}})
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "game_id": parameters["game_id"],
                "result": {"text": result["message"], "images": result["obs"]},
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return content, reward, metrics
            
        except Exception as e:
            logger.error(f"applyAction执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}
