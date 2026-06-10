import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ArithmeticTool(BaseTool):
    """一个简单的算术工具，支持基本的加减乘除运算"""
    
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
        if instance_id not in self._instance_dict:
            self._instance_dict[instance_id] = {
                "history": [],
                "operation_count": 0
            }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行算术运算"""
        try:
            operation = parameters.get("operation", "")
            operand1 = parameters.get("operand1", 0)
            operand2 = parameters.get("operand2", 0)
            
            # 验证参数
            if not operation:
                return "错误: 缺少运算操作符", -0.1, {}
            
            if not isinstance(operand1, (int, float)) or not isinstance(operand2, (int, float)):
                return "错误: 操作数必须是数字", -0.1, {}
            
            # 执行运算
            result = 0.0
            if operation == "add":
                result = operand1 + operand2
            elif operation == "minus":
                result = operand1 - operand2
            elif operation == "multiply":
                result = operand1 * operand2
            elif operation == "divide":
                if operand2 == 0:
                    return "错误: 除数不能为零", -0.1, {}
                result = operand1 / operand2
            else:
                return f"错误: 不支持的运算 '{operation}'", -0.1, {}
            
            # 更新实例状态
            self._instance_dict[instance_id]["operation_count"] += 1
            # print(f"ArithmeticTool: instance_id: {instance_id}, operation_count: {self._instance_dict[instance_id]['operation_count']}")
            self._instance_dict[instance_id]["history"].append({
                "operation": operation,
                "operand1": operand1,
                "operand2": operand2,
                "result": result
            })
            
            # 构建响应
            response = f"运算结果: {operand1} {operation} {operand2} = {result}"
            
            # 计算单轮工具奖励
            reward = 0.1
            
            metrics = {
                "operation": operation,
                "operand1": operand1,
                "operand2": operand2,
                "result": result,
                "operation_count": self._instance_dict[instance_id]["operation_count"]
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"ArithmeticTool执行错误: {str(e)}")
            return f"执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        # 基于操作次数和结果计算奖励
        instance = self._instance_dict[instance_id]
        operation_count = instance["operation_count"]

        # 设定基础奖励为1.0，每多一次操作，奖励减少0.1，最低为0
        base_reward = max(1.0 - (operation_count - 1) * 0.1, 0.0)
        
        # 如果结果不为零，额外奖励
        # if current_result != 0:
        #     base_reward += 0.2
        
        return min(base_reward, 1.0)