import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class CvotingInstructionGenerator(BaseInstructionGenerator):
    """Cvoting Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=200000, d_prob=0.5):
        """
        初始化Cvoting指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            d_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化投票训练场参数。

        参数:
            min_n (int): 最小员工数，默认1
            max_n (int): 最大员工数，默认200000
            d_prob (float): 生成D的概率，默认0.5
        """
        self.min_n = min_n
        self.max_n = max_n
        self.d_prob = d_prob
    
    def case_generator(self):
        """
        生成投票案例，包含随机员工序列和正确答案。
        """
        n = random.randint(self.min_n, self.max_n)
        sequence = ''.join(['D' if random.random() < self.d_prob else 'R' for _ in range(n)])
        correct_answer = self._solve_puzzle(n, sequence)
        return {
            'n': n,
            'sequence': sequence,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        生成包含详细规则和问题实例的提示文本。
        """
        n = question_case['n']
        sequence = question_case['sequence']
        return f"""你是Alternative Cake Manufacturing (ACM)的投票结果预测专家。公司有{n}名员工正在就一个重要问题进行投票，他们的投票顺序和所属派系如下：每位员工按顺序依次属于派系{sequence}（第i个字符代表第i位员工的派系，D代表depublicans，R代表remocrats）。

投票规则如下：
1. 投票过程分为多轮进行。每一轮中，未被淘汰的员工按照初始顺序依次发言。
2. 每位员工在发言时，可以选择淘汰对方派系的下一个即将发言的成员，或者不采取行动。
3. 当员工被淘汰后，将不再参与后续的投票过程。
4. 此过程重复进行，直到只剩下一名员工未被淘汰，该员工所属的派系将赢得投票。
5. 所有员工都将采取最优策略，即优先淘汰对方派系的下一个可能发言者以确保己方胜利。

请预测最终的投票结果，即胜利方是D还是R？请将最终答案严格放置在[answer]标签内，例如[answer]D[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _solve_puzzle(n, sequence):
        """
        准确复现参考代码逻辑的解答方法。
        """
        dq = deque()
        rq = deque()
        for i, c in enumerate(sequence):
            if c == 'D':
                dq.append(i)
            else:
                rq.append(i)

        while dq and rq:
            for i in range(n):
                if not (dq and rq):
                    break
                if sequence[i] == 'D' and i == dq[0]:
                    if dq and rq:
                        rq.popleft()
                        dq.popleft()
                elif sequence[i] == 'R' and i == rq[0]:
                    if dq and rq:
                        dq.popleft()
                        rq.popleft()

        return 'D' if dq else 'R'
