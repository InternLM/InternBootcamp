import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class ApetyaandcatacombsRewardCalculator(BaseRewardCalculator):
    """Apetyaandcatacombs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强格式兼容性的答案提取"""
        matches = re.findall(r'\[answer\s*](.*?)\[/answer\s*]', output, re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1].strip().split()[0])  # 处理可能的多余内容
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """动态内存的验证算法"""
        last_occurrence = {}
        room_count = 1
        current_time = 1
        
        for ti in identity['t']:
            if ti in last_occurrence and last_occurrence[ti] >= current_time - len(last_occurrence):
                room_count += 1
                last_occurrence.clear()
            last_occurrence[ti] = current_time
            current_time += 1
            
        return solution == room_count
    
    # 其他额外方法

