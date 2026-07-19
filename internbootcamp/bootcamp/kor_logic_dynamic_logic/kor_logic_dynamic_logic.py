"""### 谜题描述
1.Symbol Definitions
- Command: `c` represents a basic operation within a program.
- Proposition: `φ` represents a statement or condition.
- Program State: Represents the system state after the execution of a command.

2.Dynamic Operators
- Necessity Operator: `[ c ]φ` indicates that after executing command `c`, the proposition `φ` will necessarily be true.
- Possibility Operator: `⟨ c ⟩φ` indicates that after executing command `c`, the proposition `φ` may be true.

3.Axioms and Rules
- Substitution Rule:If `c` behaves the same as `d`, then `[ c ]φ` is equivalent to `[ d ]φ`.
- Sequence Rule:`[ c_1; c_2 ]φ` is equivalent to `[ c_1 ][ c_2 ]φ`.
- Choice Rule:`[ c_1 + c_2 ]φ` is equivalent to `([ c_1 ]φ ∨ [ c_2 ]φ)`.
- Loop Rule:For the loop command `c*`, `[ c* ]φ` is equivalent to `φ ∨ ([ c ][ c* ]φ)`.
- Concurrent Rule:If `c_1` and `c_2` can be executed concurrently, then `⟨ c_1 || c_2 ⟩φ` is equivalent to `⟨ c_1 ⟩⟨ c_2 ⟩φ ∨ ⟨ c_2 ⟩⟨ c_1 ⟩φ`.
- Interruption Rule:If `c_1` can interrupt `c_2`, then `⟨ c_1; c_2 ⟩φ` is equivalent to `⟨ c_1 ⟩φ`.
- Exception Rule:If `c` may trigger an exception `e`, then `[ c ]φ` is equivalent to `([ c ]φ ∧ [ e ]φ)`.
- Resource Limitation Rule:If the command `c` is subject to resource limitation `R`, then `[ c ]φ` is equivalent to `(R ∧ [ c ]φ)`.
- Dependency Rule:If the execution of `c_1` depends on `c_2`, then `[ c_1 ]φ` is equivalent to `[ c_2 ][ c_1 ]φ`.
- Priority Rule:If `c_1` has higher priority than `c_2`, then `⟨ c_1; c_2 ⟩φ` is equivalent to `⟨ c_1 ⟩⟨ c_2 ⟩φ`.
- History Rule:If the execution of `c` depends on the historical command `h`, then `[ c ]φ` is equivalent to `[ h ][ c ]φ`.
- Prediction Rule:If the system can predict the outcome of `c`, then `[ c ]φ` is equivalent to `[ predict(c) ]φ`.Example questions are as follows:

<example 0>
Express using a logical expression that after executing the command sequence c1; c2, the proposition φ will necessarily be true.
Please provide your answer in the format of [[]].
</example 0>

<example 1>
Write out a logical expression that represents the possibility of the proposition φ being true after executing the command c.
Please provide your answer in the format of [[]].
</example 1>

<example 2>
Write out a logical expression that represents the proposition φ necessarily being true after the selection of executing command c1 or c2.
Please provide your answer in the format of [[]].In all expressions, the simplest form after equivalence must be used, i.e., have the fewest occurrences of [] and <>.
</example 2>

<example 3>
If Alice is convinced that the loop command c* will continue to execute until the proposition φ is true, what logical expression should be used to represent her belief?
Please provide your answer in the format of [[]].In all expressions, the simplest form after equivalence must be used, i.e., have the fewest occurrences of [] and <>.
</example 3>

<example 4>
If Alice considers that executing the command c results in the library's open state being represented by the proposition open, 
and she believes that after executing c, it is certain that open will be true, 
how would you express Alice's belief in logical terms?

Please provide your answer in the format of [[]].
</example 4>

<example 5>
If Alice is convinced that the loop command c* will persist in execution until the proposition φ is true, what logical expression should be used to represent her belief?
Please provide your answer in the format of [[]].
</example 5>

<example 6>
If the commands c and d are equivalent according to the Substitution Rule, with what logical expression is [c]φ equivalent?
Please provide your answer in the format of [[]].
</example 6>

<example 7>
According to the Concurrent Rule,
if two commands c1 and c2 can be executed simultaneously, 
and neither affects the truth value of the proposition φ, 
please write out the logical expression.

Please provide your answer in the format of [[]].In all expressions, the simplest form after equivalence must be used, i.e., have the fewest occurrences of [] and <>.
</example 7>

<example 8>
Which of the following rules applies to the situation where an exception e may be triggered after the execution of the command c1?

A. Substitution Rule
B. Sequence Rule
C. Choice Rule
D. Loop Rule
E. Concurrent Rule
F. Interruption Rule
G. Exception Rule
H. Resource Limitation Rule
I. Dependency Rule
J. Priority Rule
K. History Rule
L. Prediction Rule

Please provide your answer in the format of [[A/B/C/D/E/F/G/H/I/J/K/L]].
</example 8>

<example 9>
If Alice is certain that once the resource limitation R is satisfied, the execution of command c will inevitably result in the outcome result being true, to which of the following rules does this belong?

A. Substitution Rule
B. Sequence Rule 
C. Choice Rule 
D. Loop Rule   
E. Concurrent Rule  
F. Interruption Rule
G. Exception Rule
H. Resource Limitation Rule
I. Dependency Rule
J. Priority Rule
K. History Rule
L. Prediction Rule
    
Please provide your answer in the format of [[A/B/C/D/E/F/G/H/I/J/K/L]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import re
import random

class KorLogicDynamicLogicbootcamp(Basebootcamp):
    RULE_MAP = {
        'A': 'Substitution Rule',
        'B': 'Sequence Rule',
        'C': 'Choice Rule',
        'D': 'Loop Rule',
        'E': 'Concurrent Rule',
        'F': 'Interruption Rule',
        'G': 'Exception Rule',
        'H': 'Resource Limitation Rule',
        'I': 'Dependency Rule',
        'J': 'Priority Rule',
        'K': 'History Rule',
        'L': 'Prediction Rule'
    }
    
    def __init__(self, **params):
        self.max_attempts = params.get('max_attempts', 3)  # 可配置参数示例
        super().__init__(**params)
    
    def case_generator(self):
        problem_type = random.choice(['expression', 'multiple_choice'])
        return self._generate_expression_problem() if problem_type == 'expression' \
            else self._generate_multiple_choice_problem()

    def _generate_expression_problem(self):
        cases = [
            # 基础规则集
            {
                'rule': 'Sequence',
                'input': '[c1;c2]φ',
                'answer': '[c1][c2]φ',
                'variants': ['[c2;c1]φ']  # 无效变体示例
            },
            {
                'rule': 'Choice',
                'input': '[c1 + c2]φ',
                'answer': '([c1]φ ∨ [c2]φ)',
                'variants': ['([c2]φ ∨ [c1]φ)']
            },
            {
                'rule': 'Loop',
                'input': '[c*]φ',
                'answer': '(φ ∨ [c][c*]φ)',
                'variants': ['(φ∨[c][c*]φ)']
            },
            # 扩展规则集
            {
                'rule': 'Concurrent',
                'input': '⟨c1||c2⟩φ',
                'answer': '(⟨c1⟩⟨c2⟩φ ∨ ⟨c2⟩⟨c1⟩φ)',
                'variants': ['⟨c2||c1⟩φ']
            },
            {
                'rule': 'Interruption',
                'input': '⟨c1;c2⟩φ',
                'answer': '⟨c1⟩φ',
                'variants': []
            }
        ]
        case = random.choice(cases)
        return {
            'type': 'expression',
            'rule': case['rule'],
            'problem': f"Convert '{case['input']}' to equivalent simplest form",
            'expected': case['answer'],
            'valid_variants': [case['answer']] + case['variants']
        }

    def _generate_multiple_choice_problem(self):
        cases = [
            {
                'scenario': "Exception e may be triggered during command execution",
                'correct': 'G',
                'distractors': ['F', 'L']
            },
            {
                'scenario': "Execution depends on historical command h",
                'correct': 'K',
                'distractors': ['I', 'J']
            },
            {
                'scenario': "Commands c1 and c2 can be executed in parallel",
                'correct': 'E',
                'distractors': ['J', 'F']
            }
        ]
        case = random.choice(cases)
        options = random.sample(
            [chr(65+i) for i in range(12) if chr(65+i) != case['correct']],
            3
        ) + [case['correct']]
        random.shuffle(options)
        
        return {
            'type': 'multiple_choice',
            'scenario': case['scenario'],
            'correct': case['correct'],
            'options': options
        }

    @staticmethod
    def prompt_func(question_case):
        
        rule = """
### 1. 符号定义
- **命令**：`c` 表示程序中的一个基本操作。
- **命题**：`φ` 表示一个陈述或条件。
- **程序状态**：表示执行某个命令后系统的状态。

---

### 2. 动态算子
- **必然性算子**：`[ c ]φ` 表示在执行命令 `c` 后，命题 `φ` 必然为真。
- **可能性算子**：`⟨ c ⟩φ` 表示在执行命令 `c` 后，命题 `φ` 可能为真。

---

### 3. 公理与规则
- **替换规则**：如果 `c` 和 `d` 的行为相同，则 `[ c ]φ` 等价于 `[ d ]φ`。
- **顺序规则**：`[ c_1; c_2 ]φ` 等价于 `[ c_1 ][ c_2 ]φ`。
- **选择规则**：`[ c_1 + c_2 ]φ` 等价于 `([ c_1 ]φ ∨ [ c_2 ]φ)`。
- **循环规则**：对于循环命令 `c*`，`[ c* ]φ` 等价于 `φ ∨ ([ c ][ c* ]φ)`。
- **并发规则**：如果 `c_1` 和 `c_2` 可以并发执行，则 `⟨ c_1 || c_2 ⟩φ` 等价于 `⟨ c_1 ⟩⟨ c_2 ⟩φ ∨ ⟨ c_2 ⟩⟨ c_1 ⟩φ`。
- **中断规则**：如果 `c_1` 可以中断 `c_2`，则 `⟨ c_1; c_2 ⟩φ` 等价于 `⟨ c_1 ⟩φ`。
- **异常规则**：如果 `c` 可能触发异常 `e`，则 `[ c ]φ` 等价于 `([ c ]φ ∧ [ e ]φ)`。
- **资源限制规则**：如果命令 `c` 受到资源限制 `R`，则 `[ c ]φ` 等价于 `(R ∧ [ c ]φ)`。
- **依赖规则**：如果 `c_1` 的执行依赖于 `c_2`，则 `[ c_1 ]φ` 等价于 `[ c_2 ][ c_1 ]φ`。
- **优先级规则**：如果 `c_1` 的优先级高于 `c_2`，则 `⟨ c_1; c_2 ⟩φ` 等价于 `⟨ c_1 ⟩⟨ c_2 ⟩φ`。
- **历史规则**：如果 `c` 的执行依赖于历史命令 `h`，则 `[ c ]φ` 等价于 `[ h ][ c ]φ`。
- **预测规则**：如果系统可以预测 `c` 的结果，则 `[ c ]φ` 等价于 `[ predict(c) ]φ`。"""
        
        if question_case['type'] == 'expression':
            return rule + '\n' + f"""Apply logical rules to simplify the expression:
            
{question_case['problem']}

Rules available:
- {question_case['rule']} Rule

Format your answer within [[double brackets]]."""
        else:
            options = '\n'.join(
                [f"{opt}: {KorLogicDynamicLogicbootcamp.RULE_MAP[opt]}" 
                 for opt in question_case['options']]
            )
            return rule + '\n' + f"""Which rule applies to this scenario?

Scenario: {question_case['scenario']}

Options:
{options}

Answer format: [[LETTER]]"""

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity['type'] == 'multiple_choice':
            return solution.upper() == identity['correct']
        else:
            return cls._normalize(solution) in identity['valid_variants']

    @staticmethod
    def _normalize(expr):
        # 统一表达式格式处理
        return re.sub(r'\s+', '', expr).replace('⟨', '[').replace('⟩', ']')

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorLogicDynamicLogicbootcamp
        bootcamp = KorLogicDynamicLogicbootcamp()
        case = bootcamp.case_generator()
        while True:
            print('='*50, 'case', '='*50 + '\n', case, '\n' ,'='*50, 'case', '='*50)
            print('='*50, bootcamp_cls.__name__, '='*50 + '\n', bootcamp_cls.prompt_func(case),'\n' +'='*50, bootcamp_cls.__name__, '='*50)
            input_answer = input('Enter your answer: ')
            print('提取到的答案：', bootcamp_cls.extract_output(input_answer), '\n')
            print('你的答案得分：', bootcamp_cls.verify_score(input_answer, case,short_penalty=False, format_penalty=False))
            exit_or_not = input('是否退出？(y/n)')
            if exit_or_not == 'y':
                break