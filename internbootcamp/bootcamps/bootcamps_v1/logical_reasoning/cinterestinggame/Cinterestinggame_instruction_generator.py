import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CinterestinggameInstructionGenerator(BaseInstructionGenerator):
    """Cinterestinggame Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100000):
        """
        初始化Cinterestinggame指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        correct_answer = self._solve(n)
        return {"n": n, "correct_answer": correct_answer}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        prompt = f"""你是石子游戏专家，请解决以下问题：

游戏规则：
1. 初始有一堆石子，共{n}个。
2. 玩家轮流操作，每次操作必须选择一堆石子，并将其分成k堆（k≥2），且满足各堆石子数目严格递减且相邻两堆数目差为1。
3. 无法操作的玩家输。Serozha先手，两人都采取最优策略。

你的任务：确定Serozha是否能赢。若赢，输出他第一次分割的最小k值；否则输出-1。

输入格式：整数n={n}

输出格式：答案放在[answer]和[/answer]之间，例如[answer]2[/answer]。

请仔细思考，给出正确的答案。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _solve(n):
        if n == 1:
            return -1

        spg = [0] * (n + 1)
        xor = [0] * (n + 1)

        for i in range(3, n + 1):
            movs = set()
            k = 2
            while k * (k + 1) <= 2 * i:
                s = 2 * i + k * (k - 1)
                if s % (2 * k) == 0:
                    a = s // (2 * k)
                    if a >= k:  # 确保分割后的堆数满足严格递减条件
                        xor_total = xor[a] ^ xor[a - k]
                        movs.add(xor_total)
                k += 1

            mex = 0
            while mex in movs:
                mex += 1
            spg[i] = mex
            xor[i] = xor[i - 1] ^ spg[i]

        if spg[n] == 0:
            return -1
        else:
            min_k = None
            k = 2
            while k * (k + 1) <= 2 * n:
                s = 2 * n + k * (k - 1)
                if s % (2 * k) == 0:
                    a = s // (2 * k)
                    if a >= k:
                        xor_total = xor[a] ^ xor[a - k]
                        if xor_total == 0:
                            min_k = k
                            break
                k += 1
            return min_k if min_k is not None else -1
