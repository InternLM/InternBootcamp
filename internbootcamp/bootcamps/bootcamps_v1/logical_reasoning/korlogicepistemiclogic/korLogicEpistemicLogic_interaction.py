from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicepistemiclogic.korLogicEpistemicLogic_reward_calculator import KorlogicepistemiclogicRewardCalculator

# 导入依赖库
import re
import random




class KorlogicepistemiclogicInteraction(BaseInteraction):
    """Korlogicepistemiclogic交互管理器"""
    
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
        score = KorlogicepistemiclogicRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korLogicEpistemicLogic问题！"""
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
    def _load_templates(self):
        return [
            # 信念公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Belief",
                "template": {
                    "scenario": "根据信念公理，如果{name}坚信{proposition}（B_{name}({proposition})），我们可以得出以下哪个结论？",
                    "options": [
                        {"text": "{name}可能怀疑{proposition}。", "is_correct": False},
                        {"text": "{proposition}是真实的。", "is_correct": True},
                        {"text": "{name}不知道{proposition}。", "is_correct": False}
                    ]
                }
            },
            # 自反性公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Reflexivity",
                "template": {
                    "scenario": "根据自反性公理，如果{name}坚信某个命题是真的，这意味着什么？",
                    "options": [
                        {"text": "{name}可能对该命题产生怀疑。", "is_correct": False},
                        {"text": "{name}确信自己坚信这个命题。", "is_correct": True},
                        {"text": "{name}和其他人全都知道这个命题。", "is_correct": False}
                    ]
                }
            },
            # 传递性公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Transitivity",
                "requires_two_names": True,
                "template": {
                    "scenario": "根据传递性公理，如果{name1}可以识别{name2}的信念状态（{name1}R{name2}），并且{name1}坚信{proposition}（B_{name1}({proposition})），那么{name2}对该命题的态度是什么？",
                    "options": [
                        {"text": "{name2}可能怀疑该命题。", "is_correct": False},
                        {"text": "{name2}坚信该命题。", "is_correct": True},
                        {"text": "{name2}的态度无法确定。", "is_correct": False}
                    ]
                }
            },
            # 共同信念选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Common Belief",
                "template": {
                    "scenario": "如果命题{proposition}是群体{group}的共同信念，这意味着什么？",
                    "options": [
                        {"text": "{group}中的每个成员都坚信{proposition}。", "is_correct": True},
                        {"text": "只有部分成员坚信{proposition}。", "is_correct": False},
                        {"text": "{group}的成员都怀疑{proposition}。", "is_correct": False}
                    ]
                }
            },
            # 怀疑引入公理选择题模板
            {
                "type": "multiple_choice",
                "axiom": "Doubt Introduction",
                "template": {
                    "scenario": "根据怀疑引入公理，如果{name}怀疑{proposition}（H_{name}({proposition})），这意味着什么？",
                    "options": [
                        {"text": "{name}坚信{proposition}。", "is_correct": False},
                        {"text": "{name}不坚信{proposition}。", "is_correct": True},
                        {"text": "{name}知道{proposition}是假的。", "is_correct": False}
                    ]
                }
            },
            # 共同信念表达式模板
            {
                "type": "expression",
                "axiom": "Common Belief",
                "template": {
                    "scenario": "如果命题{proposition}是群体{group}的共同信念，但个体{name}怀疑该命题，根据共同信念的定义，对应的逻辑表达式是什么？",
                    "correct_expression": "G_{proposition} ∧ H_{name}_{proposition}"
                }
            },
            # 自反性公理表达式模板
            {
                "type": "expression",
                "axiom": "Reflexivity",
                "template": {
                    "scenario": "如果{name}确信{proposition}（B_{name}({proposition})），并且根据自反性公理确信自己确信此事，对应的逻辑表达式是什么？",
                    "correct_expression": "B_{name}_{proposition} ∧ B_{name}(B_{name}_{proposition})"
                }
            }
        ]

    def _fill_template(self, template):
        params = {}

        # 处理需要两个不同名字的情况
        if template.get('requires_two_names', False):
            names = random.sample(self.names, 2)
            params['name1'] = names[0]
            params['name2'] = names[1]
        else:
            params['name'] = random.choice(self.names)

        params['proposition'] = random.choice(self.propositions)
        params['group'] = random.choice(self.groups)

        filled = {
            "type": template["type"],
            "axiom": template["axiom"],
            "scenario": template["template"]["scenario"].format(**params)
        }

        if template["type"] == "multiple_choice":
            options = []
            correct_answer = None
            for idx, opt in enumerate(template["template"]["options"]):
                option_text = opt["text"].format(**params)
                letter = chr(65 + idx)
                options.append(f"{letter}. {option_text}")
                if opt["is_correct"]:
                    correct_answer = letter
            filled["options"] = options
            filled["correct_answer"] = correct_answer
        elif template["type"] == "expression":
            filled["correct_expression"] = template["template"]["correct_expression"].format(**params).replace(" ", "")

        return filled
