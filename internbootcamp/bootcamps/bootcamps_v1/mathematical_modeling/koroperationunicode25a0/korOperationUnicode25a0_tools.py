import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25a0.korOperationUnicode25a0_reward_calculator import Koroperationunicode25a0RewardCalculator

# 导入依赖库
import random
import re
import sympy

# === 源文件中的全局变量 ===

x, y = sympy.symbols('x y')

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicode25a0VerificationTool(BaseTool):
    """Koroperationunicode25a0验证工具"""
    
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
            score = Koroperationunicode25a0RewardCalculator.verify_score(
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
            logger.error(f"Koroperationunicode25a0VerificationTool执行错误: {str(e)}")
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
    def _generate_term(self):
        term_types = [
            # 多项式项
            lambda: x**random.randint(1, self.max_degree),
            lambda: y**random.randint(1, self.max_degree),
            # 三角函数
            lambda: sympy.sin(random.choice([x, y])),
            lambda: sympy.cos(random.choice([x, y])),
            # 指数函数
            lambda: sympy.exp(x),
            # 分式项
            lambda: sympy.Mul(
                sympy.Poly(random.randint(1, 3)*x**random.randint(0,2), x), 
                sympy.Pow(y, -random.randint(1,2)), 
                evaluate=False
            ),
            # 常数项
            lambda: sympy.Integer(random.randint(1, 5))
        ]
        return random.choice(term_types)()

    def _generate_expression(self):
        num_terms = random.randint(1, self.max_terms)
        expr = sympy.Integer(0)
        for _ in range(num_terms):
            term = self._generate_term()
            # 确保不生成全零表达式
            if expr == 0:
                expr = term
            else:
                expr += term
        return expr
