import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from typing import Dict
from typing import Any




class BinterestingarrayRewardCalculator(BaseRewardCalculator):
    """Binterestingarray奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> str:
        matches = re.findall(
            r'\[answer\](.*?)\[/answer\]', 
            output.replace('\n', ' '), 
            re.DOTALL
        )
        if matches:
            last_answer = matches[-1].strip()
            # 清理多余的空格和换行
            return ' '.join(last_answer.split())
        return None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: Dict) -> bool:
        if not solution:
            return False
        
        solution = solution.upper().split()
        expected = identity["solution_exists"]
        
        if expected:
            if solution[0] != "YES" or len(solution) != identity["n"] + 1:
                return False
            
            try:
                arr = list(map(int, solution[1:]))
                if any(not (0 <= x < (1<<30)) for x in arr):
                    return False
            except:
                return False
            
            for l, r, q in identity["constraints"]:
                current_and = arr[l-1]
                for num in arr[l:r]:
                    current_and &= num
                    if current_and < q:  # 提前终止优化的AND计算
                        break
                if current_and != q:
                    return False
            return True
        else:
            return solution[0] == "NO"
    
    # 其他额外方法

