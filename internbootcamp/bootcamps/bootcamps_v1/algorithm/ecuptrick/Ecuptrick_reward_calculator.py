import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EcuptrickRewardCalculator(BaseRewardCalculator):
    """Ecuptrick奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip().replace('\n', ' ')
        if answer == '-1':
            return -1
        try:
            return list(map(int, answer.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 完整答案验证需要模拟操作流程
        try:
            if solution == -1:
                return False  # 我们保证生成的case都有解
            
            n = identity['n']
            cups = solution.copy()
            for xi, yi in identity['operations']:
                try:
                    pos = cups.index(xi)
                except ValueError:
                    return False  # 杯子不存在
                if pos + 1 != yi:
                    return False  # 位置不符
                # 执行移动操作
                cups = [xi] + cups[:pos] + cups[pos+1:]
            return True
        except:
            return False
    
    # 其他额外方法

