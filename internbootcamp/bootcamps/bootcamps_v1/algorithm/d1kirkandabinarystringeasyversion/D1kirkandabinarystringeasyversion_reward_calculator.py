import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class D1kirkandabinarystringeasyversionRewardCalculator(BaseRewardCalculator):
    """D1kirkandabinarystringeasyversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        强化提取逻辑，增加格式校验和非法字符过滤
        """
        # 匹配最后一个有效答案块
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL | re.IGNORECASE)
        if not matches:
            return None
        
        # 提取并清理答案
        raw_answer = matches[-1].strip().replace('\n', '').replace(' ', '')
        
        # 过滤非法字符
        filtered = re.sub(r'[^01]', '', raw_answer)
        return filtered if len(filtered) == len(raw_answer) and filtered else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        增加solution格式校验，确保与s等长
        """
        if not solution or len(solution) != len(identity['s']):
            return False
        if not re.match('^[01]+$', solution):
            return False
        return solution == identity['t']
    
    # 其他额外方法

