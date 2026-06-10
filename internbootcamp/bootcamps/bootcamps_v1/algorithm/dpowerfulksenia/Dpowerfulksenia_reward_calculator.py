import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DpowerfulkseniaRewardCalculator(BaseRewardCalculator):
    """Dpowerfulksenia奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        return answer_blocks[-1].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            lines = [l.strip() for l in solution.split('\n') if l.strip()]
            if not lines:
                return False
            
            # 验证首行有效性
            first_line = lines[0].upper()
            if first_line not in {'YES', 'NO'}:
                return False
            
            # 获取原始数据
            n = identity['n']
            a = identity['a'].copy()
            total_xor = 0
            for num in a:
                total_xor ^= num
            
            # 校验理论正确性
            expected = 'YES' if (n%2 == 1) or (total_xor == 0) else 'NO'
            if first_line != expected:
                return False
            
            # NO情况直接返回正确
            if expected == 'NO':
                return True
            
            # 验证操作步骤
            if len(lines) < 2:
                return False  # 缺失操作数行
            
            try:
                m = int(lines[1])
                if m < 0 or m > n:
                    return False
            except ValueError:
                return False
            
            # 验证每个操作
            operations = []
            arr = a.copy()
            for line in lines[2:2+m]:
                if not line:
                    continue
                parts = line.split()
                if len(parts) != 3:
                    return False
                try:
                    i, j, k = map(int, parts)
                    if len({i, j, k}) != 3 or any(x < 1 or x > n for x in (i, j, k)):
                        return False
                    # 转换为0-based索引
                    i -= 1
                    j -= 1
                    k -= 1
                    # 执行操作
                    xor_val = arr[i] ^ arr[j] ^ arr[k]
                    arr[i] = arr[j] = arr[k] = xor_val
                except (ValueError, IndexError):
                    return False
            
            # 检查最终统一性
            return all(x == arr[0] for x in arr)
        
        except Exception:
            return False
    
    # 其他额外方法

