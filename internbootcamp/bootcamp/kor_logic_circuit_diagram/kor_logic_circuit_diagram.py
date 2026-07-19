"""### 谜题描述
In a simple circuit diagram, logical operators \"negation\", \"conjunction\", and \"disjunction\" function similarly.
When there is one input it is recorded as \"I\", when there is more than 1 all inputs are represented in order as \"I1, I2, ......\".
If powered, represented as \"+\"; if not powered, represented as \"-\".
The output of the circuit diagram is represented as \"O\". Hence, a circuit diagram can be depicted and described like a truth table.Example questions are as follows:

<example 0>
Please provide a simple circuit diagram for a NOT gate, 
formatted as [[input, output]; [output when circuit is powered, output when circuit is not powered]; ...].
</example 0>

<example 1>
Please provide a simple circuit diagram for a AND gate, 
formatted as [[input, output]; [output when circuit is powered, output when circuit is not powered]; ...].
</example 1>

<example 2>
Please provide a simple circuit diagram for a OR gate, 
formatted as [[input, output]; [output when circuit is powered, output when circuit is not powered]; ...].
</example 2>

<example 3>
What is the simple circuit diagram corresponding to the logical expression ¬(p∧q)?
 Please provide the answer in the format [[input, output]; [output when circuit is powered, output when circuit is not powered]; ...].
</example 3>

<example 4>
What is the simple circuit diagram corresponding to the logical expression (p∧q)∨(p∧r)?
Please provide the answer in the format [[input, output]; [output when circuit is powered, output when circuit is not powered]; ...].
</example 4>

<example 5>
Assuming an \"OR logic gate\" 
has one input I1 as \"-\" and the other input I2 as \"+\",
what is the output? 
Please provide the answer in the format [[output]].
</example 5>

<example 6>
Assuming an \"AND logic gate\" 
has one input I1 as \"+\" and the other input I2 as \"-\",
what is the output?
Please provide the answer in the format [[output]].
</example 6>

<example 7>
Assuming a simple circuit diagram 
corresponding to the logical expression (p∧q)∨(¬p∧r), 
with inputs I1 as \"+\", I2 as \"-\", and I3 as \"+\", 
what is the output? 
Please provide the answer in the format [[output]].
</example 7>

<example 8>
Assuming a simple circuit diagram 
corresponding to the logical expression (p∧q)∨(¬p∧(q∨r)), 
with output O as \"+\", 
what are the corresponding inputs? 
Please provide multiple inputs that satisfy this condition in the format [[];[];…].
</example 8>

<example 9>
Assuming a simple circuit diagram 
corresponding to the logical expression (p∧q∧¬r)∨(¬p∧q)∨(p∨r), 
with output O as \"-\", 
what are the corresponding inputs? 
Please provide multiple inputs that satisfy this condition in the format [[];[];…].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
from itertools import product
from bootcamp import Basebootcamp

class KorLogicCircuitDiagrambootcamp(Basebootcamp):
    def __init__(self, gate_types=('NOT', 'AND', 'OR'), max_variables=4):
        self.gate_types = gate_types
        self.max_variables = max_variables
    
    def case_generator(self):
        import random
        problem_type = random.choice([
            'gate_truth_table',
            'compute_gate_output',
            'compute_expression_output',
            'find_inputs'
        ])
        
        if problem_type == 'gate_truth_table':
            return {
                'type': 'gate_truth_table',
                'gate': random.choice(self.gate_types)
            }
        
        elif problem_type == 'compute_gate_output':
            gate = random.choice(self.gate_types)
            num_inputs = 1 if gate == 'NOT' else 2
            return {
                'type': 'compute_gate_output',
                'gate': gate,
                'inputs': [random.choice(['+', '-']) for _ in range(num_inputs)],
                'powered': random.choice([True, False])
            }
        
        elif problem_type == 'compute_expression_output':
            expressions = [
                '¬p', 'p ∧ q', 'p ∨ q', '¬(p ∧ q)', '(p ∧ q) ∨ r',
                'p ∧ q ∧ ¬r', '(p ∨ q) ∧ ¬r', '¬p ∨ (q ∧ r)',
                '(p∧q)∨(¬p∧(q∨r))', '(p∧q∧¬r)∨(¬p∧q)∨(p∨r)'
            ]
            expr = random.choice(expressions)
            variables = self.extract_variables(expr)
            inputs = {var: random.choice(['+', '-']) for var in variables}
            return {
                'type': 'compute_expression_output',
                'expression': expr,
                'inputs': inputs,
                'powered': random.choice([True, False])
            }
        
        elif problem_type == 'find_inputs':
            expressions = [
                'p ∧ q', 'p ∨ q', '¬p', 'p ∧ q ∧ ¬r',
                '(p ∧ q) ∨ ¬r', '¬(p ∨ q) ∧ r',
                '(p∧q)∨(¬p∧(q∨r))', '(p∧q∧¬r)∨(¬p∧q)'
            ]
            expr = random.choice(expressions)
            variables = self.extract_variables(expr)
            return {
                'type': 'find_inputs',
                'expression': expr,
                'output': random.choice(['+', '-']),
                'powered': random.choice([True, False]),  # 修复点：允许非供电状态
                'variables': variables
            }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem_type = question_case.get('type')
        
        if problem_type == 'gate_truth_table':
            gate = question_case['gate']
            return (
                f"Provide the complete truth table for a {gate} gate. Format each row as:\n"
                "[[inputs], [powered_output, unpowered_output]].\n"
                "All input combinations must be included. Enclose the entire answer between [[ ]]."
            )
        
        elif problem_type == 'compute_gate_output':
            inputs = ', '.join([f"I{i+1}={val}" for i, val in enumerate(question_case['inputs'])])
            state = "when powered" if question_case['powered'] else "when unpowered"
            return (
                f"Given {inputs} in a {question_case['gate']} gate, what is the output {state}? "
                "Put your final answer within [[ ]]."
            )
        
        elif problem_type == 'compute_expression_output':
            inputs = ', '.join([f"{k}={v}" for k, v in question_case['inputs'].items()])
            state = "when powered" if question_case['powered'] else "when unpowered"
            return (
                f"For the logical expression: {question_case['expression']}\n"
                f"With inputs: {inputs}\n"
                f"What is the output {state}? Put your answer in [[ ]]."
            )
        
        elif problem_type == 'find_inputs':
            power_state = "when powered" if question_case['powered'] else "when unpowered"
            return (
                f"Find all possible input combinations {power_state} for:\n"
                f"Expression: {question_case['expression']}\n"
                f"That produce output: {question_case['output']}\n"
                f"Variables should be ordered as: {', '.join(question_case['variables'])}\n"
                "Format answer as [[val1,val2,...];...] within [[ ]]."
            )
        
        return "Invalid problem type"
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, flags=re.DOTALL)
        if matches:
            last_match = matches[-1].strip()
            return re.sub(r'\s+', '', last_match)  # 移除所有空白字符
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            problem_type = identity['type']
            
            if problem_type == 'gate_truth_table':
                return cls._verify_gate_table(solution, identity['gate'])
            
            elif problem_type == 'compute_gate_output':
                expected = cls._compute_gate_output(
                    identity['gate'],
                    identity['inputs'],
                    identity['powered']
                )
                return cls._sanitize_answer(solution) == expected
            
            elif problem_type == 'compute_expression_output':
                expected = cls._evaluate_expression(
                    identity['expression'],
                    identity['inputs'],
                    identity['powered']
                )
                return cls._sanitize_answer(solution) == expected
            
            elif problem_type == 'find_inputs':
                return cls._verify_input_combinations(
                    solution,
                    identity['expression'],
                    identity['output'],
                    identity['variables'],
                    identity['powered']
                )
            
            return False
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return False
    
    # Enhanced verification methods
    @classmethod
    def _verify_gate_table(cls, solution, gate):
        try:
            # 处理带换行的格式
            cleaned = solution.replace('\n', '').replace(' ', '')
            rows = [eval(r) for r in cleaned.split(';') if r]
            correct = cls._generate_gate_truth_table(gate)
            return rows == correct
        except SyntaxError:
            return False
    
    @classmethod
    def _verify_input_combinations(cls, solution, expr, target, variables, powered):
        try:
            # 解析所有可能的输入组合
            all_combos = set()
            for combo in product(['+', '-'], repeat=len(variables)):
                inputs = dict(zip(variables, combo))
                if cls._evaluate_expression(expr, inputs, powered) == target:
                    all_combos.add(tuple(combo))
            
            # 解析用户答案
            user_answers = set()
            for entry in solution.split(';'):
                entry = entry.strip("[] ")
                if not entry:
                    continue
                parts = [p.strip("'\" ") for p in entry.split(',')]
                if len(parts) != len(variables):
                    return False
                user_answers.add(tuple(parts))
            
            return user_answers == all_combos
        except Exception as e:
            print(f"Input verification error: {str(e)}")
            return False
    
    @staticmethod
    def _sanitize_answer(answer):
        """统一处理各种格式变体"""
        return answer.strip("[]'\" ").replace(' ', '').upper()
    
    @classmethod
    def _evaluate_expression(cls, expr, inputs, powered):
        """增强表达式解析"""
        if not powered:
            return '-'
        try:
            # 转换为Python表达式
            expr = (
                expr.replace('¬', ' not ')
                .replace('∧', ' and ')
                .replace('∨', ' or ')
                .replace('  ', ' ')
            )
            # 创建评估环境
            env = {k: v == '+' for k, v in inputs.items()}
            # 安全评估
            result = eval(expr, {'__builtins__': None}, env)
            return '+' if result else '-'
        except:
            return '-'
    
    @staticmethod
    def extract_variables(expr):
        """使用正则表达式精确提取变量"""
        return sorted(set(re.findall(r'\b[p-z]\b', expr)))
