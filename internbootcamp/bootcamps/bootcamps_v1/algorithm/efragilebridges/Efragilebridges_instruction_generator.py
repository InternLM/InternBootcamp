import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve(n_platforms, a):
    """动态规划解法，包含完整边界校验"""
    if n_platforms < 2:
        return 0
    if len(a) != n_platforms - 1:
        raise ValueError("Bridge count mismatch")
    
    n = n_platforms - 1
    x = a.copy()
    
    # 右侧DP初始化
    r = [[0, 0] for _ in range(n_platforms)]
    for i in range(n-1, -1, -1):
        # 计算r[i][1]
        if x[i] == 1:
            r[i][1] = 0
        else:
            next_i = i + 1
            r_next_1 = r[next_i][1] if next_i < n_platforms else 0
            sum_val = r_next_1 + x[i]
            r[i][1] = sum_val & (~1)
        
        # 计算r[i][0]
        next_i = i + 1
        r_next_0 = r[next_i][0] if next_i < n_platforms else 0
        if x[i] % 2 == 1:
            r[i][0] = max(r[i][1], x[i] + r_next_0)
        else:
            r[i][0] = max(r[i][1], (x[i]-1) + r_next_0)
    
    # 左侧DP初始化
    l = [[0, 0] for _ in range(n_platforms)]
    for i in range(1, n_platforms):
        bridge_idx = i-1
        if bridge_idx < 0:
            continue
            
        x_val = x[bridge_idx]
        # 计算l[i][1]
        if x_val == 1:
            l[i][1] = 0
        else:
            prev_i = i-1
            l_prev_1 = l[prev_i][1] if prev_i >= 0 else 0
            sum_val = l_prev_1 + x_val
            l[i][1] = sum_val & (~1)
        
        # 计算l[i][0]
        prev_i = i-1
        l_prev_0 = l[prev_i][0] if prev_i >= 0 else 0
        if x_val % 2 == 1:
            l[i][0] = max(l[i][1], x_val + l_prev_0)
        else:
            l[i][0] = max(l[i][1], (x_val-1) + l_prev_0)
    
    # 计算最大值
    max_score = 0
    for i in range(n_platforms):
        current = r[i][0] + l[i][0]
        max_score = max(max_score, current)
    return max_score


class EfragilebridgesInstructionGenerator(BaseInstructionGenerator):
    """Efragilebridges Bootcamp指令生成器"""
    
    def __init__(self, max_platforms=1e5, max_bridge=1e9):
        """
        初始化Efragilebridges指令生成器
        
        Args:
            max_platforms: 参数描述
            max_bridge: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_platforms = min(int(max_platforms), 100000)
        self.max_bridge = min(int(max_bridge), 10**18)
    
    def case_generator(self):
        # 智能生成测试案例（含边界值）
        platform_choices = [
            2,  # 最小有效值
            3,  # 小奇数平台
            random.randint(4, 100),  # 普通小案例
            self.max_platforms  # 最大规模测试
        ]
        n_platforms = random.choices(
            platform_choices,
            weights=[0.15, 0.15, 0.3, 0.4],
            k=1
        )[0]
        
        # 桥的生成策略
        bridge_patterns = [
            lambda: 1,  # 边界情况
            lambda: 2,  # 偶数基础
            lambda: random.choice([3,5,7]),  # 小奇数
            lambda: random.randint(10, 1000),  # 随机中等数
            lambda: self.max_bridge  # 极值测试
        ]
        a = [random.choice(bridge_patterns)() for _ in range(n_platforms-1)]
        
        return {
            'n': n_platforms,
            'a': a,
            'expected': solve(n_platforms, a)
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""游戏奖励关卡计算问题

关卡配置：
- 平台总数：{question_case['n']}
- 桥耐久值：{' '.join(map(str, question_case['a']))}

移动规则：
1. 选择任意起始平台
2. 每次移动消耗桥的耐久值
3. 无法移动时统计总移动次数

计算要求：
1. 找出绝对最大值
2. 考虑所有可能路径
3. 结果需为整数

答案格式：
将最终结果放在[answer]标签内，例如：[answer]42[/answer]

当前测试输入：
{question_case['n']}
{' '.join(map(str, question_case['a']))}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

