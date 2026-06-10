import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BthechildandsetInstructionGenerator(BaseInstructionGenerator):
    """Bthechildandset Bootcamp指令生成器"""
    
    def __init__(self, min_limit=1, max_limit=10**5):
        """
        初始化Bthechildandset指令生成器
        
        Args:
            min_limit: 参数描述
            max_limit: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_limit = min_limit
        self.max_limit = max_limit
    
    def case_generator(self):
        # 50%概率生成有解案例，50%生成无解案例
        if random.random() < 0.5:
            # 生成有解案例
            limit = random.randint(self.min_limit, self.max_limit)
            
            # 收集所有lowbit信息
            candidates = []
            for num in range(1, limit+1):
                lb = num & -num
                candidates.append((lb, num))
            
            # 按lowbit降序排序
            candidates.sort(reverse=True, key=lambda x: x[0])
            
            # 随机选择有效子集
            selected = []
            sum_total = 0
            for lb, num in candidates:
                if random.random() < 0.7:  # 70%概率选择当前元素
                    selected.append(num)
                    sum_total += lb
                if sum_total > 0 and random.random() < 0.3:  # 30%概率停止
                    break
            
            # 确保至少选择一个元素
            if not selected:
                selected.append(candidates[0][1])
                sum_total = candidates[0][0]
            
            return {
                'sum': sum_total,
                'limit': limit,
                '_solution': selected  # 隐藏的解信息用于验证
            }
        else:
            # 生成无解案例
            limit = random.randint(self.min_limit, self.max_limit)
            max_sum = sum(num & -num for num in range(1, limit+1))
            return {
                'sum': max_sum + random.randint(1, 100),
                'limit': limit,
                '_solution': None
            }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        sum_val = question_case['sum']
        limit_val = question_case['limit']
        return f"""Picks需要找到满足以下条件的整数集合：
1. 所有元素都是1到{limit_val}之间的不同整数
2. 所有元素的lowbit之和等于{sum_val}

lowbit定义：数字二进制表示中最后一位1所代表的值，例如：
- lowbit(6) = 2（二进制110）
- lowbit(12) = 4（二进制1100）

如果存在这样的集合，按任意顺序输出元素；否则输出-1。
答案请用[answer]标签包裹，例如：
[answer]
3
1 2 3
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def find_solution(cls, sum_val, limit):
        # 参考原题给出的解题算法
        candidates = []
        for num in range(1, limit+1):
            lb = num & -num
            candidates.append((lb, num))

        candidates.sort(reverse=True, key=lambda x: x[0])
        remaining = sum_val
        selected = []
        for lb, num in candidates:
            if remaining >= lb:
                selected.append(num)
                remaining -= lb
        return selected if remaining == 0 else None
