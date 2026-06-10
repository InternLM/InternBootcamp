import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import gcd
from collections import defaultdict




class CdilucandkaeyaRewardCalculator(BaseRewardCalculator):
    """Cdilucandkaeya奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强版答案提取：处理多种格式变体
        pattern = r'''
            \[answer\]       # 起始标签
            \s*              # 允许前置空白
            ((?:             # 捕获组：匹配数字序列
                \d+          # 数字
                (?:\s+|,|;)* # 允许空格、逗号、分号分隔
            )+) 
            \s*              # 允许后置空白
            \[/answer\]      # 结束标签
        '''
        matches = re.findall(pattern, output, re.VERBOSE | re.IGNORECASE)
        if not matches:
            return None
        
        # 规范化数字序列
        last_match = re.sub(r'[^0-9\s]', ' ', matches[-1])  # 替换非数字字符为空格
        normalized = ' '.join(last_match.strip().split())   # 合并多余空格
        return normalized
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 强化验证逻辑
        try:
            # 步骤1：解析输入
            s = identity['s']
            n = identity['n']
            
            # 步骤2：计算正确答案
            ratio_counter = defaultdict(int)
            correct_answers = []
            d_count = k_count = 0
            
            for char in s:
                d_count += (char == 'D')
                k_count += (char == 'K')
                
                # 计算最简比例
                if d_count == 0 and k_count == 0:
                    current_ratio = (0, 0)  # 理论上不可能出现
                elif k_count == 0:
                    current_ratio = (1, 0)
                elif d_count == 0:
                    current_ratio = (0, 1)
                else:
                    divisor = gcd(d_count, k_count)
                    current_ratio = (d_count//divisor, k_count//divisor)
                
                # 当前可分割数 = 该比例出现次数（包含当前）
                ratio_counter[current_ratio] += 1
                correct_answers.append(str(ratio_counter[current_ratio]))
            
            # 步骤3：验证格式和内容
            expected = ' '.join(correct_answers)
            return solution.strip() == expected
            
        except Exception as e:
            print(f"Validation Error: {str(e)}")
            return False
    
    # 其他额外方法

