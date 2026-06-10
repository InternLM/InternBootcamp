import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4
import random

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

import numpy as np

from internbootcamp.bootcamps.flangeplane_bootcamp import ips
from internbootcamp.bootcamps.flangeplane_bootcamp.utils.cost_cal import cost_analysis

import requests

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CaeAnalysis(BaseTool):
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
            for para in ["D", "B1", "L", "BoltCenterRadius", "thickness", "bolt_count_edit", "Name", "YoungsModulus", "PoissonRatio", "Density", "pressure"]:
                if para not in parameters:
                    missed.append(para)
            if len(missed):
                return f"错误: 参数缺失 {missed}", -0.1, {} 

            PAYLOAD = {
                    "D": parameters["D"], 
                    "B1": parameters["B1"], 
                    "L": parameters["L"], 
                    "BoltCenterRadius": parameters["BoltCenterRadius"], 
                    "thickness": parameters["thickness"], 
                    "bolt_count_edit": parameters["bolt_count_edit"], 
                    "Name": parameters["Name"], 
                    "YoungsModulus": parameters["YoungsModulus"], 
                    "PoissonRatio": parameters["PoissonRatio"], 
                    "Density": parameters["Density"], 
                    "pressure": parameters["pressure"]
                    }
            try:           
                response = requests.post(f"{random.choice(ips)}/cae_analysis", 
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
                "D": parameters["D"], 
                "B1": parameters["B1"], 
                "L": parameters["L"], 
                "BoltCenterRadius": parameters["BoltCenterRadius"], 
                "thickness": parameters["thickness"], 
                "bolt_count_edit": parameters["bolt_count_edit"], 
                "Name": parameters["Name"], 
                "YoungsModulus": parameters["YoungsModulus"], 
                "PoissonRatio": parameters["PoissonRatio"], 
                "Density": parameters["Density"], 
                "pressure": parameters["pressure"],
                "result": result["disp_max"]
            })
            
            # 构建响应
            response = "最大节点位移模: {}".format(result["disp_max"])
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "D": parameters["D"], 
                "B1": parameters["B1"], 
                "L": parameters["L"], 
                "BoltCenterRadius": parameters["BoltCenterRadius"], 
                "thickness": parameters["thickness"], 
                "bolt_count_edit": parameters["bolt_count_edit"], 
                "Name": parameters["Name"], 
                "YoungsModulus": parameters["YoungsModulus"], 
                "PoissonRatio": parameters["PoissonRatio"], 
                "Density": parameters["Density"], 
                "pressure": parameters["pressure"],
                "result": result["disp_max"],
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"CaeAnalysis执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}


class CostCal(BaseTool):
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
            for para in ["thickness", "D", "B1", "bolt_count_edit", "L", "Density", "price"]:
                if para not in parameters:
                    missed.append(para)
            if len(missed):
                return f"错误: 参数缺失 {missed}", -0.1, {} 

            cost = cost_analysis(parameters["thickness"], parameters["D"], parameters["B1"], parameters["bolt_count_edit"], parameters["L"], parameters["Density"], parameters["price"])
            
            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "thickness": parameters["thickness"], 
                "D": parameters["D"], 
                "B1": parameters["B1"], 
                "bolt_count_edit": parameters["bolt_count_edit"], 
                "L": parameters["L"], 
                "Density": parameters["Density"], 
                "price": parameters["price"],
                "result": cost
            })
            
            # 构建响应
            response = "总成本: {}".format(cost)
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "thickness": parameters["thickness"], 
                "D": parameters["D"], 
                "B1": parameters["B1"], 
                "bolt_count_edit": parameters["bolt_count_edit"], 
                "L": parameters["L"], 
                "Density": parameters["Density"], 
                "price": parameters["price"],
                "result": cost,
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"CostCal执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}
