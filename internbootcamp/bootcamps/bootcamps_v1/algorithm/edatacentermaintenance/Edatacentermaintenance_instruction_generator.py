import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class EdatacentermaintenanceInstructionGenerator(BaseInstructionGenerator):
    """Edatacentermaintenance Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=10, max_h=24):
        """
        初始化Edatacentermaintenance指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_h: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，设定数据中心和客户的最大数量及最大小时数
        """
        self.max_n = max_n
        self.max_m = max_m
        self.max_h = max_h
    
    def case_generator(self):
        """
        生成符合规范的谜题实例，保证至少存在一个有效解
        """
        while True:
            n = random.randint(2, self.max_n)
            m = random.randint(1, self.max_m)
            h = random.randint(2, self.max_h)
            
            # 随机选择至少一个数据中心作为解
            k = random.randint(1, n)
            solution = random.sample(range(1, n+1), k)
            
            # 生成移位后的维护时间（虚拟解）
            v = [random.randint(0, h-1) for _ in range(n)]
            
            # 生成原始维护时间
            u = []
            for i in range(n):
                if (i+1) in solution:
                    u_i = (v[i] - 1) % h
                else:
                    u_i = v[i]
                u.append(u_i)
            
            # 生成有效的客户对
            clients = []
            valid = True
            for _ in range(m):
                retries = 50
                while retries > 0:
                    c1, c2 = random.sample(range(1, n+1), 2)
                    idx1, idx2 = c1-1, c2-1
                    
                    # 检查原始时间冲突
                    if u[idx1] == u[idx2]:
                        retries -= 1
                        continue
                    
                    # 检查解的有效性
                    shift1 = v[idx1] if c1 not in solution else (u[idx1]+1)%h
                    shift2 = v[idx2] if c2 not in solution else (u[idx2]+1)%h
                    if shift1 != shift2:
                        clients.append((c1, c2))
                        break
                    retries -= 1
                else:
                    valid = False
                    break
            
            if valid and len(clients) == m:
                return {
                    'n': n,
                    'm': m,
                    'h': h,
                    'u': u,
                    'clients': clients
                }
    
    @staticmethod
    def prompt_func(case) -> str:
        problem_desc = f"""## 数据中心维护调度问题

### 背景描述
BigData Inc. 拥有{case['n']}个数据中心（编号1-{case['n']}）和{case['m']}个客户。每个数据中心每天有一个维护时间段（0-{case['h']-1}小时）。客户数据存储在两个不同数据中心，要求这些中心的维护时间在调整后必须不同。

### 任务描述
你需要选择最少数量的数据中心进行维护时间调整（时间+1小时模{case['h']}），使得所有客户的可用性得到保证。

### 输入数据
- 数据中心维护时间：{' '.join(map(str, case['u']))}
- 客户数据存储对：\n""" 
        
        client_pairs = '\n'.join([f"{c1} {c2}" for c1, c2 in case['clients']])
        format_guidance = """
### 输出要求
1. 第一行为调整的数据中心数量k
2. 第二行包含k个不同的数据中心编号

请将答案放置在[answer]和[/answer]标签之间，例如：
[answer]
2
3 5
[/answer]"""
        
        return problem_desc + client_pairs + format_guidance 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

