import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class DprogramminglanguageInstructionGenerator(BaseInstructionGenerator):
    """Dprogramminglanguage Bootcamp指令生成器"""
    
    def __init__(self, max_procedures=10, max_variables=10, max_calls=10, procedure_name_length=5, var_name_length=5, t_probability=0.3):
        """
        初始化Dprogramminglanguage指令生成器
        
        Args:
            max_procedures: 参数描述
            max_variables: 参数描述
            max_calls: 参数描述
            procedure_name_length: 参数描述
            var_name_length: 参数描述
            t_probability: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_procedures = max_procedures
        self.max_variables = max_variables
        self.max_calls = max_calls
        self.procedure_name_length = procedure_name_length
        self.var_name_length = var_name_length
        self.t_probability = t_probability
    
    def case_generator(self):
        def generate_name(length, prefix=''):
            chars = string.ascii_lowercase + string.digits
            return prefix + ''.join(random.choice(chars) for _ in range(length))
        
        # 生成变量
        m = random.randint(1, self.max_variables)
        variables = {}
        for _ in range(m):
            while True:
                var_name = generate_name(self.var_name_length, 'var_')
                if var_name not in variables:
                    break
            variables[var_name] = random.choice(['int', 'string', 'double'])
        
        # 生成调用时确保部分调用有匹配过程
        k = random.randint(1, self.max_calls)
        calls = []
        for _ in range(k):
            # 生成调用时，参数数量关联过程参数
            call_name = generate_name(self.procedure_name_length) if random.random() < 0.3 else None
            params_count = random.randint(1, 5)
            available_vars = list(variables.keys())
            vars_list = [random.choice(available_vars) for _ in range(params_count)] if available_vars else []
            calls.append({'name': call_name, 'vars': vars_list})
        
        # 生成过程，部分针对调用生成
        existing_procedures = set()
        procedures = []
        
        # 随机生成基础过程
        base_procedure_count = random.randint(0, self.max_procedures)
        for _ in range(base_procedure_count):
            name = generate_name(self.procedure_name_length)
            params_count = random.randint(1, 5)
            params = []
            for _ in range(params_count):
                if random.random() < self.t_probability:
                    param = 'T'
                else:
                    param = random.choice(['int', 'string', 'double'])
                params.append(param)
            key = (name, tuple(params))
            if key not in existing_procedures:
                existing_procedures.add(key)
                procedures.append({'name': name, 'params': params})
        
        # 为部分调用生成匹配过程
        for call in calls:
            if call['name'] is None or random.random() > 0.6:
                continue  # 不处理未命名调用或随机跳过
            var_types = [variables[var] for var in call['vars']]
            # 生成匹配参数类型的过程
            for _ in range(random.randint(0, 2)):  # 每个调用生成0-2个匹配过程
                params = []
                for t in var_types:
                    if random.random() < self.t_probability:
                        params.append('T')
                    else:
                        params.append(t)
                key = (call['name'], tuple(params))
                if key not in existing_procedures:
                    existing_procedures.add(key)
                    procedures.append({'name': call['name'], 'params': params})
        
        # 最终确保过程名称多样性
        procedure_names = list({proc['name'] for proc in procedures})
        for call in calls:
            if call['name'] is None and procedure_names:
                call['name'] = random.choice(procedure_names)
        
        return {
            'procedures': procedures,
            'variables': variables,
            'calls': calls
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = []
        input_lines.append(str(len(question_case['procedures'])))
        for proc in question_case['procedures']:
            # 模拟输入空格
            spaces_before = ' ' * random.randint(0, 2)
            spaces_after = ' ' * random.randint(0, 2)
            params = [f"{' ' * random.randint(0,1)}{p}{' ' * random.randint(0,1)}" for p in proc['params']]
            input_lines.append(f"void{spaces_before}{proc['name']}{spaces_after}({','.join(params)})".replace(' ', ' '))
        input_lines.append(str(len(question_case['variables'])))
        for var_name, var_type in question_case['variables'].items():
            input_lines.append(f"{var_type}{' ' * random.randint(1,3)}{var_name}")
        input_lines.append(str(len(question_case['calls'])))
        for call in question_case['calls']:
            spacer = ' ' * random.randint(0, 2)
            params = [f"{spacer}{var}{spacer}" for var in call['vars']]
            input_lines.append(f"{call['name']}({','.join(params)})")
        input_example = '\n'.join(input_lines)
        
        prompt = f"""你是编程竞赛的参赛者，需要解决一个关于模板过程调用的问题。请仔细阅读问题描述，并按照要求输出答案。

问题描述：

给定一组模板过程、变量列表和一系列过程调用，对于每个调用，统计有多少个模板过程适合该调用。

模板过程的条件如下：
1. 名称与调用名称相同。
2. 参数数量相同。
3. 每个参数的类型为T或者与实际变量类型相同。

输入格式：
- 第一行是整数n，表示模板过程的数量。
- 接下来的n行，每行描述一个模板过程，格式为："void 过程名 (参数类型列表)"，参数类型可以是int、string、double或T。
- 接下来一行是整数m，表示变量的数量。
- 接下来的m行，每行描述一个变量，格式为："类型 变量名"，类型是int、string、double中的一个。
- 接下来一行是整数k，表示调用的数量。
- 接下来的k行，每行描述一个调用，格式为："过程名 (变量列表)"。

输出格式：
输出k行，每行是对应调用的适合模板过程的数量。

请根据以下输入数据，编写程序解决问题。将你的答案放在[answer]标签内，每个结果占一行。

输入数据：
{input_example}

请将答案按顺序放在[answer]和[/answer]标签之间，例如：
[answer]
0
1
2
[/answer]

请确保你的输出格式正确，否则将无法得到分数。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

