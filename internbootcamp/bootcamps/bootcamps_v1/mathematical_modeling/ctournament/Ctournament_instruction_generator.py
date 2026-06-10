import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from bisect import bisect_left
from bisect import insort




class CtournamentInstructionGenerator(BaseInstructionGenerator):
    """Ctournament Bootcamp指令生成器"""
    
    def __init__(self, n=3, k=2):
        """
        初始化Ctournament指令生成器
        
        Args:
            n: 参数描述
            k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.k = k
    
    def case_generator(self):
        n, k = self.n, self.k
        sportsmen = []
        # Generate unique values for each sport
        for _ in range(k):
            base = random.randint(1, 10**9)
            step = random.choice([1, 10, 100])
            values = [base + i*step for i in random.sample(range(10**5), n)]
            sportsmen.append(values)
        
        # Transpose to get player stats
        players = list(zip(*sportsmen))
        
        return {
            'n': n,
            'k': k,
            'sportsmen': players,
            'answers': self.calculate_answers(players, k)
        }
    
    @staticmethod
    def prompt_func(case):
        prompt = [
            "体育锦标赛分析任务：",
            f"共有 {case['n']} 届锦标赛，每届新增1名选手，需计算每届可能的冠军数量。",
            "规则要点：",
            "1. 每场比赛可任选运动类型进行较量",
            "2. 高能力值选手必胜低能力值选手",
            "3. 最后剩下的选手获胜",
            "选手能力矩阵："
        ]
        for i, stats in enumerate(case['sportsmen']):
            prompt.append(f"第{i+1}年选手: {' '.join(map(str, stats))}")
        
        prompt.append("请输出每届可能的冠军数量，格式：\n[answer]1 2 3[/answer]")
        return '\n'.join(prompt) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answers(players, k):
        class Node:
            __slots__ = ['mx', 'mn', 'siz']
            def __init__(self, stats):
                self.mx = list(stats)
                self.mn = list(stats)
                self.siz = 1
            def __lt__(self, other):
                return all(a <= b for a, b in zip(self.mx, other.mn))

        nodes = []
        answers = []
        for stats in players:
            current = Node(stats)
            while True:
                # Find merge candidates using bisect
                idx = bisect_left(nodes, current)
                merged = False

                # Check left neighbor
                if idx > 0 and current < nodes[idx-1]:
                    candidate = nodes.pop(idx-1)
                    current.siz += candidate.siz
                    current.mx = [max(a,b) for a,b in zip(current.mx, candidate.mx)]
                    current.mn = [min(a,b) for a,b in zip(current.mn, candidate.mn)]
                    merged = True

                # Check right neighbor
                if idx < len(nodes) and current < nodes[idx]:
                    candidate = nodes.pop(idx)
                    current.siz += candidate.siz
                    current.mx = [max(a,b) for a,b in zip(current.mx, candidate.mx)]
                    current.mn = [min(a,b) for a,b in zip(current.mn, candidate.mn)]
                    merged = True

                if not merged: break

            insort(nodes, current)
            answers.append(nodes[-1].siz)
        return answers
