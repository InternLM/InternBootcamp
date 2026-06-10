import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class ChongcowbuysadeckofcardsInstructionGenerator(BaseInstructionGenerator):
    """Chongcowbuysadeckofcards Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=8, max_r=5, max_b=5, **kwargs):
        """
        初始化Chongcowbuysadeckofcards指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_r: 参数描述
            max_b: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        # 参数校验确保合理范围
        self.min_n = max(1, min(min_n, 10))
        self.max_n = max(self.min_n, min(max_n, 10))
        self.max_r = min(max(1, max_r), 20)
        self.max_b = min(max(1, max_b), 20)
    
    def case_generator(self):
        for _ in range(10):  # 最多尝试10次生成有效案例
            n = random.randint(self.min_n, self.max_n)
            cards = [{
                'color': random.choice(['R', 'B']),
                'r': random.randint(0, self.max_r),
                'b': random.randint(0, self.max_b)
            } for _ in range(n)]
            
            # 确保至少一个卡片有需求
            if all(c['r'] == 0 and c['b'] == 0 for c in cards):
                continue
            
            try:
                answer = self.calculate_min_turns(n, cards)
                return {
                    'n': n,
                    'cards': cards,
                    'correct_answer': answer
                }
            except Exception as e:
                continue
        
        # 保底生成简单案例
        return {
            'n': 2,
            'cards': [
                {'color': 'R', 'r': 1, 'b': 0},
                {'color': 'B', 'r': 0, 'b': 1}
            ],
            'correct_answer': 2
        }
    
    @staticmethod
    def prompt_func(question_case):
        case_str = "\n".join(
            f"{card['color']} {card['r']} {card['b']}" 
            for card in question_case['cards']
        )
        return f"""Hongcow需要购买所有卡片。每个操作可以：
1. 收集红蓝令牌各1个
2. 购买卡片（需消耗max(需求-已有对应颜色卡数,0)的对应令牌）

输入：
{question_case['n']}
{case_str}

请计算最少操作次数，并将答案放在[answer]标签内。示例：[answer]5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_min_turns(n, cards):
        # 预处理卡片数据
        color = [1 if c['color'] == 'B' else 0 for c in cards]
        r = [c['r'] for c in cards]
        b = [c['b'] for c in cards]

        total_r = sum(r)
        total_b = sum(b)
        max_rsave = total_r  # 红令牌最多能节省的总量

        # DP状态定义：dp[mask][rsave] = 最大bsave
        dp = [[-1]*(max_rsave+1) for _ in range(1<<n)]
        dp[0][0] = 0  # 初始状态

        for mask in range(1<<n):
            # 计算当前拥有的红蓝卡数量
            current_r = sum(0 if color[i] else 1 
                          for i in range(n) if (mask >> i) & 1)
            current_b = sum(1 if color[i] else 0 
                          for i in range(n) if (mask >> i) & 1)

            for rsave in range(max_rsave+1):
                if dp[mask][rsave] == -1:
                    continue

                # 尝试购买下一张卡片
                for next_card in range(n):
                    if (mask & (1 << next_card)) == 0:
                        # 计算实际需要支付的令牌
                        needed_r = max(r[next_card] - current_r, 0)
                        needed_b = max(b[next_card] - current_b, 0)

                        # 累计节省的令牌
                        new_rsave = rsave + (r[next_card] - needed_r)
                        new_bsave = dp[mask][rsave] + (b[next_card] - needed_b)
                        new_mask = mask | (1 << next_card)

                        # 更新状态
                        if new_rsave <= max_rsave and new_bsave > dp[new_mask][new_rsave]:
                            dp[new_mask][new_rsave] = new_bsave

        # 计算最终结果
        min_ops = max(total_r, total_b)  # 初始值
        full_mask = (1 << n) - 1

        for rsave in range(max_rsave+1):
            if dp[full_mask][rsave] != -1:
                required_r = max(total_r - rsave, 0)
                required_b = max(total_b - dp[full_mask][rsave], 0)
                min_ops = min(min_ops, max(required_r, required_b))

        return min_ops + n  # 加上购买卡片的n次操作
