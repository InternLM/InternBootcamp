import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicepistemiclogic.korLogicEpistemicLogic_reward_calculator import KorlogicepistemiclogicRewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class KorlogicepistemiclogicVerificationTool(BaseTool):
    """Korlogicepistemiclogic验证工具"""
    
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
            score = KorlogicepistemiclogicRewardCalculator.verify_score(
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
            logger.error(f"KorlogicepistemiclogicVerificationTool执行错误: {str(e)}")
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
