import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CanyaandsmartphoneRewardCalculator(BaseRewardCalculator):
    """Canyaandsmartphone奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            m = identity['m']
            k = identity['k']
            a = identity['a']
            b = identity['b']
        except KeyError:
            return False
        
        # 初始化数据结构
        app_pos = {app: i+1 for i, app in enumerate(a)}
        pos_app = [0] * (n + 2)  # 位置从1开始
        for idx, app in enumerate(a):
            pos_app[idx+1] = app
        
        total_gestures = 0
        
        for app_id in b:
            current_pos = app_pos[app_id]
            # 计算手势次数
            screen = (current_pos - 1) // k
            total_gestures += (screen + 1)  # 滚动screen次 + 点击1次
            
            # 处理位置交换
            if current_pos > 1:
                prev_pos = current_pos - 1
                prev_app = pos_app[prev_pos]
                
                # 更新映射关系
                app_pos[app_id] = prev_pos
                app_pos[prev_app] = current_pos
                pos_app[current_pos] = prev_app
                pos_app[prev_pos] = app_id
        
        try:
            return int(solution) == total_gestures
        except:
            return False
    
    # 其他额外方法

