import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CpetyaandcatacombsRewardCalculator(BaseRewardCalculator):
    """Cpetyaandcatacombs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配标签大小写，使用多行匹配模式
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if matches:
            try:
                return int(matches[-1].strip())
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """严格参考原题解算法验证"""
        t_list = identity['t']
        state = {}
        room_count = 1
        for ti in t_list:
            if state.get(ti, False):
                room_count += 1
                # 重置所有状态（参考原题解中dp数组的更新逻辑）
                state = {k: False for k in state}
            state[ti] = True
        return solution == room_count
    
    # 其他额外方法

