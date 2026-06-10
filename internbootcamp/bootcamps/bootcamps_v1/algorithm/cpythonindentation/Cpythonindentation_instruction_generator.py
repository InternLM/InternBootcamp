import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpythonindentationInstructionGenerator(BaseInstructionGenerator):
    """Cpythonindentation Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10):
        """
        初始化Cpythonindentation指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if min_n < 1:
            raise ValueError("min_n must be at least 1")
        if max_n > 5000:
            raise ValueError("max_n cannot exceed 5000")
        self.min_n = max(1, min_n)
        self.max_n = min(5000, max(max_n, self.min_n))
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        commands = [random.choice(['f', 's']) for _ in range(n-1)]
        commands.append('s')  # Ensure last command is 's'
        return {
            'n': n,
            'commands': commands
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['n'])] + question_case['commands']
        input_example = '\n'.join(input_lines)
        prompt = f"""你是编程专家，需要解决一个关于Python缩进规则的谜题。请仔细阅读问题描述，并给出正确的答案。

问题描述：
在Python中，代码块由缩进定义，而没有显式的开始/结束符号。我们考虑一个极简化的Python子集，只有两种语句：简单语句（s）和for语句（f）。简单语句占据单独一行。for语句是复合语句，包含一个头部和一个循环体。循环体必须比for语句的头部缩进一级，且不能为空。

给定一个由's'和'f'组成的命令序列，最后一个命令一定是's'。你需要计算所有可能的有效缩进方式的数量，结果对10^9+7取模。

输入格式：
第一行包含整数N（命令数）。随后N行，每行是'f'或's'。

输出格式：
输出一个整数，表示有效方式数取模后的结果。

示例输入1：
4
s
f
f
s

示例输出1：
1

示例输入2：
4
f
s
f
s

示例输出2：
2

现在，请你解决以下输入案例：

输入：
{input_example}

请将你的最终答案放在[answer]标签内，例如：[answer]123[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

