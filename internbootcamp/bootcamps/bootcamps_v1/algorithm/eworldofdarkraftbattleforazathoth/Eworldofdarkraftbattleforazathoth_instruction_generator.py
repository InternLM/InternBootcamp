import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from bisect import bisect_right




class EworldofdarkraftbattleforazathothInstructionGenerator(BaseInstructionGenerator):
    """Eworldofdarkraftbattleforazathoth Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, max_p=10, weapon_a_max=1e6, weapon_ca_max=1e9, armor_b_max=1e6, armor_cb_max=1e9, monster_x_max=1e6, monster_y_max=1e6, monster_z_max=1e3):
        """
        初始化Eworldofdarkraftbattleforazathoth指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_p: 参数描述
            weapon_a_max: 参数描述
            weapon_ca_max: 参数描述
            armor_b_max: 参数描述
            armor_cb_max: 参数描述
            monster_x_max: 参数描述
            monster_y_max: 参数描述
            monster_z_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.max_p = max_p
        self.weapon_a_max = weapon_a_max
        self.weapon_ca_max = weapon_ca_max
        self.armor_b_max = armor_b_max
        self.armor_cb_max = armor_cb_max
        self.monster_x_max = monster_x_max
        self.monster_y_max = monster_y_max
        self.monster_z_max = monster_z_max
    
    def case_generator(self):
        # 生成武器并预处理最小成本
        n = random.randint(1, self.max_n)
        weapons = []
        for _ in range(n):
            a = random.randint(1, self.weapon_a_max)
            ca = random.randint(1, self.weapon_ca_max)
            weapons.append((a, ca))
        weapons.sort(reverse=True)
        min_weapon_ca = {}
        current_min = float('inf')
        for a, ca in weapons:
            current_min = min(current_min, ca)
            min_weapon_ca[a] = current_min
        
        # 生成护甲并预处理最小成本
        m = random.randint(1, self.max_m)
        armors = []
        for _ in range(m):
            b = random.randint(1, self.armor_b_max)
            cb = random.randint(1, self.armor_cb_max)
            armors.append((b, cb))
        armors.sort(reverse=True)
        min_armor_cb = {}
        current_min = float('inf')
        for b, cb in armors:
            current_min = min(current_min, cb)
            min_armor_cb[b] = current_min
        
        # 生成怪物
        p = random.randint(0, self.max_p)
        monsters = []
        for _ in range(p):
            x = random.randint(1, self.monster_x_max)
            y = random.randint(1, self.monster_y_max)
            z = random.randint(1, self.monster_z_max)
            monsters.append((x, y, z))
        
        # 按x排序并预处理怪物贡献
        monsters.sort()
        defense_contribution = {}
        for x, y, z in monsters:
            weapon_idx = bisect_right([a for a, _ in weapons], x)
            if weapon_idx < len(weapons):
                a_threshold = weapons[weapon_idx][0]
                if a_threshold > x:
                    defense_contribution.setdefault(y, 0)
                    defense_contribution[y] += z
        
        # 计算最大利润
        max_profit = -float('inf')
        armor_b_values = sorted(min_armor_cb.keys(), reverse=True)
        current_max_z = 0
        max_z_by_defense = {}
        
        # 构建防御贡献映射
        for b in sorted(armor_b_values, reverse=True):
            current_max_z += sum(z for y, z in defense_contribution.items() if y < b)
            max_z_by_defense[b] = current_max_z
        
        # 遍历武器计算最优解
        for a, ca in weapons:
            valid_defense = [b for b in armor_b_values if b > 0]  # 防御必须>0
            if not valid_defense:
                continue
            max_b = valid_defense[0]
            total_z = max_z_by_defense.get(max_b, 0)
            cb = min_armor_cb.get(max_b, float('inf'))
            profit = total_z - ca - cb
            if profit > max_profit:
                max_profit = profit
        
        # 处理无有效解的情况
        if max_profit == -float('inf'):
            min_ca = min(ca for _, ca in weapons)
            min_cb = min(cb for _, cb in armors)
            max_profit = - (min_ca + min_cb)
        
        return {
            "n": n,
            "m": m,
            "p": p,
            "weapons": [{"a": a, "ca": ca} for a, ca in weapons],
            "armors": [{"b": b, "cb": cb} for b, cb in armors],
            "monsters": [{"x": x, "y": y, "z": z} for x, y, z in monsters],
            "expected": max_profit
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [f"{question_case['n']} {question_case['m']} {question_case['p']}"]
        input_lines.extend(f"{w['a']} {w['ca']}" for w in question_case["weapons"])
        input_lines.extend(f"{a['b']} {a['cb']}" for a in question_case["armors"])
        input_lines.extend(f"{m['x']} {m['y']} {m['z']}" for m in question_case["monsters"])
        input_example = "\n".join(input_lines)

        return f"""Roma needs to choose one weapon and one armor to maximize profit. 

**Rules:**
1. Weapon attack must exceed monster's defense (a_i > x_k)
2. Armor defense must exceed monster's attack (b_j > y_k)
3. Profit = total coins from defeated monsters - (weapon cost + armor cost)
4. Must buy one weapon and one armor even if losing money

**Input:**
{input_example}

**Output Format:**
Single integer in [answer][/answer] tags. Example: [answer]-5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

