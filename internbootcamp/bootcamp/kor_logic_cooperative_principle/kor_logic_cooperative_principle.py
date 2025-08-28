"""### 谜题描述
Custom Cooperation Principles

1. C* Principle

(1) Speaker's Criterion: Do not let your statement be weaker in information than what your knowledge allows, unless a stronger statement conflicts with the Information Principle.
(2) Hearer's Inference:
    - CQ1: If the speaker says A(w), and <s, w> brackets the words in order of information strength with s (strong) followed by w (weak), A(s) entails A(w), then it can be inferred that K~(A(s)), meaning the speaker knows that the stronger information cannot be established.
    - CQ2: The speaker states A(w), which does not entail the content of the embedded sentence Q, but the content of Q is entailed by the stronger information A(s), and {s, w} form a contrast set, then it can be deduced that ~K(Q), meaning the speaker does not know whether Q can be established.

2. C% Principle

(1) Speaker's Criterion: Minimalization Criterion - Speak as little as possible, only speak to the minimum extent necessary to achieve the purpose of communication.
(2) Hearer's Inference:
    - CI1: Assume that the relationship between the objects and time in the sentence follows the convention unless there is clear evidence to the contrary.
    - CI2: If a certain existence or fact exactly matches the confirmed situation, it is set that this is what the sentence is saying. The Information Principle actually refers to the speaker striving to \"speak as little as possible,\" while the hearer strives to \"expand the information\" until fully grasping the intention of the speech.

3. C! Principle

(1) Speaker's Criterion: Do not use lengthy, obscure, or marked expressions without reason.
(2) Hearer's Inference: If the speaker uses a lengthy marked expression, their meaning is different from what they could have expressed with an unmarked expression, especially they should try to avoid conventional associations or derive meanings using the Information Principle.Example questions are as follows:

<example 0>
A: \"Do you have tickets for tonight's movie?\"
B: \"I bought two tickets.\" 
C: \"I managed to get two tickets.\" 
C uses \"managed to get\" instead of directly saying \"bought,\" implying that \"getting the tickets was not easy and took some effort.\"

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 0>

<example 1>
A: \"Do you love Xiao Hong? Please tell me.\"
B: \"I like her.\"
Here, the pair <love, like> forms a hierarchy. 
B answered with the weaker information, thus implying that the stronger statement \"I love her\" does not hold. 
Therefore, which principle did B use to tactfully reveal the truth?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 1>

<example 2>
A: All soccer players are on the field.
B: Some soccer players are on the field.
Here, the pair <all, some> forms a hierarchy. 
Therefore, if the speaker says B, it indicates that they know saying A does not match the facts. 

Which principle did the speaker use to reveal the truth?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 2>

<example 3>
A: I believe you are a college student.
B: I know you are a college student.

The speaker says A, which does not entail the clause \"you are a college student,\" but B can entail \"you are a college student,\" because the pair <know, believe> forms a hierarchy. 
That is to say, when the speaker says A, they do not actually know whether \"you are a college student\" is established.

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 3>

<example 4>
Xiao Ma opens the food box, and the beer is still warm → Beer is part of the food in the food box.

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 4>

<example 5>
A: \"Can we complete this project on time? I need a definite answer.\"
B: \"We have finished most of the work, with only a few details left to address.\"
C: \"We have essentially wrapped up the project, with just some minor finishing touches remaining.\"

In this dialogue, A is requesting a definite answer about whether the project can be completed on time. B's response provides some information but does not directly answer A's question, instead implying that the project is nearly finished but there is still work to be done. C's response is similar to B's but uses the expression \"essentially wrapped up the project,\" which may suggest that the project is substantially complete with only minor steps left. C's response might lead one to understand that although there are still parts of the project unfinished, the main work has been accomplished, and C has chosen a more euphemistic and optimistic way of expression, implying a high likelihood of project success while also leaving some openness, indicating there might be some unforeseen work left.

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 5>

<example 6>
The baby lying in bed cries, and the mother picks her up. → The mother is the baby's mother. (Attributive inference type)

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 6>

<example 7>
Zhang San bought a new car, but the door won't close → Zhang San's new car has doors. (Connection inference type)

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 7>

<example 8>
Xiao Wang gives flowers to a nurse. → Xiao Wang gives flowers to a female. (Common sense inference type)

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 8>

<example 9>
A: \"Can you help me borrow the materials for tomorrow's meeting?\"
B: \"I borrowed the materials.\"
C: \"I managed to get the materials.\"

In this dialogue, B's response \"I borrowed the materials\" is a direct and conventional answer, indicating that B has successfully completed the action of borrowing the materials. However, C's response \"I managed to get the materials\" uses the word \"managed,\" which may imply that the process of obtaining the materials was not simple and may involve additional effort or the use of some special methods. C's response may lead people to understand that the process of obtaining the materials was \"quite troublesome,\" or C encountered some obstacles or difficulties in obtaining the materials.

Which of the following principles does this conform to?

A. C* Principle     
B. C% Principle 
C. C! Principle

Please give your answer in the format [[A/B/C]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import random


class KorLogicCooperativePrinciplebootcamp(Basebootcamp):
    RULE_DESCRIPTIONS = {
        'A': [
            "C*原则 - 信息强度准则",
            "1. 说话者准则：除非强陈述违反信息原则，否则不应使用信息量更弱的陈述",
            "2. 听者推理：",
            "   - 若使用弱信息A(w)，且存在<s,w>强度序列，则暗示K¬A(s)",
            "   - 若A(w)不蕴含Q，但A(s)蕴含Q且{s,w}形成对比，则暗示¬KQ"
        ],
        'B': [
            "C%原则 - 最小化准则",
            "1. 说话者准则：仅传达必要的最小信息量",
            "2. 听者推理：",
            "   - 默认按常规关系理解（CI1）",
            "   - 精确匹配已知事实时优先采用（CI2）"
        ],
        'C': [
            "C!原则 - 标记性准则",
            "1. 说话者准则：避免使用复杂标记性表达",
            "2. 听者推理：当使用标记性表达时，其含义应与非标记表达不同"
        ]
    }

    def __init__(self, case_weights=None, **kwargs):
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

    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[\[([ABC])\]\]', output, re.IGNORECASE)
        return matches[-1].upper() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        return str(solution).upper() == identity['correct']

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorLogicCooperativePrinciplebootcamp
        bootcamp = KorLogicCooperativePrinciplebootcamp()
        case = bootcamp.case_generator()
        while True:
            print('='*50, 'case', '='*50 + '\n', case,'='*50, 'case', '='*50)
            print('='*50, bootcamp_cls.__name__, '='*50 + '\n', bootcamp_cls.prompt_func(case),'\n' +'='*50, bootcamp_cls.__name__, '='*50)
            input_answer = input('Enter your answer: ')
            print('你的答案得分：', bootcamp_cls.verify_score(input_answer, case,short_penalty=False, format_penalty=False))
            exit_or_not = input('是否退出？(y/n)')
            if exit_or_not == 'y':
                break
