import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from string import ascii_lowercase
import re




class CsubstringgameinthelessonRewardCalculator(BaseRewardCalculator):
    """Csubstringgameinthelesson奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强的答案提取逻辑"""
        # 匹配所有可能的答案块
        blocks = re.findall(r'\[answer\][\s]*((?:Mike|Ann\s*)+)[\s]*\[/answer\]', 
                          output, re.IGNORECASE)
        if not blocks:
            return None
        
        # 处理最后一个答案块
        last_block = blocks[-1].strip().upper()
        candidates = []
        for line in last_block.split('\n'):
            line = line.strip()
            if line == 'MIKE':
                candidates.append('Mike')
            elif line == 'ANN':
                candidates.append('Ann')
        
        return candidates if candidates else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """严格验证逻辑"""
        expected = identity['correct']
        # 双重验证：长度和内容
        return len(solution) == len(expected) and solution == expected
    
    # 其他额外方法

