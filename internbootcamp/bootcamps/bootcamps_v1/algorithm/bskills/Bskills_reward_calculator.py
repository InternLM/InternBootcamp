import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BskillsRewardCalculator(BaseRewardCalculator):
    """Bskills奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\][\s]*([\d\s]+?)[\s]*\[/answer\]', output, flags=re.DOTALL)
        if not matches:
            return None
        
        try:
            # 提取最后一个有效答案块
            last_answer = matches[-1].strip()
            lines = [l.strip() for l in last_answer.split('\n') if l.strip()]
            if len(lines) < 2:
                return None
            return list(map(int, lines[1].split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """全面验证解决方案的正确性"""
        if not solution or len(solution) != identity['n']:
            return False
        
        # 等级合法性检查
        for orig, final in zip(identity['a'], solution):
            if not (orig <= final <= identity['A']):
                return False
        
        # 预算检查
        total_cost = sum(final - orig for orig, final in zip(identity['a'], solution))
        if total_cost > identity['m']:
            return False
        
        # 计算实际Force值
        perfect_count = sum(1 for lv in solution if lv == identity['A'])
        min_level = min(solution)
        actual_force = perfect_count * identity['cf'] + min_level * identity['cm']
        
        # 验证是否为最优解（对比预计算的最优值）
        return actual_force == identity['_force']
    
    # 其他额外方法

