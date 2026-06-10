import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CtabledecorationsRewardCalculator(BaseRewardCalculator):
    """Ctabledecorations奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """增强提取鲁棒性，处理多种格式异常"""
        # 清除可能的换行和空格干扰
        cleaned = output.replace('\n', ' ').replace('\r', '')
        matches = re.findall(r'\[answer\s*](.*?)\[/answer\s*]', cleaned)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """添加类型检查和验证日志"""
        if not isinstance(solution, int):
            return False
            
        r, g, b = identity['r'], identity['g'], identity['b']
        constraints = [
            r + g,
            g + b,
            r + b,
            (r + g + b) // 3
        ]
        return solution == min(constraints)
    
    # 其他额外方法

