import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from heapq import heapify
from heapq import heappop
from heapq import heappush




class CswapsInstructionGenerator(BaseInstructionGenerator):
    """Cswaps Bootcamp指令生成器"""
    
    def __init__(self, n_range=(1, 10), s_range=(1, 20)):
        """
        初始化Cswaps指令生成器
        
        Args:
            n_range: 参数描述
            s_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = n_range
        self.s_range = s_range
    
    def case_generator(self):
        n = random.randint(*self.n_range)
        s = random.randint(*self.s_range)
        a = self.generate_a(n, s)
        possible = self.check_possible(n, s, a)
        return {'n': n, 's': s, 'a': a, 'possible': possible}
    
    @staticmethod
    def prompt_func(case):
        n = case['n']
        s = case['s']
        a = case['a']
        problem_text = (
            f"有 {n} 个玩家围坐在圆桌旁，初始时每个玩家拥有特定颜色的卡牌。玩家可以按照以下规则交换卡牌：\n"
            "1. 每次交换必须是一对玩家互相交换\n"
            "2. 每个玩家只能给出自己初始颜色的卡牌\n"
            "3. 玩家不能接受自己已拥有颜色的卡牌（包括初始颜色）\n"
            "目标：所有玩家通过若干次交换后，必须给出自己所有的初始颜色卡牌。\n\n"
            "输入格式：\n"
            "第一行两个整数 n 和 s（玩家数量和初始卡牌总数）\n"
            "第二行 n 个整数表示每个玩家的初始卡牌数\n\n"
            "当前问题实例：\n"
            f"{n} {s}\n"
            f"{' '.join(map(str, a))}\n\n"
            "请判断是否存在合法交换方案。若存在，输出'Yes'并给出交换步骤；否则输出'No'。\n"
            "答案请用[answer]标签包裹，示例：\n"
            "[answer]\nYes\n3\n1 2\n2 3\n3 1\n[/answer]"
        )
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_a(n, s):
        if n == 0:
            return []
        a = [0] * n
        total = 0
        for i in range(n-1):
            max_assign = s - total
            a[i] = random.randint(0, max_assign)
            total += a[i]
        a[-1] = s - total
        return a

    @staticmethod
    def check_possible(n, s, a):
        q = [(-x, i) for i, x in enumerate(a) if x > 0]
        heapify(q)
        try:
            while q:
                x, i = heappop(q)
                if -x > len(q):
                    return False
                partners = []
                for _ in range(-x):
                    if not q:
                        return False
                    partners.append(heappop(q))
                for y, j in partners:
                    if y + 1 != 0:
                        heappush(q, (y + 1, j))
            return True
        except:
            return False
