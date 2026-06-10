import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Set




class CcontinuouscityRewardCalculator(BaseRewardCalculator):
    """Ccontinuouscity奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Optional[str]:
        # 精确提取最后一个答案块
        start_tag = '[answer]'
        end_tag = '[/answer]'
        
        start_idx = output.rfind(start_tag)
        if start_idx == -1:
            return None
        
        end_idx = output.rfind(end_tag, start_idx)
        if end_idx == -1:
            return None
        
        return output[start_idx+len(start_tag):end_idx].strip()
    
    @classmethod
    def _verify_correction(cls, solution: Optional[str], identity: dict) -> bool:
        if not solution:
            return False
        
        solution = solution.strip()
        expected_possible = identity['possible']
        
        # 处理不可能情况
        if not expected_possible:
            return solution.upper() == "NO"
        
        # 验证可能情况的格式
        lines = [line.strip() for line in solution.split('\n') if line.strip()]
        if len(lines) < 3 or lines[0].upper() != "YES":
            return False
        
        try:
            n, m = map(int, lines[1].split())
            edges = []
            for line in lines[2:2+m]:
                a, b, c = map(int, line.split())
                if a >= b or c <= 0:
                    return False
                edges.append((a, b, c))
        except:
            return False
        
        # 验证结构约束
        if n < 2 or n > 32:
            return False
        if len(edges) != m:
            return False
        if len({(a,b) for a,b,_ in edges}) != m:
            return False
        
        # 高效验证路径特性
        return cls.validate_paths(n, edges, identity['L'], identity['R'])
    
    # 其他额外方法

