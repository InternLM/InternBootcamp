from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicenumerativeinductivereasoning.korLogicEnumerativeInductiveReasoning_reward_calculator import KorlogicenumerativeinductivereasoningRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class KorlogicenumerativeinductivereasoningInteraction(BaseInteraction):
    """Korlogicenumerativeinductivereasoning交互管理器"""
    
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
        score = KorlogicenumerativeinductivereasoningRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korLogicEnumerativeInductiveReasoning问题！"""
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
    def _generate_choice_case(self, class_name, prop, total):
        problem_type = 'A' if random.random() < self.type_prob else 'B'

        if problem_type == 'A':
            observed = random.randint(3, max(3, total-1))  # 确保观察数合理
            premise = (
                f"在{class_name}类别中，研究人员随机选取了{observed}个不同个体进行观察，"
                f"发现这些样本均具有「{prop}」特征。"
            )
        else:
            observed = total
            premise = (
                f"经过全面核查，确认当前{class_name}类别下所有{total}个注册个体，"
                f"每一个都符合「{prop}」的标准。"
            )

        return {
            "type": problem_type,
            "premise": premise,
            "conclusion": f"由此推断：所有{class_name}都具有「{prop}」特征。",
            "class": class_name,
            "property": prop,
            "total": total,
            "observed": observed
        }

    def _generate_symbolic_case(self, class_name, prop, total):
        problem_type = 'A' if random.random() < self.type_prob else 'B'
        instances = [f'e{i+1}' for i in range(total)]
        sampled = random.sample(instances, k=3) if problem_type == 'A' else instances

        premise_desc = {
            'A': (
                f"观察到{sampled}都具有属性P，"
                f"这些是{class_name}类中的部分实例"
            ),
            'B': (
                f"每个实例{instances}都具有属性P，"
                f"这些构成{class_name}类的完整集合"
            )
        }[problem_type]

        conclusion_desc = {
            'A': f"所有{class_name}类的实例都具有属性P",
            'B': f"{class_name}类整体具有属性P"
        }[problem_type]

        return {
            "type": problem_type,
            "premise": premise_desc,
            "conclusion": conclusion_desc,
            "instances": instances,
            "sampled": sampled,
            "class": class_name
        }

    @staticmethod
    def _choice_prompt(case):
        return (
            "## 归纳推理类型判断\n"
            "**定义说明**\n"
            "A. *归纳推理：基于部分实例的观察得出结论\n"
            "   - 例：检查50辆共享单车→所有车辆都完好\n"
            "B. Φ归纳推理：基于全部实例的检查得出结论\n"
            "   - 例：核验所有参会人员→全部完成注册\n\n"
            "**题目描述**\n"
            f"{case['premise']}\n"
            f"{case['conclusion']}\n\n"
            "**请选择正确的推理类型**\n"
            "将答案用[[A]]或[[B]]标记"
        )

    @staticmethod
    def _symbolic_prompt(case):
        return (
            "## 逻辑符号化练习\n"
            "**符号约定**\n"
            "- e_i: 第i个实例\n"
            "- P(e_i): 实例具有属性P\n"
            "- ∀e∈S: S类的所有实例\n"
            "- P(S): 类S整体具有属性P\n\n"
            "**题目要求**\n"
            f"请将以下陈述转换为标准符号表示：\n"
            f"前提：{case['premise']}\n"
            f"结论：{case['conclusion']}\n\n"
            "**格式要求**\n"
            "按照[[前提符号];[结论符号]]格式作答\n"
            "示例：[[P(e1)∧P(e2);∀e∈S,P(e)]]"
        )

    @property
    def params(self):
        return {
            'class_names': self.class_names,
            'properties': self.properties,
            'type_prob': self.type_prob,
            'question_types': self.question_types
        }
