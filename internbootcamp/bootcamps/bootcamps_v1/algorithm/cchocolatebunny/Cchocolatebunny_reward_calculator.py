import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CchocolatebunnyRewardCalculator(BaseRewardCalculator):
    """Cchocolatebunny奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """强健的答案提取方法"""
        # 匹配所有可能的答案块
        answer_blocks = re.findall(
            r'\[answer\][\s\S]*?!([\s\S]*?)\[\/answer\]',
            output,
            flags=re.IGNORECASE
        )
        
        if not answer_blocks:
            return None
        
        # 提取最后一个答案块中的数字
        numbers = re.findall(r'\d+', answer_blocks[-1])
        try:
            return list(map(int, numbers))
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """完整的验证流程"""
        expected = identity['permutation']
        n = identity['n']
        
        # 类型和长度校验
        if not isinstance(solution, list) or len(solution) != n:
            return False
        
        # 元素范围校验
        if set(solution) != set(range(1, n+1)):
            return False
        
        # 精确顺序校验
        return solution == expected
    
    # 其他额外方法

