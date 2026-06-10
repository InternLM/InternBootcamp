import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random

# === 源文件中的全局函数 ===

def solve(n, p_list, x, a, y, b, k):
    arr = sorted(p_list, reverse=True)
    # 确保x是较大值并交换参数
    if y > x:
        x, y = y, x
        a, b = b, a
    
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a
    
    g = gcd(a, b)
    lcm_ab = (a * b) // g if g != 0 else 0
    lo = 0
    hi = n
    
    while lo < hi:
        mid = (lo + hi) // 2
        cnt1 = mid // lcm_ab if lcm_ab != 0 else 0
        cnt2 = mid // a - cnt1
        cnt3 = mid // b - cnt1
        
        total = 0
        ind = 0
        # 处理x+y%的贡献
        for _ in range(cnt1):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * (x + y)
            ind += 1
        # 处理x%的贡献
        for _ in range(cnt2):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * x
            ind += 1
        # 处理y%的贡献
        for _ in range(cnt3):
            if ind >= len(arr):
                break
            total += arr[ind] // 100 * y
            ind += 1
        
        if total >= k:
            hi = mid
        else:
            lo = mid + 1
    
    return lo if lo <= n else -1  # 移除多余验证


class AsavethenatureInstructionGenerator(BaseInstructionGenerator):
    """Asavethenature Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=20, p_min=1, p_max=1000, k_gen_strategy='mixed'):
        """
        初始化Asavethenature指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            p_min: 参数描述
            p_max: 参数描述
            k_gen_strategy: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.p_min = p_min  # 100的倍數基數
        self.p_max = p_max
        self.k_gen_strategy = k_gen_strategy
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        p = [random.randint(self.p_min, self.p_max) * 100 for _ in range(n)]
        
        # 生成合法的x,y參數
        s = random.randint(2, 100)
        x = random.randint(1, s-1)
        y = s - x
        
        # 修正：允許a,b在完整範圍隨機
        a = random.randint(1, n)
        b = random.randint(1, n)
        
        # 重要：保持與solve函數相同的參數交換邏輯
        if y > x:
            x, y = y, x
            a, b = b, a
        
        # 計算真實最大值
        sorted_p = sorted(p, reverse=True)
        g = math.gcd(a, b)
        lcm_ab = (a * b) // g if g != 0 else 0
        
        max_total = 0
        ind = 0
        # 計算使用全部票的最大貢獻
        for cnt in [n//lcm_ab, (n//a)-n//lcm_ab, (n//b)-n//lcm_ab]:
            take = min(cnt, len(sorted_p)-ind)
            if cnt == n//lcm_ab:
                rate = x + y
            elif cnt == (n//a)-n//lcm_ab:
                rate = x
            else:
                rate = y
            max_total += sum(sorted_p[ind:ind+take]) // 100 * rate
            ind += take
        
        # 生成k時考慮策略
        if self.k_gen_strategy == 'mixed':
            base = max(1, max_total)
            k = random.randint(1, base * 2)
        elif self.k_gen_strategy == 'solvable':
            k = random.randint(1, max_total) if max_total > 0 else 1
        elif self.k_gen_strategy == 'unsolvable':
            k = max_total + random.randint(1, 1000)
        else:
            raise ValueError("Invalid strategy")
        
        return {
            'n': n,
            'p': p,
            'x': x,
            'a': a,
            'y': y,
            'b': b,
            'k': k,
        }
    
    @staticmethod
    def prompt_func(question_case):
        params = question_case
        problem_desc = (
            "作为电影院售票员兼环保主义者，你需要优化票券销售顺序以达到环保筹款目标。\n\n"
            "**参数说明**\n"
            f"- 可售票据：{params['n']} 张，价格分别为（单位元）{params['p']}\n"
            f"- 环保项目1：每售出第 {params['a']}、{2*params['a']}... 张票时，贡献票价的 {params['x']}%\n"
            f"- 环保项目2：每售出第 {params['b']}、{2*params['b']}... 张票时，贡献票价的 {params['y']}%\n"
            "**叠加规则**：若同一张票同时符合两个项目（如第 {lcm} 张），则贡献率叠加".format(
                lcm=(params['a']*params['b']//math.gcd(params['a'], params['b']))
            ) + "\n\n"
            f"**目标**：通过调整售票顺序，使得用最少的售票数量达到至少 {params['k']} 元的环保捐款。\n"
            "**输出**：最少需要的售票数（如无法达到则返回 -1），答案请包裹在[answer][/answer]标签中。"
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

