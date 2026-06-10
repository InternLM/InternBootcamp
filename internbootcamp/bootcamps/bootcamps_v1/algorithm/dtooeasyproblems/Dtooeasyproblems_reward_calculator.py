import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DtooeasyproblemsRewardCalculator(BaseRewardCalculator):
    """Dtooeasyproblems奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """提取最后一个[answer]块内的答案"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if len(lines) < 2:  # 至少需要s和k两行
            return None
        
        try:
            s = int(lines[0])
            k = int(lines[1])
            if k == 0:
                return {'s': s, 'k': k, 'p_list': []}
            p_list = list(map(int, lines[2].split())) if len(lines)>=3 else []
            if len(p_list) != k:
                return None
            return {'s': s, 'k': k, 'p_list': p_list}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """核心验证逻辑"""
        # 获取标准答案
        try:
            correct = cls.solve_problem(
                identity['n'], 
                identity['T'], 
                identity['problems']
            )
        except:
            return False
        
        # 基本情况验证
        if solution['s'] != correct['s'] or solution['k'] != correct['k']:
            return False
        
        # 检查问题索引有效性
        p_list = solution['p_list']
        problem_dict = {i+1: (a, t) for i, (a, t) in enumerate(identity['problems'])}
        for p in p_list:
            if p not in problem_dict:
                return False
        
        # 验证总时间约束
        total_time = sum(problem_dict[p][1] for p in p_list)
        if total_time > identity['T']:
            return False
        
        # 验证每个问题的a_i >=k（k为正确的s值）
        k_max = correct['s']
        for p in p_list:
            if problem_dict[p][0] < k_max:
                return False
        
        return True
    
    # 其他额外方法

