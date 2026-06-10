import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque




class DratingcompressionRewardCalculator(BaseRewardCalculator):
    """Dratingcompression奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 格式验证
        if not solution or len(solution) != identity['n']:
            return False
        
        # 逻辑验证（兼容可能存在多个正确解的情况）
        expected = identity['correct_answer']
        
        # 检查每个有效位的合理性
        for k in range(1, identity['n']+1):
            if solution[k-1] == '1' and expected[k-1] == '0':
                return False
            if identity['case_type'] == 'invalid_all' and '1' in solution:
                return False
        return solution == expected
    
    # 其他额外方法

