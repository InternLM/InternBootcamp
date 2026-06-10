import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict




class CairconditionerInstructionGenerator(BaseInstructionGenerator):
    """Cairconditioner Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=100, m_min=-1000, m_max=1000, time_delta_min=0, time_delta_max=100):
        """
        初始化Cairconditioner指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
            time_delta_min: 参数描述
            time_delta_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.m_min = m_min
        self.m_max = m_max
        self.time_delta_min = time_delta_min  # 允许0间隔
        self.time_delta_max = time_delta_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m = random.randint(self.m_min, self.m_max)
        prev_t = 0
        t_list = []
        
        # 生成允许重复的时间序列（非递减）
        for _ in range(n):
            delta = random.randint(self.time_delta_min, self.time_delta_max)
            prev_t += delta
            t_list.append(prev_t)
        
        current_l = current_r = m
        previous_time = 0
        customers = []
        
        # 生成基础可行案例
        for t in t_list:
            dt = t - previous_time
            new_l = current_l - dt
            new_r = current_r + dt
            
            # 确保生成有效温度区间
            a = random.randint(new_l, new_r)
            b = random.randint(a, new_r)
            customers.append({'t': t, 'l': a, 'h': b})
            
            current_l = max(new_l, a)
            current_r = min(new_r, b)
            previous_time = t

        # 50%概率转为不可解案例
        if random.choice([True, False]):
            # 计算每个时间点的允许温度范围
            allowed_ranges = []
            sim_l = sim_r = m
            sim_prev = 0
            for c in customers:
                dt = c['t'] - sim_prev
                allowed_l = sim_l - dt
                allowed_r = sim_r + dt
                allowed_ranges.append((allowed_l, allowed_r))
                sim_l = max(allowed_l, c['l'])
                sim_r = min(allowed_r, c['h'])
                sim_prev = c['t']
            
            # 查找可破坏的客户
            candidates = []
            for i, (al, ar) in enumerate(allowed_ranges):
                current_l, current_h = customers[i]['l'], customers[i]['h']
                if current_l > ar or current_h < al:
                    continue  # 已经无法满足的客户不处理
                candidates.append(i)
            
            # 找到可破坏的客户后进行调整
            if candidates:
                idx = random.choice(candidates)
                al, ar = allowed_ranges[idx]
                
                # 确保新区间与允许范围无交集
                if random.random() < 0.5:
                    new_l = ar + 1
                    new_h = new_l + 10  # 确保区间有效性
                else:
                    new_h = al - 1
                    new_l = new_h - 10  # 确保区间有效性
                new_l, new_h = sorted([new_l, new_h])
                
                # 应用破坏
                customers[idx]['l'] = new_l
                customers[idx]['h'] = new_h

        return {
            'initial_temp': m,
            'customers': sorted(customers, key=lambda x: x['t'])  # 确保时间有序
        }
    
    @staticmethod
    def prompt_func(question_case):
        m = question_case['initial_temp']
        customers = question_case['customers']
        
        problem = f"Gildong's restaurant has an initial temperature of {m}°C. Customers will arrive at specific times with preferred temperature ranges:\n"
        problem += "\nThe air conditioner can be in three states: off (maintains temperature), heating (+1°C/min), or cooling (-1°C/min). State changes can occur at any integer minute.\n\n"
        problem += "Customers (sorted by visit time):\n"
        for idx, c in enumerate(customers, 1):
            problem += f"{idx}. Time: {c['t']} min, Range: [{c['l']}, {c['h']}]°C\n"
        problem += "\nDetermine if all customers can be satisfied. Reply with [answer]YES[/answer] or [answer]NO[/answer]."
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _solve_identity(cls, identity):
        m = identity['initial_temp']
        customers = identity['customers']
        time_dict = defaultdict(list)

        # 合并同时到达的客户
        for c in customers:
            time_dict[c['t']].append((c['l'], c['h']))

        merged = []
        for t in sorted(time_dict):
            ls, hs = zip(*time_dict[t]) if time_dict[t] else ([], [])
            merged_l = max(ls) if ls else 0
            merged_h = min(hs) if hs else 0
            if merged_l > merged_h:
                return 'NO'
            merged.append((t, merged_l, merged_h))

        current_l = current_r = m
        prev_t = 0

        for t, l, h in merged:
            dt = t - prev_t
            new_l = current_l - dt
            new_r = current_r + dt

            # 检查是否存在可行区间
            if new_r < l or new_l > h:
                return 'NO'

            # 收紧温度范围
            current_l = max(new_l, l)
            current_r = min(new_r, h)
            prev_t = t

        return 'YES'
