import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random




class DspaceminesInstructionGenerator(BaseInstructionGenerator):
    """Dspacemines Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dspacemines指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'A': params.get('A', self.generate_random_A()),
            'v': params.get('v', self.generate_random_v()),
            'R': params.get('R', random.randint(1, 100)),
            'min_mines': params.get('min_mines', 1),
            'max_mines': params.get('max_mines', 3),
        }
    
    def case_generator(self):
        while True:
            A = self.params['A']
            v = self.params['v']
            R = self.params['R']
            n = random.randint(self.params['min_mines'], self.params['max_mines'])
            
            mines = []
            existing = []
            for _ in range(n):
                mine = self.generate_mine(A, R, existing)
                if mine:
                    mines.append(mine)
                    existing.append(mine)
            if mines:
                break  # 成功生成至少一个地雷时退出循环

        # 计算正确解
        def compute_collision_time():
            t = float('inf')
            ax, ay, az = A
            vx, vy, vz = v
            
            def check(ox, oy, oz, r_check):
                nonlocal t
                x = ax - ox
                y = ay - oy
                z = az - oz
                
                a = vx**2 + vy**2 + vz**2
                if a == 0: return
                b = 2*(x*vx + y*vy + z*vz)
                c = x**2 + y**2 + z**2 - r_check**2
                
                disc = b**2 - 4*a*c
                if disc < 0: return
                
                sqrt_d = math.sqrt(disc)
                t1 = (-b + sqrt_d)/(2*a)
                t2 = (-b - sqrt_d)/(2*a)
                
                if t1 >= 0: t = min(t, t1)
                if t2 >= 0: t = min(t, t2)

            for mine in mines:
                # 检查本体碰撞
                ox, oy, oz = mine['O']
                check(ox, oy, oz, mine['r'] + R)
                # 检查尖刺碰撞
                for (px, py, pz) in mine['spikes']:
                    check(ox+px, oy+py, oz+pz, R)
            
            return t if t != float('inf') else -1.0

        return {
            'death_star': {'A': list(A), 'v': list(v), 'R': R},
            'mines': mines,
            'correct_t': compute_collision_time()
        }
    
    @staticmethod
    def prompt_func(case):
        prompt = "Rebel Commander Analysis Task\n\nDeath Star Parameters:\n"
        prompt += f"- Initial Position: {case['death_star']['A']}\n"
        prompt += f"- Velocity Vector: {case['death_star']['v']}\n"
        prompt += f"- Radius: {case['death_star']['R']}\n\n"
        prompt += f"Minefield Details ({len(case['mines'])} mines):\n"
        
        for i, mine in enumerate(case['mines'], 1):
            prompt += f"\nMine {i}:\n"
            prompt += f"- Center: {mine['O']}\n"
            prompt += f"- Body Radius: {mine['r']}\n"
            prompt += f"- Spikes: {len(mine['spikes'])}\n"
            if mine['spikes']:
                prompt += "  Spike Vectors:\n"
                for vec in mine['spikes']:
                    prompt += f"  {vec}\n"
        
        prompt += "\nCalculate the earliest collision time (precision 1e-6) or -1.\n"
        prompt += "Enclose your final answer within [answer]...[/answer] tags."
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_random_A(self):
        return (
            random.randint(-10000, 10000),
            random.randint(-10000, 10000),
            random.randint(-10000, 10000)
        )

    def generate_random_v(self):
        while True:
            v = (random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10))
            if any(v):
                return v

    def generate_mine(self, A, R, existing_mines):
        max_attempts = 1000
        for _ in range(max_attempts):
            # 生成随机方向和距离
            theta = random.uniform(0, math.pi)
            phi = random.uniform(0, 2*math.pi)
            dx = math.sin(theta)*math.cos(phi)
            dy = math.sin(theta)*math.sin(phi)
            dz = math.cos(theta)

            r_i = random.randint(1, R-1)
            min_dist = R + r_i + 1
            distance = random.uniform(min_dist, 2*min_dist)  # 生成适中距离

            ox = A[0] + dx*distance
            oy = A[1] + dy*distance
            oz = A[2] + dz*distance
            ox, oy, oz = int(round(ox)), int(round(oy)), int(round(oz))

            # 检查与已有地雷的间距
            valid = True
            for mine in existing_mines:
                mo = mine['O']
                mr = mine['r']
                dist_sq = (ox-mo[0])**2 + (oy-mo[1])**2 + (oz-mo[2])**2
                if dist_sq < (r_i + mr)**2:
                    valid = False
                    break
            if valid:
                return {
                    'O': [ox, oy, oz],
                    'r': r_i,
                    'm': random.randint(0, 10),
                    'spikes': [[random.randint(-10,10) for _ in range(3)] 
                              for _ in range(random.randint(0, 10))]
                }
        return None
