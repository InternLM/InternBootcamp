import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CdividingthenumbersRewardCalculator(BaseRewardCalculator):
    """Cdividingthenumbers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 使用更健壮的正则表达式匹配
        answer_pattern = re.compile(
            r'\[answer\][\s\r\n]*(\d+)[\s\r\n]+(\d+[\s\d]*)[\s\r\n]*\[/answer\]', 
            re.DOTALL | re.IGNORECASE
        )
        matches = answer_pattern.findall(output)
        if not matches:
            return None
        
        # 只处理最后一个有效匹配
        last_match = matches[-1]
        try:
            diff = int(last_match[0])
            group_part = list(map(int, last_match[1].split()))
            if len(group_part) < 1:
                return None
            group_size = group_part[0]
            elements = group_part[1:]
            if group_size != len(elements):
                return None
            return {
                'diff': diff,
                'group_size': group_size,
                'elements': elements
            }
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 防御性编程：逐步排除所有可能错误
        if not solution:
            return False
        
        # 必需字段检查
        required_keys = {'diff', 'group_size', 'elements'}
        if any(key not in solution for key in required_keys):
            return False

        # 基础类型校验
        if not isinstance(solution['diff'], int):
            return False
        if not isinstance(solution['group_size'], int):
            return False
        if not isinstance(solution['elements'], (list, tuple)):
            return False

        # 获取验证参数
        n = identity['n']
        correct_diff = identity['correct_diff']
        total_sum = identity['total_sum']
        elements = solution['elements']
        group_size = solution['group_size']

        # 差值验证
        if solution['diff'] != correct_diff:
            return False

        # 分组大小有效性
        if group_size < 1 or group_size >= n:
            return False

        # 元素唯一性检查
        if len(set(elements)) != len(elements):
            return False

        # 元素范围检查
        if any(not (1 <= num <= n) for num in elements):
            return False

        # 数学验证
        sum_group = sum(elements)
        actual_diff = abs(2*sum_group - total_sum)  # 优化计算方式
        return actual_diff == correct_diff
    
    # 其他额外方法

