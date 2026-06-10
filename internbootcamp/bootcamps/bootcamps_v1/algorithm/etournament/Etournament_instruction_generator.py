import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import bisect
import random
from typing import List
from typing import Optional

# === 源文件中的其他类 ===

class Node:
    def __init__(self, s_list):
        self.mx = s_list.copy()
        self.mn = s_list.copy()
        self.sz = 1
    
    def __lt__(self, other: 'Node') -> bool:
        for i in range(len(self.mn)):
            if self.mn[i] < other.mx[i]:
                return True
        return False
    
    def is_greater_than(self, other: 'Node') -> bool:
        for i in range(len(self.mx)):
            if self.mx[i] > other.mn[i]:
                return True
        return False


class EtournamentInstructionGenerator(BaseInstructionGenerator):
    """Etournament Bootcamp指令生成器"""
    
    def __init__(self, max_n=100, max_k=10):
        """
        初始化Etournament指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_k = max_k
    
    def case_generator(self) -> dict:
        n = random.randint(1, self.max_n)
        k = random.randint(1, min(self.max_k, 10))
        
        # Generate unique values for each sport
        athletes = []
        sport_values = []
        for j in range(k):
            values = random.sample(range(1, 10**9), n)
            sport_values.append(values)
        
        # Transpose to get athletes' stats
        athletes = [[sport_values[j][i] for j in range(k)] for i in range(n)]
        
        # Compute correct output
        correct_output = self._compute_correct_output(n, k, athletes)
        
        return {
            'n': n,
            'k': k,
            'athletes': athletes,
            'correct_output': correct_output
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = """你正在参加一个包含多种运动的锦标赛分析任务。请根据以下比赛数据，计算每年锦标赛可能的冠军人数。

输入格式：
第一行包含两个整数n和k，表示锦标赛的年数和运动种类数。
接下来n行，每行包含k个整数，表示第i年加入的运动员在各个运动中的能力值（保证同一运动的能力值唯一）。

输出格式：
输出n行，每行一个整数，表示对应年份可能的冠军人数。

题目数据：
n = {n}
k = {k}
运动员能力值：
{athletes}

请将你的答案放置在[answer]标签内，例如：
[answer]
1
2
3
[/answer]

你需要确保：
1. 严格按照输入数据计算正确结果
2. 输出格式与要求的完全一致
3. 将最终答案放在[answer]标签内""".format(
            n=question_case['n'],
            k=question_case['k'],
            athletes='\n'.join(' '.join(map(str, row)) for row in question_case['athletes'])
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _compute_correct_output(self, n: int, k: int, athletes: List[List[int]]) -> List[int]:
        nodes = []
        correct_output = []
        for s in athletes:
            tmp = Node(s)
            while True:
                pos = bisect.bisect_left(nodes, tmp)
                merged = False
                while pos > 0:
                    pos -= 1
                    current_node = nodes[pos]
                    if current_node.is_greater_than(tmp):
                        tmp.sz += current_node.sz
                        for j in range(k):
                            tmp.mn[j] = min(tmp.mn[j], current_node.mn[j])
                            tmp.mx[j] = max(tmp.mx[j], current_node.mx[j])
                        del nodes[pos]
                        merged = True
                        break
                    else:
                        break
                if not merged:
                    break
            bisect.insort(nodes, tmp)
            correct_output.append(nodes[-1].sz if nodes else 0)
        return correct_output
