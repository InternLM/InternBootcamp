import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from itertools import groupby
import re




class DomkarandbedwarsInstructionGenerator(BaseInstructionGenerator):
    """Domkarandbedwars Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=20):
        """
        初始化Domkarandbedwars指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，确保n ≥ 3
        参数:
            min_n (int): 最小玩家数 ≥3
            max_n (int): 最大玩家数
        """
        assert min_n >= 3, "玩家数至少为3"
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        """生成合法测试用例及预计算答案"""
        n = random.randint(self.min_n, self.max_n)
        # 生成有效攻击序列
        s = []
        for _ in range(n):
            s.append(random.choice(['L', 'R']))
        s = ''.join(s)
        
        # 正确解法逻辑
        if all(c == s[0] for c in s):
            ans = (n + 2) // 3
        else:
            groups = []
            for k, grp in groupby(s):
                groups.append( (k, sum(1 for _ in grp)) )
            
            # 合并循环相同段
            if len(groups) > 1 and groups[0][0] == groups[-1][0]:
                groups[0] = (groups[0][0], groups[0][1] + groups[-1][1])
                groups.pop()
            
            ans = sum( cnt // 3 for _, cnt in groups )
        
        return {
            'n': n,
            's': s,
            'correct_answer': ans
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        """生成详细规则描述的问题模板"""
        return f"""## Bed Wars策略分析

**游戏配置**
- 玩家总数：{case['n']}
- 攻击方向序列：`{case['s']}`（索引从1开始，L/R表示攻击方向）

**策略规则**
1. 玩家被1人攻击时必须反击攻击者
2. 被0或2人攻击时可自由选择攻击方向
3. 每次转换可改变一个玩家的攻击方向

**任务**
计算使得所有玩家符合策略的最小转换次数，将最终数字包裹在[answer]标签内，如：[answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

