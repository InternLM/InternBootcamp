import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class CfencepaintingRewardCalculator(BaseRewardCalculator):
    """Cfencepainting奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_block = None
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if matches:
            last_match = matches[-1].strip()
            lines = [l.strip() for l in last_match.split('\n') if l.strip()]
            if len(lines) >= 1:
                result = {'answer': lines[0].upper()}
                if result['answer'] == 'YES' and len(lines) >= 2:
                    try:
                        paints = list(map(int, lines[1].split()))
                        result['paints'] = paints
                    except:
                        return None
                if result['answer'] in ('YES', 'NO'):
                    return result
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or 'answer' not in solution:
            return False
        
        # 获取标准答案
        expected_answer, expected_paints = cls.solve_case(identity)
        
        # 验证答案类型
        if solution['answer'] != expected_answer:
            return False
        
        # 对于YES答案需要验证具体方案
        if solution['answer'] == 'YES':
            if 'paints' not in solution:
                return False
            
            # 验证方案长度
            if len(solution['paints']) != identity['m']:
                return False
            
            # 模拟涂色过程
            current = identity['a'].copy()
            for idx, (plank, color) in enumerate(zip(solution['paints'], identity['c'])):
                # 验证木板索引有效性
                if not (1 <= plank <= identity['n']):
                    return False
                current[plank-1] = color  # 转换为0-based索引
            
            # 验证最终结果
            return current == identity['b']
        
        return True
    
    # 其他额外方法

