import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogiccanonicalpropositions.korLogicCanonicalPropositions_reward_calculator import KorlogiccanonicalpropositionsRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class KorlogiccanonicalpropositionsVerificationTool(BaseTool):
    """Korlogiccanonicalpropositions验证工具"""
    
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
            score = KorlogiccanonicalpropositionsRewardCalculator.verify_score(
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
            logger.error(f"KorlogiccanonicalpropositionsVerificationTool执行错误: {str(e)}")
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
    def _gen_relationship_case(self):
        case = {
            "type": "relationship",
            "pairs": [],
            "options": ["A.*", "B.x", "C.@", "D.%"],
            "key": [],
            "relation_definitions": self.relation_definitions.copy()  # 修复1：添加定义信息
        }

        for _ in range(2):
            rel_type, symbol_pair = self._random_relation_pair()
            context = random.choice(self.variable_pool)

            statements = [
                self._symbol_to_natural(symbol_pair[0], context),
                self._symbol_to_natural(symbol_pair[1], context)
            ]

            case["pairs"].append(statements)
            case["key"].append(rel_type)

        return case

    def _gen_symbolization_case(self):
        variables = random.sample(self.variable_pool, 2)
        structure = random.choice([
            ("permitted", "prohibited"),
            ("mandatory", "prohibited"),
            ("prohibited", "permitted not"),
            ("mandatory", "permitted not")  # 修复3：新增结构类型
        ])

        return {
            "type": "symbolization",
            "sentence": f"{variables[0]} is {structure[0]}, but {variables[1]} is {structure[1]}.",
            "mapping": {chr(97+i): var for i, var in enumerate(variables)},
            "solution": self._structure_to_symbols(structure)
        }

    def _gen_formula_case(self):
        formula = random.choice(self.formula_pool)
        context_var = random.choice(self.variable_pool)

        premise = self._apply_formula_context(formula[1].split('←→')[0], context_var)
        options = self._generate_formula_options(formula, context_var)

        return {
            "type": "formula",
            "question": f"Which formula corresponds to: {premise}?",
            "options": options,
            "correct": formula[0]
        }

    @staticmethod
    def _random_relation_pair():
        relations = {
            '*': [('¶p', '§¬p'), ('‽p', '§p')],
            'x': [('¶p', '‽p')],
            '@': [('§p', '§¬p')],
            '%': [('¶p', '§p'), ('‽p', '§¬p')]
        }
        rel_type = random.choice(list(relations.keys()))
        return rel_type, random.choice(relations[rel_type])

    def _symbol_to_natural(self, symbol, context):
        modality_map = {
            '¶': ['must', 'is obligatory for'],
            '§': ['may', 'is permitted for'],
            '‽': ['must not', 'is prohibited for']
        }

        operator, proposition = symbol[0], symbol[1:]
        negation = "not " if '¬' in proposition else ""
        clean_prop = proposition.replace('¬', '')

        modality = random.choice(modality_map[operator])
        return f"{modality} {negation}{context}"

    def _structure_to_symbols(self, structure):
        conversion = {
            ('permitted', 'prohibited'): ('§p', '‽q'),
            ('mandatory', 'prohibited'): ('¶p', '‽q'),
            ('prohibited', 'permitted not'): ('‽p', '§¬q'),
            ('mandatory', 'permitted not'): ('¶p', '§¬q')  # 修复3：新增转换规则
        }
        return ' ∧ '.join(conversion[structure])

    def _apply_formula_context(self, formula_part, context):
        replacements = {
            'p': context,
            '§': 'permitted',
            '¶': 'mandatory',
            '‽': 'prohibited'
        }
        for k, v in replacements.items():
            formula_part = formula_part.replace(k, v)
        return formula_part.capitalize()

    def _generate_formula_options(self, formula, context):
        options = {chr(65): f"Formula {formula[0]}: {formula[2]}"}

        # 生成干扰项（排除正确公式）
        distractors = [f for f in self.formula_pool if f[0] != formula[0]]
        random.shuffle(distractors)

        for i in range(1, 4):
            if i-1 < len(distractors):
                options[chr(65+i)] = f"Formula {distractors[i-1][0]}: {distractors[i-1][2]}"
            else:  # 如果公式池不够，补充通用干扰项
                options[chr(65+i)] = f"Formula {random.randint(1,12)}: Generic Principle"

        return options

    @staticmethod
    def _rel_type_to_option(rel_type):
        return {'*':'A', 'x':'B', '@':'C', '%':'D'}[rel_type]
