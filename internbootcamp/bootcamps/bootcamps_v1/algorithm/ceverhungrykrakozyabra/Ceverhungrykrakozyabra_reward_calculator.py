import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CeverhungrykrakozyabraRewardCalculator(BaseRewardCalculator):
    """Ceverhungrykrakozyabra奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个[answer]标签内容
        """
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案的正确性：遍历所有数字计算实际结果
        """
        L = identity['L']
        R = identity['R']
        unique_tails = set()
        
        for num in range(L, R + 1):
            # 处理数字并标准化表示
            sorted_str = ''.join(sorted(str(num))).lstrip('0')
            # 处理全零情况（根据题目输入限制不会出现）
            unique_tails.add(sorted_str if sorted_str else '0')
        
        return solution == len(unique_tails)
    
    # 其他额外方法

