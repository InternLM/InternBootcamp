import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class ConlinecoursesinbsuRewardCalculator(BaseRewardCalculator):
    """Conlinecoursesinbsu奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if last_match == '-1':
            return -1
        try:
            lines = [l.strip() for l in last_match.split('\n') if l.strip()]
            m = int(lines[0])
            courses = list(map(int, lines[1].split()))
            if len(courses) != m:
                return None
            return courses
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution == -1:
            return not identity['possible']
        if not identity['possible']:
            return False
        
        # 验证课程集合完整性
        required = set()
        q = deque(identity['main'])
        while q:
            c = q.popleft()
            if c not in required:
                required.add(c)
                deps = next(d['deps'] for d in identity['dependencies'] if d['course'] == c)
                for dep in deps:
                    q.append(dep)
        
        if set(solution) != required:
            return False
        
        # 验证顺序正确性
        pos = {c: i for i, c in enumerate(solution)}
        for c in solution:
            deps = next(d['deps'] for d in identity['dependencies'] if d['course'] == c)
            for dep in deps:
                if dep in pos and pos[dep] >= pos[c]:
                    return False
        return True
    
    # 其他额外方法

