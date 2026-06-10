import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class BonlinemeetingRewardCalculator(BaseRewardCalculator):
    """Bonlinemeeting奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配最后一个answer块
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        # 处理答案内容
        answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in answer.split('\n') if line.strip()]
        
        try:
            if not lines:
                return None
            
            # 处理0的情况
            if lines[0] == '0':
                return [] if len(lines) == 1 else None  # 严格格式检查
            
            k = int(lines[0])
            # 检查数量一致性
            if len(lines) < 2 or k == 0:
                return None
            
            ids = list(map(int, lines[1].split()))
            if len(ids) != k or sorted(ids) != ids:
                return None  # 数量或顺序错误
            
            return ids
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected']
        # 预期是空列表表示0个候选人
        if not expected:
            return solution == []
        # 比较ID列表是否完全一致
        return solution == expected
    
    # 其他额外方法

