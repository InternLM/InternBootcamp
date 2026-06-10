import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CjohnnyandanotherratingdropInstructionGenerator(BaseInstructionGenerator):
    """Cjohnnyandanotherratingdrop Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10**18, seed=None):
        """
        初始化Cjohnnyandanotherratingdrop指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.rng = random.Random(seed)
    
    def case_generator(self):
        # 生成策略优化：70%普通随机数，20%边界值，10%特殊模式
        if self.rng.random() < 0.7:
            n = self.rng.randint(self.min_n, self.max_n)
        elif self.rng.random() < 0.5:
            n = self.rng.choice([self.min_n, self.max_n])
        else:
            # 生成全1模式或2^k模式
            bits = self.rng.randint(1, 60)
            n = (1 << bits) - 1 if self.rng.random() < 0.5 else (1 << bits)
            n = min(max(n, self.min_n), self.max_n)
        return {"n": n}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["n"]
        return f"""## 编程竞赛不公平性计算问题

**任务背景**：
给定从0到{n}的连续整数序列（共{n+1}个数），计算所有相邻数对的二进制差异总和。

**规则说明**：
1. 二进制对齐：所有数字转换为相同位数的二进制表示（较短数补前导零）
2. 差异计算：每对相邻数比较每一位，统计不同位的总数
3. 相邻对数：共有{n}对相邻数（0与1, 1与2, ..., {n-1}与{n}）

**示例说明**：
当n=5时序列为：000, 001, 010, 011, 100, 101
差异计算：1+2+1+3+1=8

**当前输入**：
n = {n}

**答案要求**：
将最终结果用[answer]标签包裹，例如：[answer]8[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

