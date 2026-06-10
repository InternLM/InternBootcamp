import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CglasscarvingRewardCalculator(BaseRewardCalculator):
    """Cglasscarving奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """从模型输出中提取最后一个[answer]块内的数字序列"""
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        last_answer = answer_blocks[-1].strip()
        solution = []
        for line in last_answer.split('\n'):
            line = line.strip()
            if line:
                try:
                    solution.append(int(line))
                except ValueError:
                    continue
        return solution if solution else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """验证答案是否与预期结果完全匹配"""
        expected = identity['expected_areas']
        return isinstance(solution, list) and solution == expected
    
    # 其他额外方法

