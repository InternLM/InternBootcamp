import json
import logging
import os
from typing import Any, Optional, Tuple, Dict
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.battery_bootcamp.battery_utils import execute_pybamm_logic

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))

class BatterySimulationTool(BaseTool):
    """
    锂离子电池电化学仿真工具。
    基于 PyBaMM 框架，计算特定正极参数下的电池比能量、温度和放电时间。
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
            "max_calls": 5  # 限制最大调用次数，模拟昂贵的仿真成本
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """
        执行工具调用：解析参数 -> 运行仿真 -> 返回结果
        """
        try:
            # 1. 必填参数检查
            required_keys = [
                "pos_thickness", "pos_porosity", 
                "c_rate", "ambient_temp", "heat_transfer_coeff", "chemistry"
            ]
            missing_params = [k for k in required_keys if k not in parameters]
            
            if missing_params:
                err_msg = f"错误: 参数缺失 {', '.join(missing_params)}。请确保从任务描述中提取并传入所有环境参数。"
                return err_msg, -0.1, {"error": "missing_params"}

            # 2. 构建仿真上下文
            # 注意：必须进行类型转换，防止 JSON 序列化 numpy 类型失败
            try:
                sim_context = {
                    "chemistry": str(parameters["chemistry"]),
                    "c_rate": str(parameters["c_rate"]),
                    "ambient_temp": float(parameters["ambient_temp"]),
                    "initial_temp": float(parameters["ambient_temp"]), # 假设初始温度等于环境温度
                    "heat_transfer_coeff": float(parameters["heat_transfer_coeff"])
                }
                pos_thickness = float(parameters["pos_thickness"])
                pos_porosity = float(parameters["pos_porosity"])
            except ValueError as e:
                return f"错误: 参数类型错误 - {str(e)}", -0.1, {"error": "type_error"}

            # 3. 执行仿真核心逻辑
            #  - 概念上这里调用底层的物理求解器
            result_dict = execute_pybamm_logic(pos_thickness, pos_porosity, sim_context)

            # 4. 状态更新与记录
            self._instance_dict[instance_id]["call_count"] += 1
            self._instance_dict[instance_id]["history"].append({
                "inputs": parameters,
                "outputs": result_dict
            })

            # 5. 构建响应
            if result_dict["status"] == "success":
                # 格式化成功的输出，保留关键指标供模型决策
                response = json.dumps(result_dict, ensure_ascii=False)
                # 仿真成功给予微小的正反馈，或者是0 (主要奖励由最终结果决定)
                reward = 0.0 
                metrics = result_dict
            else:
                # 仿真失败（如参数不合理导致求解器崩溃）
                response = json.dumps(result_dict, ensure_ascii=False)
                reward = -0.5 # 给予一定惩罚，让模型学会避开物理上不可行的参数区域
                metrics = {"error": result_dict.get("message")}

            return response, reward, metrics

        except Exception as e:
            logger.error(f"BatterySimulationTool 执行未捕获异常: {str(e)}")
            return f"系统错误: {str(e)}", -1.0, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """
        计算工具层面的奖励。
        这里主要用于约束工具的使用成本（仿真很慢，不应滥用）。
        """
        if instance_id not in self._instance_dict:
            return 0.0
        
        instance = self._instance_dict[instance_id]
        call_count = instance["call_count"]
        max_calls = instance["max_calls"]

        # 逻辑：基础分 1.0
        # 每调用一次扣除 0.1 分 (鼓励少次尝试)
        # 如果超过最大次数，大幅扣分
        
        cost_per_call = 0.1
        reward = 1.0 - (call_count * cost_per_call)
        
        if call_count > max_calls:
            reward -= 10.0 # 强惩罚，表示任务失败
            
        return max(reward, -1.0) # 设定下限