from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.korlogiccanonicalpropositions.korLogicCanonicalPropositions_reward_calculator import KorlogiccanonicalpropositionsRewardCalculator

# 导入依赖库
import re
import random
from itertools import permutations




class KorlogiccanonicalpropositionsInteraction(BaseInteraction):
    """Korlogiccanonicalpropositions交互管理器"""
    
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
        score = KorlogiccanonicalpropositionsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个korLogicCanonicalPropositions问题！"""
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
