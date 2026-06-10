import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CtillicollapseRewardCalculator(BaseRewardCalculator):
    """Ctillicollapse奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """鲁棒的答案提取方法"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
            
        last_match = matches[-1].strip()
        cleaned = re.sub(r'\s+', ' ', last_match)  # 合并多余空白
        return cleaned if cleaned else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """增强验证稳定性的检查"""
        try:
            # 处理首尾可能的换行符
            ans_str = solution.strip()
            # 处理多空格情况
            ans_list = list(map(int, ans_str.split()))
            return ans_list == identity['ans']
        except:
            return False
    
    # 其他额外方法

