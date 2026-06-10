import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.koroperationunicode203b.korOperationUnicode203b_reward_calculator import Koroperationunicode203bRewardCalculator

# 导入依赖库
import json
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicode203bVerificationTool(BaseTool):
    """Koroperationunicode203b验证工具"""
    
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
            score = Koroperationunicode203bRewardCalculator.verify_score(
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
            logger.error(f"Koroperationunicode203bVerificationTool执行错误: {str(e)}")
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
    def _generate_compute_case(self):
        for _ in range(self.max_attempts):
            num_operands = random.choices([2,3,4], weights=[5,3,1])[0]
            operands = [random.randint(1, self.max_operand) for _ in range(num_operands)]

            try:
                current_value = operands[0]
                for op in operands[1:]:
                    current_value = self._compute_operation(current_value, op, self.C)
            except ZeroDivisionError:
                continue

            # 允许有限概率生成结果为24的题目
            if current_value !=24 or random.random() < 0.2:
                return {
                    'type': 'compute',
                    'expression': operands,
                    'C': self.C,
                    'answer': int(current_value)
                }

        # 保底返回简单计算题
        return {
            'type': 'compute',
            'expression': [4,7],
            'C': self.C,
            'answer': 24
        }

    def _compute_operation(self, a, b, C):
        if b == 0 or a == 0:
            return 24
        if a % b == 0:
            return (a // b) + C
        if b % a == 0:
            return (b // a) + C
        return 24

    def _generate_solve_x_case(self):
        for _ in range(self.max_attempts):
            # 随机选择生成方向
            if random.random() < 0.5:  # 生成 a※X=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []

                # 寻找所有可能的X解
                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(a, X, self.C) == target:
                            solutions.append(X)
                    except:
                        continue

                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"{a}※X={target}",
                        'solutions': solutions,
                        'C': self.C
                    }
            else:  # 生成 X※a=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []

                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(X, a, self.C) == target:
                            solutions.append(X)
                    except:
                        continue

                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"X※{a}={target}",
                        'solutions': solutions,
                        'C': self.C
                    }

        # 保底返回单解问题
        return {
            'type': 'solve_x',
            'equation': "X※4=6",
            'solutions': [8],  # 8※4=2+2=4?
            'C': self.C
        }

    def _generate_solve_c_case(self):
        for _ in range(self.max_attempts):
            # 随机生成方向
            if random.random() < 0.5:
                a = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                b = a * factor
                expected = factor + self.C  # a※b = b/a + C
            else:
                b = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                a = b * factor
                expected = factor + self.C  # a※b = a/b + C

            # 避免除零错误
            if a == 0 or b == 0:
                continue

            return {
                'type': 'solve_c',
                'equation': f"{a}※{b}={expected}",
                'answer': self.C
            }

        # 保底返回
        return {
            'type': 'solve_c',
            'equation': "25※5=8",
            'answer': 3  # 25/5=5 +3=8
        }
