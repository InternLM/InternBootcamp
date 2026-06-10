import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.cryptography.koroperationunicode2295.korOperationUnicode2295_reward_calculator import Koroperationunicode2295RewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicode2295VerificationTool(BaseTool):
    """Koroperationunicode2295验证工具"""
    
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
            score = Koroperationunicode2295RewardCalculator.verify_score(
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
            logger.error(f"Koroperationunicode2295VerificationTool执行错误: {str(e)}")
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
    def _generate_equation_case(self):
        operators = ['+', '-', '*']
        if self.allow_division:
            operators.append('/')

        for _ in range(100):
            x = random.uniform(-self.max_operand, self.max_operand)
            x = round(x, 1)  # 允许一位小数
            operand_index = random.choice([0, 1])
            part = random.choice(['a', 'b'])

            left_a = random.randint(-self.max_operand, self.max_operand)
            left_b = random.randint(-self.max_operand, self.max_operand)
            right_a = random.randint(-self.max_operand, self.max_operand)
            right_b = random.randint(-self.max_operand, self.max_operand)
            operator = random.choice(operators)

            if operand_index == 0:
                left_operand = {'a': 'X' if part == 'a' else left_a, 'b': 'X' if part == 'b' else left_b}
                right_operand = {'a': right_a, 'b': right_b}
                a1 = x if part == 'a' else left_a
                b1 = x if part == 'b' else left_b
                a2, b2 = right_a, right_b
            else:
                left_operand = {'a': left_a, 'b': left_b}
                right_operand = {'a': 'X' if part == 'a' else right_a, 'b': 'X' if part == 'b' else right_b}
                a1, b1 = left_a, left_b
                a2 = x if part == 'a' else right_a
                b2 = x if part == 'b' else right_b

            # 处理分母有效性
            if operator == '/':
                if (a2 == 0 and b2 == 0):
                    continue
                denominator = a2**2 + b2**2
                if denominator == 0:
                    continue

            try:
                if operator == '+':
                    target_real = a1 + a2
                    target_imag = b1 + b2
                elif operator == '-':
                    target_real = a1 - a2
                    target_imag = b1 - b2
                elif operator == '*':
                    target_real = a1 * a2 - b1 * b2
                    target_imag = a1 * b2 + b1 * a2
                else:
                    denominator = a2**2 + b2**2
                    target_real = (a1 * a2 + b1 * b2) / denominator
                    target_imag = (b1 * a2 - a1 * b2) / denominator

                # 允许浮点结果，保留两位小数
                target_real = round(target_real, 2)
                target_imag = round(target_imag, 2)

                return {
                    'type': 'equation',
                    'left_operands': [left_operand, right_operand],
                    'operator': operator,
                    'target_real': target_real,
                    'target_imag': target_imag,
                    'unknown': {'operand_index': operand_index, 'part': part},
                    'solution': round(x, 2)
                }
            except:
                continue
        return self._generate_compute_case()

    def _generate_compute_case(self):
        operators = ['+', '-', '*']
        if self.allow_division:
            operators.append('/')

        operator = random.choice(operators)

        for _ in range(100):
            a = random.randint(-self.max_operand, self.max_operand)
            b = random.randint(-self.max_operand, self.max_operand)
            c = random.randint(-self.max_operand, self.max_operand)
            d = random.randint(-self.max_operand, self.max_operand)

            if operator == '/' and (c == 0 and d == 0):
                continue

            if operator == '+':
                real = a + c
                imag = b + d
            elif operator == '-':
                real = a - c
                imag = b - d
            elif operator == '*':
                real = a * c - b * d
                imag = a * d + b * c
            else:
                denominator = c**2 + d**2
                real = (a * c + b * d) / denominator
                imag = (b * c - a * d) / denominator

            # 保留两位小数
            real = round(real, 2)
            imag = round(imag, 2)

            return {
                'type': 'compute',
                'operator': operator,
                'left_a': a,
                'left_b': b,
                'right_a': c,
                'right_b': d,
                'solution_real': real,
                'solution_imag': imag
            }

        return {
            'type': 'compute',
            'operator': '+',
            'left_a': random.randint(-self.max_operand, self.max_operand),
            'left_b': random.randint(-self.max_operand, self.max_operand),
            'right_a': random.randint(-self.max_operand, self.max_operand),
            'right_b': random.randint(-self.max_operand, self.max_operand),
            'solution_real': 0,
            'solution_imag': 0
        }
