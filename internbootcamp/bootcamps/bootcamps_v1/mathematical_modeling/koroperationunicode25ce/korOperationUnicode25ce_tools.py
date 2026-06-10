import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.koroperationunicode25ce.korOperationUnicode25ce_reward_calculator import Koroperationunicode25ceRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicode25ceVerificationTool(BaseTool):
    """Koroperationunicode25ce验证工具"""
    
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
            score = Koroperationunicode25ceRewardCalculator.verify_score(
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
            logger.error(f"Koroperationunicode25ceVerificationTool执行错误: {str(e)}")
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
    def compute_operator(a, b):
        """计算a◎b对应的复数平方"""
        return (a**2 - b**2, 2*a*b)

    def _generate_equation_case(self):
        """生成包含多种形式的方程"""
        equation_type = random.choice([
            'basic_left', 
            'basic_right',
            'scalar_left',
            'scalar_right'
        ])

        X = random.randint(self.min_val, self.max_val)
        a = random.randint(1, 5)  # 避免a为0导致多解
        b = random.randint(self.min_val, self.max_val)
        c = random.randint(self.min_val, self.max_val)
        k = random.randint(2, 5)

        if equation_type.startswith('basic'):
            term1_real, term1_imag = self.compute_operator(X, a)
            term2_real, term2_imag = self.compute_operator(b, c)
            op = '+' if random.random() < 0.5 else '-'

            if equation_type == 'basic_left':
                # (X◎a) ± (b◎c) = target
                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'(X◎{a}) {op} ({b}◎{c})',
                    'x_pos': 'left',
                    'params': (a, b, c, op),
                    'target': (target_real, target_imag)
                }
            else:  # basic_right
                # (b◎c) ± (X◎a) = target
                target_real = term2_real + term1_real if op == '+' else term2_real - term1_real
                target_imag = term2_imag + term1_imag if op == '+' else term2_imag - term1_imag
                return {
                    'type': 'equation',
                    'form': f'({b}◎{c}) {op} (X◎{a})',
                    'x_pos': 'right',
                    'params': (a, b, c, op),
                    'target': (target_real, target_imag)
                }

        else:  # scalar类型
            scalar = k
            if equation_type == 'scalar_left':
                # (X◎a) ± k×(b◎c) = target
                term1_real, term1_imag = self.compute_operator(X, a)
                term2_real, term2_imag = self.compute_operator(b, c)
                term2_real *= scalar
                term2_imag *= scalar
                op = '+' if random.random() < 0.5 else '-'

                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'(X◎{a}) {op} {scalar}×({b}◎{c})',
                    'x_pos': 'left_scalar',
                    'params': (a, b, c, scalar, op),
                    'target': (target_real, target_imag)
                }
            else:  # scalar_right
                # k×(X◎a) ± (b◎c) = target
                term1_real, term1_imag = self.compute_operator(X, a)
                term1_real *= scalar
                term1_imag *= scalar
                term2_real, term2_imag = self.compute_operator(b, c)
                op = '+' if random.random() < 0.5 else '-'

                target_real = term1_real + term2_real if op == '+' else term1_real - term2_real
                target_imag = term1_imag + term2_imag if op == '+' else term1_imag - term2_imag
                return {
                    'type': 'equation',
                    'form': f'{scalar}×(X◎{a}) {op} ({b}◎{c})',
                    'x_pos': 'right_scalar',
                    'params': (a, b, c, scalar, op),
                    'target': (target_real, target_imag)
                }

    @staticmethod
    def parse_complex(s):
        s = s.replace(' ', '').lower().replace('i', 'j').rstrip('j')
        try:
            c = complex(s)
            return (int(c.real), int(c.imag))
        except:
            if s:
                return (int(s), 0)
            return (0, 0)
