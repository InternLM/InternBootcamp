import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class KorlogiccooperativeprincipleInstructionGenerator(BaseInstructionGenerator):
    """Korlogiccooperativeprinciple Bootcamp指令生成器"""
    
    def __init__(self, case_weights=None, **kwargs):
        """
        初始化Korlogiccooperativeprinciple指令生成器
        
        Args:
            case_weights: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.lexicon = {
            'strength_pairs': [
                ('love', 'like'), 
                ('all', 'some'),
                ('know', 'believe'),
                ('finished', 'managed to get'),
                ('perfect', 'good enough'),
                ('love', 'like'), 
                ('all', 'some'),
                ('know', 'believe'),
                ('finished', 'managed to get'),
                ('perfect', 'good enough'),
                ('adore', 'appreciate'),
                ('worship', 'respect'),
                ('complete', 'partially finish'),
                ('excel', 'do well'),
                ('master', 'understand'),
                ('conquer', 'overcome'),
                ('destroy', 'damage'),
                ('obliterate', 'weaken'),
                ('dominate', 'influence'),
                ('control', 'guide'),
                ('fulfill', 'satisfy'),
                ('treasure', 'value'),
                ('cherish', 'enjoy'),
                ('idolize', 'admire'),
                ('venerate', 'respect'),
                ('perfectly execute', 'attempt'),
                ('fully commit', 'try'),
            ],
            'inference_types': [
                ('buy car', 'has doors', '连接推理'),
                ('mother and baby', 'parent-child', '属性推理'),
                ('nurse', 'female', '常识推理'),
                ('buy car', 'has doors', '连接推理'),
                ('mother and baby', 'parent-child', '属性推理'),
                ('nurse', 'female', '常识推理'),
                ('own a dog', 'pet owner', '属性推理'),
                ('drive a car', 'has wheels', '连接推理'),
                ('teacher', 'educated', '常识推理'),
                ('doctor', 'medical professional', '属性推理'),
                ('eat pizza', 'has cheese', '连接推理'),
                ('programmer', 'uses computer', '常识推理'),
                ('own a house', 'has roof', '连接推理'),
                ('father and son', 'family relation', '属性推理'),
                ('pilot', 'flies plane', '常识推理'),
                ('read book', 'has pages', '连接推理'),
                ('athlete', 'physically fit', '常识推理'),
                ('write letter', 'uses pen', '连接推理'),
                ('student', 'attends school', '常识推理'),
                ('cook meal', 'uses stove', '连接推理'),
                ('musician', 'plays instrument', '常识推理'),
                ('paint picture', 'uses brush', '连接推理'),
                ('gardener', 'plants flowers', '常识推理'),
            ],
            'marked_phrases': [
                ('essentially wrapped up', 'finished'),
                ('secured tickets', 'bought tickets'),
                ('persuaded to join', 'asked to join'),
                ('essentially wrapped up', 'finished'),
                ('secured tickets', 'bought tickets'),
                ('persuaded to join', 'asked to join'),
                ('made a decision', 'decided'),
                ('came to a conclusion', 'concluded'),
                ('took a seat', 'sat down'),
                ('initiated contact', 'contacted'),
                ('engaged in conversation', 'talked'),
                ('expressed gratitude', 'thanked'),
                ('provided assistance', 'helped'),
                ('demonstrated ability', 'showed skill'),
                ('exhibited patience', 'was patient'),
                ('displayed courage', 'was brave'),
                ('performed an analysis', 'analyzed'),
                ('conducted an investigation', 'investigated'),
                ('carried out a task', 'did a task'),
                ('executed a plan', 'planned'),
                ('utilized resources', 'used resources'),
                ('implemented a solution', 'solved'),
                ('generated ideas', 'brainstormed'),
            ]
        }
        self.weights = case_weights or [1, 1, 1]
    
    def case_generator(self):
        principle = random.choices(['A', 'B', 'C'], weights=self.weights, k=1)[0]
        case = {'correct': principle}
        
        if principle == 'A':
            s, w = random.choice(self.lexicon['strength_pairs'])
            case.update({
                'type': 'strength_hierarchy',
                'dialogue': [
                    f"你是否{s}这个？请如实回答。",
                    f"我{w}它。"
                ],
                'explanation': f"使用弱项'{w}'暗示强项'{s}'不成立"
            })
        elif principle == 'B':
            context, inference, i_type = random.choice(self.lexicon['inference_types'])
            case.update({
                'type': i_type,
                'scenario': f"{context} → {inference}",
                'explanation': f"{i_type}类型推理"
            })
        else:
            marked, plain = random.choice(self.lexicon['marked_phrases'])
            case.update({
                'type': 'marked_expression',
                'dialogue': [
                    "项目完成了吗？",
                    f"我们已经{marked}。" if random.random() > 0.5 else 
                    f"我们{marked}。"
                ],
                'contrast': plain,
                'explanation': f"使用标记表达'{marked}'代替常规'{plain}'"
            })
        return case
    
    @staticmethod
    def prompt_func(question_case):
        prompt = ["请根据对话分析适用的协作原则（答案格式：[[A/B/C]]）\n"]
        
        if 'dialogue' in question_case:
            prompt.append("对话情景：")
            prompt.extend([f"- {line}" for line in question_case['dialogue']])
        elif 'scenario' in question_case:
            prompt.append(f"场景描述：{question_case['scenario']}")
        
        prompt.append(f"请根据对话情景，选择最合适的协作原则：\nA.C*原则\nB.C%原则\nC.C!原则\n")
        prompt.append("\n正确答案是：[[ ]]")
        
        rule = "Custom Cooperation Principles\n\n1. C* Principle\n\n(1) Speaker's Criterion: Do not let your statement be weaker in information than what your knowledge allows, unless a stronger statement conflicts with the Information Principle.\n(2) Hearer's Inference:\n    - CQ1: If the speaker says A(w), and <s, w> brackets the words in order of information strength with s (strong) followed by w (weak), A(s) entails A(w), then it can be inferred that K~(A(s)), meaning the speaker knows that the stronger information cannot be established.\n    - CQ2: The speaker states A(w), which does not entail the content of the embedded sentence Q, but the content of Q is entailed by the stronger information A(s), and {s, w} form a contrast set, then it can be deduced that ~K(Q), meaning the speaker does not know whether Q can be established.\n\n2. C% Principle\n\n(1) Speaker's Criterion: Minimalization Criterion - Speak as little as possible, only speak to the minimum extent necessary to achieve the purpose of communication.\n(2) Hearer's Inference:\n    - CI1: Assume that the relationship between the objects and time in the sentence follows the convention unless there is clear evidence to the contrary.\n    - CI2: If a certain existence or fact exactly matches the confirmed situation, it is set that this is what the sentence is saying. The Information Principle actually refers to the speaker striving to \"speak as little as possible,\" while the hearer strives to \"expand the information\" until fully grasping the intention of the speech.\n\n3. C! Principle\n\n(1) Speaker's Criterion: Do not use lengthy, obscure, or marked expressions without reason.\n(2) Hearer's Inference: If the speaker uses a lengthy marked expression, their meaning is different from what they could have expressed with an unmarked expression, especially they should try to avoid conventional associations or derive meanings using the Information Principle."
        
        
        return rule + '\n'.join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

