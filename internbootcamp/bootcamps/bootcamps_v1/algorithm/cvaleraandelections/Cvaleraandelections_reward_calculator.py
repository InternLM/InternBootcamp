import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict




class CvaleraandelectionsRewardCalculator(BaseRewardCalculator):
    """Cvaleraandelections奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if len(lines) < 2:
            return None
        try:
            k = int(lines[0])
            candidates = list(map(int, lines[1].split()))
            if len(candidates) != k or len(set(candidates)) != k:
                return None
            return sorted(candidates)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 处理特殊情况：无问题道路
        problem_edges = [e for e in identity['edges'] if e[2] == 2]
        if not problem_edges:
            return solution == []
        
        # 构建完整的父节点关系（包含根节点的子节点）
        parent_map = defaultdict(lambda: None)
        parent_map.update(identity.get('parent_map', {}))
        
        # 验证问题边覆盖
        required_nodes = set()
        for u, v, _ in problem_edges:
            current = v
            while current is not None:
                required_nodes.add(current)
                current = parent_map[current]
        
        # 检查候选节点是否覆盖所有必要节点
        covered = set()
        for candidate in solution:
            current = candidate
            while current is not None:
                covered.add(current)
                current = parent_map[current]
        
        if not required_nodes.issubset(covered):
            return False

        # 验证极小性：检查每个候选是否必要
        for candidate in solution:
            temp_covered = set()
            for c in solution:
                if c == candidate:
                    continue
                current = c
                while current is not None:
                    temp_covered.add(current)
                    current = parent_map[current]
            if required_nodes.issubset(temp_covered):
                return False
        
        return True
    
    # 其他额外方法

