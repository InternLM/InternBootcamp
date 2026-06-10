import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import bisect
from bisect import bisect_left
from bisect import bisect_right




class EsashaandapatientfriendInstructionGenerator(BaseInstructionGenerator):
    """Esashaandapatientfriend Bootcamp指令生成器"""
    
    def __init__(self, max_queries=10, max_time=int(1e9), max_speed=int(1e9)):
        """
        初始化Esashaandapatientfriend指令生成器
        
        Args:
            max_queries: 参数描述
            max_time: 参数描述
            max_speed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_queries = max_queries
        self.max_time = max_time
        self.max_speed = max_speed
    
    def case_generator(self):
        event_times = []  # 维护有序事件时间
        events = dict()   # 时间到速度的映射
        queries = []
        
        # 生成基础查询
        q_count = random.randint(3, self.max_queries)
        for _ in range(q_count-1):
            if not event_times or random.random() < 0.7:
                # 生成类型1事件
                while True:
                    t = random.randint(1, self.max_time)
                    if t not in events:
                        break
                s = random.randint(-self.max_speed, self.max_speed)
                bisect.insort(event_times, t)
                events[t] = s
                queries.append({"type": 1, "t": t, "s": s})
            else:
                # 生成类型2事件
                idx = random.randrange(len(event_times))
                t = event_times.pop(idx)
                del events[t]
                queries.append({"type": 2, "t": t})

        # 生成类型3查询
        l, r = self._gen_lr(event_times)
        v = random.randint(0, self.max_speed)
        
        # 筛选有效事件
        left = bisect.bisect_left(event_times, l)
        right = bisect.bisect_right(event_times, r)
        valid_events = [{"t": t, "s": events[t]} for t in event_times[left:right]]

        expected = self._simulate(valid_events, l, r, v)
        queries.append({
            "type": 3,
            "l": l,
            "r": r,
            "v": v,
            "expected": expected
        })

        return {
            "queries": queries,
            "expected": expected,
            "events": events
        }
    
    @staticmethod
    def prompt_func(question_case):
        queries = question_case["queries"]
        input_lines = [str(len(queries))]
        for q in queries:
            if q["type"] == 1:
                input_lines.append(f"1 {q['t']} {q['s']}")
            elif q["type"] == 2:
                input_lines.append(f"2 {q['t']}")
            else:
                input_lines.append(f"3 {q['l']} {q['r']} {q['v']}")

        problem_desc = (
            "Fedya's Patience Simulation\n\n"
            "Rules:\n"
            "1. Bowl bursts when patience (v) ≤ 0\n"
            "2. Events change tap speed at specific seconds\n"
            "3. Type 3 queries simulate from l to r with initial v\n\n"
            f"Input Queries:\n" + "\n".join(input_lines) + "\n\n"
            "Compute the exact burst time (with 6 decimal places if needed) "
            "or -1 if it doesn't burst.\n"
            "Format your answer as: [answer]<result>[/answer]"
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _gen_lr(self, event_times):
        """生成合理的l和r范围"""
        if event_times:
            min_t = event_times[0]
            max_t = event_times[-1]
            l = random.randint(max(1, min_t-10), max_t+10)
            r = random.randint(l, min(self.max_time, max_t+1000))
        else:
            l = random.randint(1, 100)
            r = random.randint(l, min(self.max_time, l+1000))
        return l, r

    @staticmethod
    def _simulate(events, l, r, v_initial):
        if v_initial == 0:
            return l  # 初始值为0立即破裂

        current_time = l
        current_speed = 0  # 初始速度
        v = v_initial
        sorted_events = sorted(events, key=lambda x: x["t"])

        for event in sorted_events:
            t_event = event["t"]
            s_new = event["s"]

            # 处理当前时间段 [current_time, t_event)
            if t_event > current_time:
                dt = t_event - current_time
                if current_speed < 0:
                    # 计算在当前速度下是否会耗尽
                    if v <= 0:
                        return current_time
                    time_to_empty = v / (-current_speed)
                    if time_to_empty <= dt:
                        return current_time + time_to_empty
                    # 不会耗尽，更新v和时间
                    v += current_speed * dt
                    current_time = t_event
                else:
                    v += current_speed * dt
                    current_time = t_event
                if v <= 0:
                    return current_time  # 刚好在时间点耗尽

            # 更新速度
            current_speed = s_new

        # 处理最后的时间段 [current_time, r)
        dt = r - current_time
        if dt > 0:
            if current_speed < 0:
                if v <= 0:
                    return current_time
                time_to_empty = v / (-current_speed)
                if time_to_empty <= dt:
                    return current_time + time_to_empty
                v += current_speed * dt
            else:
                v += current_speed * dt
            if v <= 0:
                return r  # 在结束时间点耗尽

        return -1 if v > 0 else r
