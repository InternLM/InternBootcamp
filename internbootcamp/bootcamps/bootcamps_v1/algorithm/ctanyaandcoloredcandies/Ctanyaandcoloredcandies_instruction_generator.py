import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_candy_boxes(n, s, k, r_list, color_str):
    s -= 1  # 转换为0-based索引
    r = r_list
    color = color_str
    INF = float('inf')
    
    # 预处理最大可能的糖果数
    max_possible = sum(r)
    if max_possible < k:
        return -1
    
    # 动态规划数组，dp[cur][c]表示从cur出发，获得至少c颗糖果的最短时间
    dp = [[INF] * (k + 1) for _ in range(n)]
    
    # 预处理每个盒子自身的情况
    for i in range(n):
        current_max = min(r[i], k)
        for c in range(current_max + 1):
            dp[i][c] = 0  # 只需要吃当前盒子即可
        
    # 记忆化搜索函数
    def dfs(cur):
        # 已经处理过的情况直接返回
        if dp[cur][k] != INF:
            return
        
        # 尝试所有可能的后继盒子
        for to in range(n):
            if color[to] != color[cur] and r[to] > r[cur]:
                dfs(to)
                distance = abs(cur - to)
                
                # 状态转移：当前吃掉的糖果数 + 后续吃掉的糖果数
                for c in range(k, -1, -1):
                    if dp[cur][c] == INF:
                        continue
                    
                    # 计算转移后的糖果数
                    new_c = min(c + r[to], k)
                    cost = dp[cur][c] + distance
                    if cost < dp[to][new_c]:
                        dp[to][new_c] = cost
                        # 回溯更新所有可能的更优解
                        for nc in range(new_c, k+1):
                            if dp[to][nc] > cost:
                                dp[to][nc] = cost
    
    # 从每个可能的起点开始计算
    for i in range(n):
        dfs(i)
    
    # 计算最小时间
    min_time = INF
    for i in range(n):
        start_cost = abs(i - s)
        if start_cost + dp[i][k] < min_time:
            min_time = start_cost + dp[i][k]
    
    return min_time if min_time != INF else -1


class CtanyaandcoloredcandiesInstructionGenerator(BaseInstructionGenerator):
    """Ctanyaandcoloredcandies Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=15, min_r=1, max_r=20, min_k=5, max_k=200):
        """
        初始化Ctanyaandcoloredcandies指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_r: 参数描述
            max_r: 参数描述
            min_k: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_r = min_r
        self.max_r = max_r
        self.min_k = min_k
        self.max_k = max_k
    
    def case_generator(self):
        while True:
            n = random.randint(self.min_n, self.max_n)
            s = random.randint(1, n)
            r = [random.randint(self.min_r, self.max_r) for _ in range(n)]
            colors = ''.join(random.choice(['R', 'G', 'B']) for _ in range(n))
            total = sum(r)
            k = random.randint(self.min_k, min(total + 5, self.max_k))
            
            # 确保至少存在两种颜色的盒子
            if len(set(colors)) >= 2:
                return {
                    'n': n,
                    's': s,
                    'k': k,
                    'r': r,
                    'colors': colors
                }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['s']
        k = question_case['k']
        r = question_case['r']
        colors = question_case['colors']
        table = "\n| 盒子编号 | 糖果数量 | 颜色 |\n"
        table += "|:-:|:-:|:-:|\n"
        for i in range(n):
            table += f"| {i+1} | {r[i]} | {colors[i]} |\n"
        prompt = f"""## 糖果盒谜题

你面前有{n}个排列成行的糖果盒（编号1~{n}），初始位置在盒子{s}旁。每个盒子的信息如下：

{table}

### 规则说明
1. 每次可以移动到相邻盒子（耗时1秒）或吃光当前盒子的所有糖果（瞬间完成）
2. 连续吃的两个盒子颜色必须不同
3. 后吃的盒子糖果数必须严格大于前一个
4. 目标是通过移动和吃糖获得**至少{k}颗糖果**

请计算达成目标所需的最短时间（单位：秒），如果无法达成，请输出-1。

将最终答案放在[answer]和[/answer]之间，例如：[answer]5[/answer]或[answer]-1[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

