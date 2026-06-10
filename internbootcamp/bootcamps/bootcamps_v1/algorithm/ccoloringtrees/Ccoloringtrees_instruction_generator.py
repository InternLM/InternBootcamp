import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
import re

# === 源文件中的全局函数 ===

def solve(n, m, k, c_list, p_matrix):
    INF = 10**18
    c = c_list
    p = p_matrix

    # DP优化算法实现
    dp = [[INF]*(m+1) for _ in range(k+1)]
    dp[0][0] = 0  # 初始状态
    
    for tree_idx in range(n):
        current_color = c[tree_idx]
        new_dp = [[INF]*(m+1) for _ in range(k+1)]
        
        for groups in range(k+1):
            for prev_color in range(m+1):
                if dp[groups][prev_color] == INF:
                    continue
                
                for new_color in range(1, m+1):
                    if current_color != 0 and current_color != new_color:
                        continue  # 已染色树不能改变颜色
                    
                    # 计算新分组数
                    new_groups = groups + (1 if new_color != prev_color else 0)
                    if new_groups > k:
                        continue
                    
                    # 计算成本
                    cost = p[tree_idx][new_color-1] if current_color == 0 else 0
                    
                    new_dp[new_groups][new_color] = min(
                        new_dp[new_groups][new_color],
                        dp[groups][prev_color] + cost
                    )
        
        dp = new_dp

    min_cost = min(dp[k][color] for color in range(1, m+1))
    return min_cost if min_cost < INF else -1


class CcoloringtreesInstructionGenerator(BaseInstructionGenerator):
    """Ccoloringtrees Bootcamp指令生成器"""
    
    def __init__(self, max_n=50, max_m=20, **kwargs):
        """
        初始化Ccoloringtrees指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        # 生成有效案例逻辑优化
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        k = random.randint(1, min(n, 20))  # 限制k的范围
        
        # 生成颜色，确保至少有一个未染色树（当需要染色时）
        c = []
        for _ in range(n):
            if random.random() < 0.3:
                c.append(0)
            else:
                c.append(random.randint(1, m))
        
        # 生成油漆成本矩阵
        p = [[random.randint(1, 1000) for _ in range(m)] for _ in range(n)]
        
        # 计算正确答案
        ans = solve(n, m, k, c, p)
        return {
            "n": n,
            "m": m,
            "k": k,
            "c": c,
            "p": p,
            "ans": ans
        }
    
    @staticmethod
    def prompt_func(case):
        # 修正的字符串格式化方法
        prompt = f"""ZS the Coder和Chris the Baboon需要给公园里的树染色。现有{case['n']}棵树排成一列，每棵树初始颜色为0（未染色）或1~{case['m']}。要求将所有未染色的树染色，使得最终染色方案的美丽值恰好为{case['k']}（美丽值定义为将树划分为连续同色组的最小数量），求最小油漆用量。

输入格式：
- 第一行三个整数n m k
- 第二行n个整数表示初始颜色
- 接下来n行每行m个整数表示染色花费

当前问题：
第一行：{case['n']} {case['m']} {case['k']}
第二行：{' '.join(map(str, case['c']))}
"""
        # 添加油漆成本矩阵
        prompt += "\n" + "\n".join(' '.join(map(str, row)) for row in case['p'])
        prompt += "\n请计算最小油漆用量（若无解输出-1），将最终答案放在[answer]标签内，例如：[answer]-1[/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

