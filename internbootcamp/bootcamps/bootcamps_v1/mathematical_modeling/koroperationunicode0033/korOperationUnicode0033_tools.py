import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode0033.korOperationUnicode0033_reward_calculator import Koroperationunicode0033RewardCalculator

# 导入依赖库
import math
import re
import random
from typing import Optional



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicode0033VerificationTool(BaseTool):
    """Koroperationunicode0033验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = Koroperationunicode0033RewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"Koroperationunicode0033VerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法
    @staticmethod
    def expression_to_str(expr) -> str:
        if isinstance(expr, dict):
            left = KorOperationUnicode0033bootcamp.expression_to_str(expr['left'])
            right = KorOperationUnicode0033bootcamp.expression_to_str(expr['right'])
            return f"({left}{expr['operator']}{right})"
        return str(expr)

    @staticmethod
    def compute_expression(expr) -> float:
        if isinstance(expr, dict):
            left = KorOperationUnicode0033bootcamp.compute_expression(expr['left'])
            right = KorOperationUnicode0033bootcamp.compute_expression(expr['right'])
            if expr['operator'] == '①':
                return math.sqrt(left) + right**2
            return math.sqrt(left) * right
        return float(expr)

    @staticmethod
    def parse_solution(solution: str) -> float:
        solution = solution.replace(' ', '')
        # 处理分数
        frac_match = re.match(r'\\frac\{(-?\d+)\}\{(\d+)\}', solution)
        if frac_match:
            return float(frac_match[1]) / float(frac_match[2])

        # 处理根号表达式（支持系数）
        sqrt_match = re.match(r'(-?)(\d*)\\sqrt\{(\d+)\}', solution)
        if sqrt_match:
            sign = -1 if sqrt_match[1] else 1
            coeff = float(sqrt_match[2] or 1) * sign
            return coeff * math.sqrt(float(sqrt_match[3]))

        # 处理纯根号
        if solution.startswith('\\sqrt'):
            return math.sqrt(float(re.search(r'\d+', solution).group()))

        return float(solution)
