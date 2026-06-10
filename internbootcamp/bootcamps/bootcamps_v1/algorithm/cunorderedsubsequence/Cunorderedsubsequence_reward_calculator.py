import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CunorderedsubsequenceRewardCalculator(BaseRewardCalculator):
    """Cunorderedsubsequence奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        answer_str = matches[-1].strip()
        lines = answer_str.split('\n')
        if not lines:
            return None
        # 第一行是k
        k_str = lines[0].strip()
        if not k_str:
            return None
        try:
            k = int(k_str)
        except:
            return None
        if k == 0:
            return 0
        else:
            if len(lines) < 2:
                return None
            indices_str = lines[1].strip()
            indices = list(map(int, indices_str.split()))
            if len(indices) != k:
                return None
            return {'k': k, 'indices': indices}
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        correct_length = identity['correct_answer_length']
        correct_indices = identity['correct_answer_indices']
        if correct_length == 0:
            return solution == 0
        else:
            if isinstance(solution, dict) and solution['k'] == correct_length:
                sequence = identity['sequence']
                indices = solution['indices']
                # 转换为0-based
                subseq = [sequence[i - 1] for i in indices]
                # 检查是否无序
                is_ordered = False
                # 检查是否非递增
                non_increasing = True
                for i in range(len(subseq) - 1):
                    if subseq[i] < subseq[i + 1]:
                        non_increasing = False
                        break
                if non_increasing:
                    is_ordered = True
                else:
                    # 检查是否非递减
                    non_decreasing = True
                    for i in range(len(subseq) - 1):
                        if subseq[i] > subseq[i + 1]:
                            non_decreasing = False
                            break
                    if non_decreasing:
                        is_ordered = True
                # 如果子序列是无序的，则正确
                return not is_ordered
            else:
                return False
    
    # 其他额外方法

