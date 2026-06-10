import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class AmrkitayutathetreasurehunterInstructionGenerator(BaseInstructionGenerator):
    """Amrkitayutathetreasurehunter Bootcamp指令生成器"""
    
    def __init__(self, max_n=100, max_d=30000, **params):
        """
        初始化Amrkitayutathetreasurehunter指令生成器
        
        Args:
            max_n: 参数描述
            max_d: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_n = min(max_n, 30000)
        self.max_d = min(max_d, 30000)
        self.max_island = 30000
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        d = random.randint(1, self.max_d)
        gems = []
        # Ensure valid gem distribution with at least one gem >=d
        base = random.randint(d, self.max_island - 50) if d < self.max_island else d
        spreads = sorted(random.sample(range(base, self.max_island + 1), k=min(n, self.max_island - base + 1)))
        gems = [random.choice(spreads) for _ in range(n)]
        gems.sort()
        correct_answer = self.calculate_max_gems(n, d, gems)
        return {
            'n': n,
            'd': d,
            'gems': gems,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        gems = sorted(question_case['gems'])
        gems_str = '\n'.join(map(str, gems))
        prompt = f"""在Shuseki群岛寻宝问题中，Kitayuta先生从岛0出发，首次跳跃到岛{question_case['d']}。之后每次跳跃长度可为前次±1或相同（必须>0），直到无法继续跳跃。求他能收集的宝石最大数量。

输入参数：
- 宝石总数 n = {question_case['n']}
- 初始跳跃距离 d = {question_case['d']}
- 按非降序排列的宝石位置：
{gems_str}

请计算最大可收集宝石数量，并将最终答案置于[answer]标签内，例如：[answer]5[/answer]。注意岛屿编号上限为30000，跳跃长度必须始终为正。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_max_gems(n, d, gems):
        cnt = defaultdict(int)
        for p in gems:
            cnt[p] += 1

        MX = 30000
        max_offset = 260
        dp = [[-1] * (2*max_offset + 1) for _ in range(MX + 1)]
        initial_pos = d

        if initial_pos > MX:
            return 0
        dp[initial_pos][max_offset] = cnt[initial_pos]
        ans = cnt[0] + dp[initial_pos][max_offset]  # Include starting position

        for pos in range(initial_pos, MX + 1):
            for offset in range(2*max_offset + 1):
                if dp[pos][offset] == -1:
                    continue
                current_len = d + (offset - max_offset)
                for dl in (-1, 0, 1):
                    new_len = current_len + dl
                    if new_len <= 0:
                        continue
                    next_pos = pos + new_len
                    if next_pos > MX:
                        continue
                    new_offset = offset + dl
                    if 0 <= new_offset <= 2*max_offset:
                        total = dp[pos][offset] + cnt[next_pos]
                        if total > dp[next_pos][new_offset]:
                            dp[next_pos][new_offset] = total
                            ans = max(ans, total)
        return ans
