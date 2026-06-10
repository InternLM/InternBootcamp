from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicpredicatelogicformalization.korLogicPredicateLogicFormalization_reward_calculator import KorlogicpredicatelogicformalizationRewardCalculator

# 导入依赖库
import re
import random
from collections import OrderedDict




class KorlogicpredicatelogicformalizationInteraction(BaseInteraction):
    """Korlogicpredicatelogicformalization交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = KorlogicpredicatelogicformalizationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korLogicPredicateLogicFormalization问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
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
