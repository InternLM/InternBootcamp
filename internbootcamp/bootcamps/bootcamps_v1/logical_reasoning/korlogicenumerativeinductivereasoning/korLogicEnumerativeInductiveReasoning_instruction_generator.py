import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class KorlogicenumerativeinductivereasoningInstructionGenerator(BaseInstructionGenerator):
    """Korlogicenumerativeinductivereasoning Bootcamp指令生成器"""
    
    def __init__(self, class_names=None, properties=None, type_prob=0.5, question_types=None):
        """
        初始化Korlogicenumerativeinductivereasoning指令生成器
        
        Args:
            class_names: 参数描述
            properties: 参数描述
            type_prob: 参数描述
            question_types: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        # 扩展默认数据
        self.class_names = class_names or [
            '苹果', '橙子', '元素', '学生', '鸟类', '样本S', '类别T', '类别B',
            '行星', '微生物', '化合物', '历史事件', '编程语言', '几何图形',
            '国家', '化学反应', '文学作品', '数学函数'
        ]
        self.properties = properties or [
            '红色', '甜', '有原子数', '喜欢数学', '会飞', '绿色',
            '有属性Q', '蓝色', '导电', '可降解', '有历史记载',
            '面向对象', '可迭代', '可导', '有韵律', '可逆'
        ]
        self.type_prob = type_prob
        self.question_types = question_types or {
            'choice': 0.6,  # 选择题比例
            'symbolic': 0.4  # 符号题比例
        }
    
    def case_generator(self):
        # 随机选择问题类型
        q_type = random.choices(
            list(self.question_types.keys()),
            weights=list(self.question_types.values()),
            k=1
        )[0]

        # 公共参数生成
        class_name = random.choice(self.class_names)
        prop = random.choice(self.properties)
        total = random.randint(5, 20)  # 统一总量范围
        
        # 根据问题类型生成不同结构
        if q_type == 'choice':
            case = self._generate_choice_case(class_name, prop, total)
        else:
            case = self._generate_symbolic_case(class_name, prop, total)
        
        case['question_type'] = q_type
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        if question_case['question_type'] == 'choice':
            return KorLogicEnumerativeInductiveReasoningbootcamp._choice_prompt(question_case)
        return KorLogicEnumerativeInductiveReasoningbootcamp._symbolic_prompt(question_case) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
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
