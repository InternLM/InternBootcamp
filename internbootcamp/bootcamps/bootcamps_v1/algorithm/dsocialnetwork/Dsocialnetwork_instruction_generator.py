import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import deque
from collections import defaultdict
import random
import re
import bisect




class DsocialnetworkInstructionGenerator(BaseInstructionGenerator):
    """Dsocialnetwork Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dsocialnetwork指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        self.default_params = {
            'min_n': 4,
            'max_n': 10,
            'min_M': 2,
            'max_M': 5,
            'min_T': 10,
            'max_T': 100,
        }
        self.default_params.update(params)
    
    def case_generator(self):
        def _solve_case(times, M, T):
            n = len(times)
            times_sec = [self._time_str_to_seconds(t) for t in times]
            ans = [0] * n
            r = 0
            real_m = 0
            cnt = defaultdict(int)
            last = defaultdict(int)
            cur_s = []  # Maintained as sorted list (descending by last time)
            q = deque()

            for i in range(n):
                s = times_sec[i]
                # Remove expired users
                while q and q[0][0] <= s:
                    expire_time, user_id = q.popleft()
                    cnt[user_id] -= 1
                    if cnt[user_id] == 0:
                        # Find and remove from cur_s
                        index = bisect.bisect_left(cur_s, (-last[user_id], -user_id))
                        if index < len(cur_s) and cur_s[index] == (-last[user_id], -user_id):
                            del cur_s[index]

                # Assign user ID
                if len(cur_s) >= M:
                    # Select user with largest last time (first in sorted cur_s)
                    selected_user = -cur_s[0][1]
                    ans[i] = selected_user
                else:
                    r += 1
                    ans[i] = r

                # Update user's expiration and counters
                user_id = ans[i]
                expire_time = s + T
                q.append((expire_time, user_id))
                cnt[user_id] += 1

                # Update last and cur_s
                prev_last = last.get(user_id, 0)
                if prev_last != 0:
                    # Remove previous entry
                    prev_entry = (-prev_last, -user_id)
                    index = bisect.bisect_left(cur_s, prev_entry)
                    if index < len(cur_s) and cur_s[index] == prev_entry:
                        del cur_s[index]
                last[user_id] = s
                new_entry = (-s, -user_id)  # Use negative for descending sort
                bisect.insort(cur_s, new_entry)

                # Update real_m
                current_online = len(cur_s)
                if current_online > real_m:
                    real_m = current_online

            # Check if reached M
            if real_m >= M:
                return r, ans
            else:
                return None, None

        max_attempts = 100
        for _ in range(max_attempts):
            # Generate parameters with M <= possible maximum users
            n = random.randint(self.default_params['min_n'], self.default_params['max_n'])
            max_possible_M = min(n, self.default_params['max_M'])
            M = random.randint(self.default_params['min_M'], max_possible_M)
            T = random.randint(self.default_params['min_T'], self.default_params['max_T'])

            # Generate overlapping times to increase valid cases
            base_time = random.randint(0, 86400 - T)
            times_sec = [base_time + random.randint(0, T//2) for _ in range(n//2)]
            # Add some non-overlapping times
            if n > len(times_sec):
                non_overlap_start = base_time + T + random.randint(1, 100)
                times_sec.extend([non_overlap_start + i*T for i in range(n - len(times_sec))])
            times_sec = sorted(times_sec)
            # Trim times to 86400 - T
            times_sec = [min(t, 86400 - T - 1) for t in times_sec]

            # Format times
            times = []
            for s in times_sec:
                hh, rem = divmod(s, 3600)
                mm, ss = divmod(rem, 60)
                times.append(f"{hh:02d}:{mm:02d}:{ss:02d}")

            # Solve case
            r, ans = _solve_case(times, M, T)
            if r is not None:
                return {
                    'times': times,
                    'M': M,
                    'T': T,
                    'correct_r': r,
                    'correct_ans': ans
                }
        # Fallback example
        return {
            'times': ['17:05:53', '17:05:58', '17:06:01', '22:39:47'],
            'M': 2,
            'T': 10,
            'correct_r': 3,
            'correct_ans': [1, 2, 2, 3]
        }
    
    @staticmethod
    def prompt_func(question_case):
        case = question_case
        times_str = '\n'.join(case['times'])
        n = len(case['times'])
        M = case['M']
        T = case['T']
        return f"""你是某社交网络的实习生，需要确定在24小时内访问网络的唯一用户最大数目。给定{n}个请求时间，每个请求后用户在线{T}秒。已知该日同时在线用户数达到{M}。请分配用户ID满足：
1. 任何时刻在线用户数≤{M}。
2. 至少有一个时刻在线用户数恰为{M}。
3. 用户总数尽可能多。

输入：
n = {n}
M = {M}
T = {T}

请求时间：
{times_str}

输出要求：
- 首行为用户总数R，随后{n}行为各请求的用户ID（1~R），无解输出"No solution"。

将答案置于[answer]和[/answer]之间。例如：
[answer]
3
1
2
2
3
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _time_str_to_seconds(time_str):
        hh, mm, ss = map(int, time_str.split(':'))
        return hh * 3600 + mm * 60 + ss
