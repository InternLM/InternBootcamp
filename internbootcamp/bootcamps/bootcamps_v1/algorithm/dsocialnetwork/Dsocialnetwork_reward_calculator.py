import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import deque
from collections import defaultdict
import random
import re
import bisect




class DsocialnetworkRewardCalculator(BaseRewardCalculator):
    """Dsocialnetwork奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None
        if lines[0].lower() == 'no solution':
            return 'No solution'
        try:
            R = int(lines[0])
            user_ids = list(map(int, lines[1:]))
            return {'R': R, 'user_ids': user_ids}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity.get('correct_r') is None:
            return solution == 'No solution'
        if solution == 'No solution':
            return False
        if not isinstance(solution, dict):
            return False
        user_r = solution['R']
        user_ids = solution['user_ids']
        n = len(identity['times'])
        M = identity['M']
        T = identity['T']
        if len(user_ids) != n:
            return False

        # Verify user ID consistency
        unique_ids = set(user_ids)
        if len(unique_ids) != user_r or min(unique_ids) < 1 or max(unique_ids) > user_r:
            return False

        # Convert times to seconds
        times_sec = [cls._time_str_to_seconds(t) for t in identity['times']]

        # Simulate online periods
        events = []
        for uid, s in zip(user_ids, times_sec):
            start = s
            end = s + T - 1
            events.append((start, 'login', uid))
            events.append((end + 1, 'logout', uid))  # Event after online period

        events.sort(key=lambda x: (x[0], x[1] == 'logout'))

        current_online = set()
        max_online = 0
        reached_M = False
        for time, action, uid in events:
            if action == 'login':
                current_online.add(uid)
            else:
                current_online.discard(uid)
            
            current_count = len(current_online)
            if current_count > M:
                return False
            if current_count > max_online:
                max_online = current_count
            if current_count == M:
                reached_M = True

        return reached_M and max_online >= M
    
    # 其他额外方法

