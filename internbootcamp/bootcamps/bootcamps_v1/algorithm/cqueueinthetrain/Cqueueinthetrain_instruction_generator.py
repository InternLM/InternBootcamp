import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque
import heapq
import re




class CqueueinthetrainInstructionGenerator(BaseInstructionGenerator):
    """Cqueueinthetrain Bootcamp指令生成器"""
    
    def __init__(self, max_n=100000, max_p=10**9, max_t=10**9):
        """
        初始化Cqueueinthetrain指令生成器
        
        Args:
            max_n: 参数描述
            max_p: 参数描述
            max_t: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_p = max_p
        self.max_t = max_t
    
    def case_generator(self):
        n = random.randint(1, min(self.max_n, 1000))  # 控制测试规模
        p = random.randint(1, self.max_p)
        
        # 生成更有挑战性的测试数据
        if random.random() < 0.3:
            # 生成全相同时间
            t = random.randint(0, self.max_t)
            t_list = [t] * n
        elif random.random() < 0.5:
            # 生成严格递增序列
            t_list = sorted(random.sample(range(self.max_t), n))
        else:
            # 随机生成包含重复值的数据
            t_list = [random.choice([0, self.max_t]) for _ in range(n)]
        
        correct_output = self.solve(n, p, t_list)
        return {
            'n': n,
            'p': p,
            't_list': t_list,
            'correct_output': correct_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        p = question_case['p']
        t_list = question_case['t_list']
        
        rule_desc = (
            "1. 每个乘客i在t_i分钟出发前往取水，使用时间为p分钟\n"
            "2. 出发时会检查所有左侧座位（1～i-1），如果任一左侧座位为空，则继续等待\n"
            "3. 如果所有左侧座位都有人，则立即加入队列\n"
            "4. 相同时间出发时，座位号小的乘客优先\n"
            "5. 队列遵循先到先服务原则，但需注意上述条件优先级"
        )
        
        example = (
            "输入示例：\n5 314\n0 310 942 628 0\n"
            "正确输出：\n314 628 1256 942 1570\n"
            "格式要求：用空格分隔的整数，座位1到n的完成时间"
        )

        return f"""解决火车车厢取水时间问题：

# 问题背景
{random.choice(["长途列车", "高铁动车"])}上有{n}个座位，每位乘客需要按特定规则使用饮水机。请计算各乘客完成取水的时间。

# 核心规则
{rule_desc}

# 输入参数
座位数n = {n}
单次使用时间p = {p}
出发时间列表t = [{' '.join(map(str, t_list))}]

# 输出要求
按座位顺序输出完成时间，格式为空格分隔的整数

{example}

请将最终答案放在[answer]和[/answer]标记之间：
[answer]
你的计算结果
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(n, p, t_list):
        temp = [(t, i) for i, t in enumerate(t_list)]
        temp.sort()
        people = deque()
        ready = []
        heapq.heapify(ready)
        time = 0
        i = 0
        result = [0] * n

        while i < n:
            if not people:
                if ready:
                    people.append(heapq.heappop(ready))
                else:
                    people.append(temp[i][1])
                    time = temp[i][0]
                    i += 1

            while i < n and temp[i][0] <= time + p:
                if temp[i][1] < people[-1]:
                    people.append(temp[i][1])
                else:
                    heapq.heappush(ready, temp[i][1])
                i += 1

            time += p
            passenger = people.popleft()
            result[passenger] = time

        while people:
            time += p
            passenger = people.popleft()
            result[passenger] = time

        while ready:
            time += p
            passenger = heapq.heappop(ready)
            result[passenger] = time

        return result
