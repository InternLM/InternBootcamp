import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogicpropositionallogicformalization.korLogicPropositionalLogicFormalization_reward_calculator import KorlogicpropositionallogicformalizationRewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class KorlogicpropositionallogicformalizationVerificationTool(BaseTool):
    """Korlogicpropositionallogicformalization验证工具"""
    
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
            score = KorlogicpropositionallogicformalizationRewardCalculator.verify_score(
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
            logger.error(f"KorlogicpropositionallogicformalizationVerificationTool执行错误: {str(e)}")
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
