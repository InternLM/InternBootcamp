import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DinterestingarrayRewardCalculator(BaseRewardCalculator):
    """Dinterestingarray奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强容错性的正则表达式
        answer_blocks = re.findall(
            r'\[ *answer *\](.*?)\[ */ *answer *\]', 
            output, 
            flags=re.IGNORECASE|re.DOTALL
        )
        if not answer_blocks:
            return None
        
        # 取最后一个答案块并标准化处理
        raw_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in raw_answer.split('\n') if line.strip()]
        
        if not lines:
            return None
        
        status = lines[0].upper()
        result = {'status': status}
        
        if status == 'YES' and len(lines) >= 2:
            try:
                arr = list(map(int, lines[1].split()))
                if all(0 <= x < (1<<30) for x in arr):
                    result['array'] = arr
                else:
                    return None
            except:
                return None
        return result if status in ('YES', 'NO') else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 基础校验
        if not solution or 'status' not in solution:
            return False
        if solution['status'] not in ('YES', 'NO'):
            return False
        
        # 状态一致性检查
        expected_status = 'YES' if identity['solution_exists'] else 'NO'
        if solution['status'] != expected_status:
            return False
        
        # 无解案例快速返回
        if not identity['solution_exists']:
            return solution['status'] == 'NO'
        
        # 有解案例详细验证
        arr = solution.get('array', [])
        if len(arr) != identity['n']:
            return False
        if any(not isinstance(x, int) or x < 0 or x >= (1<<30) for x in arr):
            return False
        
        # 逐约束验证
        for l, r, q in identity['constraints']:
            current_and = arr[l-1]
            for i in range(l, r):
                current_and &= arr[i]
                if current_and < q:  # 提前终止优化
                    break
            if current_and != q:
                return False
        return True
    
    # 其他额外方法

