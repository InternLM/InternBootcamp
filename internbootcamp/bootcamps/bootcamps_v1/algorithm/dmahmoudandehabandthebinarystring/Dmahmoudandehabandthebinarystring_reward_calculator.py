import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DmahmoudandehabandthebinarystringRewardCalculator(BaseRewardCalculator):
    """Dmahmoudandehabandthebinarystring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配标签内的最后一个答案
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if answer_blocks:
            last_answer = answer_blocks[-1].strip()
            match = re.fullmatch(r'!\s*(\d+)\s+(\d+)', last_answer)
            if match:
                return f"! {match.group(1)} {match.group(2)}"
        
        # 全局匹配严格格式
        matches = re.findall(r'!\s*\d+\s+\d+', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 格式验证
        match = re.fullmatch(r'!\s*(\d+)\s+(\d+)', solution.strip())
        if not match:
            return False
        
        pos0, pos1 = map(int, match.groups())
        s = identity['hidden_str']
        n = identity['n']
        
        # 有效性验证
        return (
            1 <= pos0 <= n and
            1 <= pos1 <= n and
            pos0 != pos1 and  # 关键修正点：必须不同位置
            s[pos0-1] == '0' and
            s[pos1-1] == '1'
        )
    
    # 其他额外方法

