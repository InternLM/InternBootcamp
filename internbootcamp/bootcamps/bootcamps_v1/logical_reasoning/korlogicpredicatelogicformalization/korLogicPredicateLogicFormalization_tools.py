import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicpredicatelogicformalization.korLogicPredicateLogicFormalization_reward_calculator import KorlogicpredicatelogicformalizationRewardCalculator

# 导入依赖库
import re
import random
from collections import OrderedDict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class KorlogicpredicatelogicformalizationVerificationTool(BaseTool):
    """Korlogicpredicatelogicformalization验证工具"""
    
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
            score = KorlogicpredicatelogicformalizationRewardCalculator.verify_score(
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
            logger.error(f"KorlogicpredicatelogicformalizationVerificationTool执行错误: {str(e)}")
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
    def _normalize(expr):
        return expr.replace(' ', '').upper()

    def _create_universal_implication(self):
        domain_map = {
            "humans": ["breathe", "are mortal"],
            "students": ["study hard", "attend classes"],
            "prime numbers": ["are even", "are greater than 2"],
            "birds": ["fly", "have feathers"],
        }
        subject, conditions = random.choice(list(domain_map.items()))
        condition = random.choice(conditions)

        return {
            "description": f"Using universal domain: All {subject} {condition}.",
            "predicates": {
                "F(x)": f"x is a {subject}",
                "G(x)": f"x {condition}"
            },
            "correct_answer": "Ax(F(x)⇒G(x))"
        }

    def _create_existential_conjunction(self):
        entities = {
            "rabbits": ["run fast", "have long ears"],
            "cars": ["are red", "have turbo engines"],
            "apples": ["are sweet", "are organic"],
            "turtles": ["swim slowly", "have hard shells"],
        }
        subject, properties = random.choice(list(entities.items()))
        prop = random.choice(properties)

        return {
            "description": f"Using universal domain: Some {subject} {prop}.",
            "predicates": {
                "F(x)": f"x is a {subject}",
                "G(x)": f"x {prop}"
            },
            "correct_answer": "Ex(F(x)&G(x))"
        }

    def _create_0ary_predicate(self):
        constants = ["a", "b", "c", "d"]
        templates = [
            ("{c} is both {p1} and {p2}", "&"),
            ("If {c1} is {p} then {c2} is {p}", "⇒"),
            ("Either {c1} is {p} or {c2} is {p}", "|"),
            ("Neither {c1} nor {c2} is {p}", "∼{0}&∼{1}")
        ]
        template, conn = random.choice(templates)

        if template.count("{c}") == 1:
            c = random.choice(constants)
            p1, p2 = random.sample(["F", "G", "H"], 2)
            return {
                "description": template.format(c=c, p1=p1, p2=p2),
                "predicates": {
                    f"{p1}({c})": f"{c} has property {p1}",
                    f"{p2}({c})": f"{c} has property {p2}"
                },
                "correct_answer": f"{p1}({c}){conn}{p2}({c})"
            }
        else:
            c1, c2 = random.sample(constants, 2)
            p = random.choice(["F", "G"])
            if "Neither" in template:
                answer = conn.format(f"{p}({c1})", f"{p}({c2})")
            else:
                answer = f"{p}({c1}){conn}{p}({c2})"
            return {
                "description": template.format(c1=c1, c2=c2, p=p),
                "predicates": {
                    f"{p}({c1})": f"{c1} has property {p}",
                    f"{p}({c2})": f"{c2} has property {p}"
                },
                "correct_answer": answer
            }

    def _create_nested_quantifiers(self):
        relations = {
            "faster than": ["rabbits", "turtles"],
            "smarter than": ["humans", "animals"],
            "older than": ["students", "teachers"],
        }
        rel_desc, (subject, obj) = random.choice(list(relations.items()))

        return {
            "description": f"Symbolize: Some {subject} are {rel_desc} all {obj}.",
            "predicates": {
                "F(x)": f"x is a {subject}",
                "G(y)": f"y is a {obj}",
                "H(x,y)": f"x is {rel_desc} y"
            },
            "correct_answer": "Ex(F(x)&Ay(G(y)⇒H(x,y)))"
        }

    def _create_negation_case(self):
        return {
            "description": "No humans can fly. (Using universal domain)",
            "predicates": {
                "F(x)": "x is human",
                "G(x)": "x can fly"
            },
            "correct_answer": "Ax(F(x)⇒∼G(x))"
        }

    def _create_multiple_quantifiers(self):
        return {
            "description": "Every person has someone they love. (Domain: people)",
            "predicates": {
                "F(x,y)": "x loves y"
            },
            "correct_answer": "AxEyF(x,y)"
        }
