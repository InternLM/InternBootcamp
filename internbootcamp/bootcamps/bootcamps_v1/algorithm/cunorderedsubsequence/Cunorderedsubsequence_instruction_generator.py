import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CunorderedsubsequenceInstructionGenerator(BaseInstructionGenerator):
    """Cunorderedsubsequence Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cunorderedsubsequence指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)  # 默认n为5
        self.min_n = params.get('min_n', 3)  # 最小n为3
        self.max_n = params.get('max_n', 1000)  # 最大n为1000
    
    def case_generator(self):
        while True:
            n = random.randint(self.min_n, self.max_n)
            # 确保n至少为3
            n = max(n, self.min_n)
            # 生成初始有序序列，递增或递减的概率各占一半
            if random.choice([True, False]):
                sequence = list(range(1, n + 1))
            else:
                sequence = list(range(n, 0, -1))
            
            # 随机选择一个位置i，确保在有效范围内
            i = random.randint(0, n - 3)
            # 判断当前序列是递增还是递减
            if sequence[i] < sequence[i + 1]:
                # 递增，形成一个峰
                new_val = sequence[i + 1] + random.randint(1, 100)
                sequence[i + 1] = new_val
            else:
                # 递减，形成一个谷
                new_val = sequence[i + 1] - random.randint(1, 100)
                sequence[i + 1] = new_val
            
            # 压缩序列，处理相同元素
            s = []
            for idx, num in enumerate(sequence):
                if not s or s[-1][1] != num:
                    s.append((idx + 1, num))  # 使用1-based索引
            
            # 检查是否有三元组
            correct_length = 0
            correct_indices = []
            for j in range(1, len(s) - 1):
                a, b, c = s[j - 1][1], s[j][1], s[j + 1][1]
                if (a < b and b > c) or (a > b and b < c):
                    correct_length = 3
                    correct_indices = [s[j - 1][0], s[j][0], s[j + 1][0]]
                    break
            if correct_length == 3:
                # 记录正确答案
                case = {
                    "sequence": sequence,
                    "n": n,
                    "correct_answer_length": correct_length,
                    "correct_answer_indices": correct_indices
                }
                return case
            else:
                # 继续生成，直到找到一个有解的序列
                continue
    
    @staticmethod
    def prompt_func(question_case):
        sequence = question_case['sequence']
        n = question_case['n']
        prompt = f"""你是一个聪明的解谜者，请解决以下问题：

给定一个长度为{n}的数字序列：
{sequence}

你的任务是找到其中最短的无序子序列。无序子序列指的是既不是非递增也不是非递减的子序列。子序列可以通过删除一些元素得到，但顺序必须保持不变。

规则说明：
1. 如果整个序列是有序的（非递增或非递减），则输出0。
2. 否则，输出最短无序子序列的长度k，接着输出k个元素的索引（1-based）。
3. 如果有多个解，输出任意一个即可。

例如：
输入：
5
67 499 600 42 23

输出：
3
1 3 5

请将答案放在[answer]标签中，格式如下：
如果无解，输出：
[answer]
0
[/answer]

否则，输出：
[answer]
3
1 3 5
[/answer]

现在，请解决以下问题：

给定序列：{sequence}

输出格式：
[answer]
...
[/answer]
"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

