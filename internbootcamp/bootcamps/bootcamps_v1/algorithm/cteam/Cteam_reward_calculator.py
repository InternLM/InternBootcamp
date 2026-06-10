import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CteamRewardCalculator(BaseRewardCalculator):
    """Cteam奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        强化答案提取逻辑，处理多种可能输出格式
        """
        # 优先匹配标准格式
        answer_tag_match = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if answer_tag_match:
            candidate = answer_tag_match[-1].strip().replace(' ', '').replace('\n', '')
            if candidate == '-1':
                return '-1'
            if all(c in {'0', '1'} for c in candidate):
                return candidate
        
        # 处理无标签但符合格式的输出
        clean_output = output.strip().replace(' ', '').replace('\n', '')
        if clean_output == '-1':
            return '-1'
        if len(clean_output) == (question_case.get('n',0) + question_case.get('m',0)):
            if '00' not in clean_output and '111' not in clean_output:
                return clean_output
        
        # 提取最长有效序列
        valid_sequences = re.findall(r'[01]+', output)
        if valid_sequences:
            return max(valid_sequences, key=len)
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        实现数学验证算法，确保与参考解法逻辑一致
        """
        n, m = identity['n'], identity['m']
        
        # 处理无解情况
        if solution == '-1':
            # 计算理论是否可解
            valid = not ((n <= m + 1) and (m <= 2 * (n + 1)))
            return valid
        
        # 验证基本参数
        try:
            if (solution.count('0') != n or 
                solution.count('1') != m or
                len(solution) != n + m):
                return False
        except:
            return False
        
        # 实现参考解法验证逻辑
        prev_zero = False
        consecutive_ones = 0
        for c in solution:
            if c == '0':
                if prev_zero:
                    return False
                prev_zero = True
                consecutive_ones = 0
            else:
                consecutive_ones += 1
                if consecutive_ones > 2:
                    return False
                prev_zero = False
        return True
    
    # 其他额外方法

