import json
import logging
import os
from typing import Any, Optional, Tuple, Dict
from uuid import uuid4
import random

import requests
from internbootcamp.bootcamps.fenics_bootcamp import ips
from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ThermalSimulationTool(BaseTool):
    """
    非线性热传导仿真工具（API 版本）
    通过 HTTP API 调用远程 FEniCS 服务器进行仿真
    """
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)

    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例，初始化状态追踪"""
        if instance_id is None:
            instance_id = str(uuid4())
        
        self._instance_dict[instance_id] = {
            "history": [],
            "call_count": 0,
            "max_calls": 5  # 限制最大调用次数
        }
        return instance_id

    @staticmethod
    def _execute_thermal_simulation(
        flux_left: float, 
        flux_bottom: float, 
        monitor_coords_1: Tuple[float, float],
        monitor_coords_2: Tuple[float, float],
        config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        热仿真逻辑核心封装（通过 API 调用）
        """
        try:
            # 构建 API 请求负载
            payload = {
                "length": float(config["length"]),
                "width": float(config["width"]),
                "kappa_base": float(config["kappa_base"]),
                "alpha": float(config["alpha"]),
                "source_amp": float(config["source_amp"]),
                "flux_left": float(flux_left),
                "flux_bottom": float(flux_bottom),
                "monitor1_x": float(monitor_coords_1[0]),
                "monitor1_y": float(monitor_coords_1[1]),
                "monitor2_x": float(monitor_coords_2[0]),
                "monitor2_y": float(monitor_coords_2[1])
            }
            
            # 调用 API
            response = requests.post(
                f"{random.choice(ips)}/run_thermal_simulation",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=200
            )
            
            if not response.ok:
                return {
                    "status": "error",
                    "message": f"API 返回错误状态码 {response.status_code}"
                }
            
            result = response.json()
            
            if not result.get("success"):
                return {
                    "status": "error",
                    "message": result.get("message", "Unknown error")
                }
            
            return {
                "status": "success",
                "temp_monitor1": float(result["temp_monitor1"]),
                "temp_monitor2": float(result["temp_monitor2"]),
                "max_temp": float(result["max_temp"])
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"API 请求失败: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """
        执行工具调用：解析参数 -> 通过 API 调用仿真 -> 返回结果
        """
        try:
            # 1. 必填参数检查
            required_keys = [
                "length", "width", "kappa_base", "alpha", "source_amp",
                "flux_left", "flux_bottom",
                "monitor1_x", "monitor1_y", "monitor2_x", "monitor2_y"
            ]
            missing_params = [k for k in required_keys if k not in parameters]
            
            if missing_params:
                err_msg = f"错误: 参数缺失 {', '.join(missing_params)}。请确保从任务描述中提取并传入所有参数。"
                return err_msg, -0.1, {"error": "missing_params"}

            # 2. 构建 API 请求负载
            try:
                payload = {
                    "length": float(parameters["length"]),
                    "width": float(parameters["width"]),
                    "kappa_base": float(parameters["kappa_base"]),
                    "alpha": float(parameters["alpha"]),
                    "source_amp": float(parameters["source_amp"]),
                    "flux_left": float(parameters["flux_left"]),
                    "flux_bottom": float(parameters["flux_bottom"]),
                    "monitor1_x": float(parameters["monitor1_x"]),
                    "monitor1_y": float(parameters["monitor1_y"]),
                    "monitor2_x": float(parameters["monitor2_x"]),
                    "monitor2_y": float(parameters["monitor2_y"])
                }
            except ValueError as e:
                return f"错误: 参数类型错误 - {str(e)}", -0.1, {"error": "type_error"}

            # 3. 调用 API
            try:
                response = requests.post(
                    f"{random.choice(ips)}/run_thermal_simulation",
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=200
                )
            except requests.exceptions.RequestException as e:
                return f"API 请求失败: {str(e)}", -0.1, {"error": str(e)}

            if not response.ok:
                return f"API 返回错误状态码 {response.status_code}", -0.1, {"error": str(response.status_code)}

            try:
                result = response.json()
            except ValueError:
                return f"API 返回非 JSON 格式: {response.text}", -0.1, {"error": str(response.text)}

            # 4. 处理 API 响应
            if not result.get("success"):
                err_msg = result.get("message", "Unknown error")
                return f"仿真失败: {err_msg}", -0.5, {"error": err_msg}

            # 5. 状态更新与记录
            self._instance_dict[instance_id]["call_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "inputs": parameters,
                "outputs": result
            })

            # 6. 构建响应
            m1 = (payload["monitor1_x"], payload["monitor1_y"])
            m2 = (payload["monitor2_x"], payload["monitor2_y"])
            
            response_text = (
                f"仿真完成:\n"
                f"- 监测点 A ({m1[0]:.3f}, {m1[1]:.3f}): {result['temp_monitor1']:.2f} K\n"
                f"- 监测点 B ({m2[0]:.3f}, {m2[1]:.3f}): {result['temp_monitor2']:.2f} K\n"
                f"- 全局最高温度: {result['max_temp']:.2f} K\n"
                f"(输入通量: Left={payload['flux_left']}, Bottom={payload['flux_bottom']})"
            )
            
            reward = 0.0
            metrics = {
                "temp_monitor1": result['temp_monitor1'],
                "temp_monitor2": result['temp_monitor2'],
                "max_temp": result['max_temp']
            }

            return response_text, reward, metrics

        except Exception as e:
            logger.error(f"ThermalSimulationTool 执行未捕获异常: {str(e)}")
            return f"系统错误: {str(e)}", -1.0, {"error": str(e)}

