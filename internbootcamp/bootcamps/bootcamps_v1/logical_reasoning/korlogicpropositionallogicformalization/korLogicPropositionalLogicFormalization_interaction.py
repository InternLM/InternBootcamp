from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicpropositionallogicformalization.korLogicPropositionalLogicFormalization_reward_calculator import KorlogicpropositionallogicformalizationRewardCalculator

# 导入依赖库
import re
import random




class KorlogicpropositionallogicformalizationInteraction(BaseInteraction):
    """Korlogicpropositionallogicformalization交互管理器"""
    
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
        score = KorlogicpropositionallogicformalizationRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korLogicPropositionalLogicFormalization问题！"""
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
    def _generate_propositions(self):
        propositions = {}
        used_subjects = set()
        for i in range(self.num_propositions):
            while True:
                subject = random.choice(self.subjects)
                if subject not in used_subjects:
                    used_subjects.add(subject)
                    prop = random.choice(self.proposition_templates)
                    propositions[f'p{i+1}'] = f"{subject} {prop}."
                    break
        return propositions

    def _generate_symbolize_questions(self, propositions):
        questions = []
        answers = []
        variables = list(propositions.keys())
        for _ in range(self.max_questions):
            formula = self._generate_formula(variables)
            question_text = self._formula_to_natural_language(formula, propositions)
            questions.append(question_text)
            answers.append(formula)
        return questions, answers

    def _generate_formula(self, variables, depth=0):
        if depth >= 2 or len(variables) < 2:
            return random.choice(variables)

        connective = random.choice(self.allowed_connectives)
        if connective == '~':
            sub = self._generate_formula(variables, depth+1)
            return f'~{sub}'
        else:
            left = self._generate_formula(variables, depth+1)
            right = self._generate_formula(variables, depth+1)
            return f'({left}{connective}{right})'

    def _formula_to_natural_language(self, formula, propositions):
        formula = formula.replace('(', '').replace(')', '')
        parts = re.split(r'(&|\|\||~)', formula)
        parts = [p for p in parts if p]

        stack = []
        for part in parts:
            if part in ['&', '||', '~']:
                stack.append(part)
            else:
                stack.append(propositions.get(part, part))

        natural = []
        prev_op = None
        for item in stack:
            if item == '&':
                natural.append("and")
            elif item == '||':
                natural.append("or")
            elif item == '~':
                natural.append("It is not the case that")
            else:
                if prev_op == '~':
                    natural[-1] += f" {item}"
                else:
                    natural.append(item)
            prev_op = item if item in ['&', '||', '~'] else None

        return ' '.join(natural).replace(' .', '.')

    @staticmethod
    def normalize(formula):
        return formula.replace(' ', '').replace('(', '').replace(')', '')
