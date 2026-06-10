import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class CfencepaintingInstructionGenerator(BaseInstructionGenerator):
    """Cfencepainting Bootcamp指令生成器"""
    
    def __init__(self, possible=True, max_n=10, max_m=10):
        """
        初始化Cfencepainting指令生成器
        
        Args:
            possible: 参数描述
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.possible = possible
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        max_attempts = 100  # 防止无限循环的保险措施
        for _ in range(max_attempts):
            n = random.randint(1, self.max_n)
            m = random.randint(1, self.max_m)
            
            # 生成目标颜色数组
            b = [random.randint(1, n) for _ in range(n)]
            if len(set(b)) == 1 and m == 0:  # 处理特殊情况
                continue
                
            # 生成初始颜色数组
            a = []
            required_colors = defaultdict(list)
            for i, target in enumerate(b):
                if random.random() < 0.3:  # 30%概率生成差异
                    available = [c for c in range(1, n+1) if c != target]
                    if available:
                        a.append(random.choice(available))
                        required_colors[target].append(i)
                    else:
                        a.append(target)
                else:
                    a.append(target)
            
            # 生成油漆工颜色
            c = []
            if required_colors:
                # 确保最后一个颜色有效
                last_color_candidates = list(required_colors.keys())
                if any(c in required_colors for c in b):
                    last_color_candidates += [random.choice(b)]
                last_color = random.choice(last_color_candidates) if last_color_candidates else random.randint(1, n)
                
                # 填充前m-1个颜色
                for _ in range(m-1):
                    if required_colors:
                        c.append(random.choice(list(required_colors.keys())))
                    else:
                        c.append(random.randint(1, n))
                c.append(last_color)
            else:
                c = [random.choice(b) for _ in range(m)]
                if not c:
                    c = [random.randint(1, n)]
                c[-1] = random.choice(b) if b else c[-1]
            
            case = {'n': n, 'm': m, 'a': a, 'b': b, 'c': c}
            expected, _ = self.solve_case(case)
            
            # 验证是否符合预期解
            if (self.possible and expected == 'YES') or (not self.possible and expected == 'NO'):
                return case
        
        # 保险措施：返回简单案例
        return {'n': 1, 'm': 1, 'a': [1], 'b': [1], 'c': [1]}
    
    @staticmethod
    def prompt_func(question_case):
        problem = (
            "Repaint the fence with the following configuration:\n"
            f"Initial colors: {question_case['a']}\n"
            f"Target colors:  {question_case['b']}\n"
            f"Painters' colors in order: {question_case['c']}\n\n"
            "Rules:\n"
            "1. Each painter must paint exactly one plank\n"
            "2. Painters arrive in the given order (1st to mth)\n"
            "3. Final colors must exactly match the target\n\n"
            "Output format:\n"
            "[answer]\n"
            "YES\n"
            "x1 x2 ... xm\n"
            "[/answer]\n"
            "OR\n"
            "[answer]\n"
            "NO\n"
            "[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_case(case):
        a, b, c = case['a'], case['b'], case['c']
        n, m = case['n'], case['m']

        # 构建需要修改的位置
        required = defaultdict(list)
        for i in range(n):
            if a[i] != b[i]:
                required[b[i]].append(i)

        # 检查最后一个颜色是否有效
        last_valid = False
        if c:
            last_color = c[-1]
            if last_color in required:
                last_valid = True
            else:
                for i in range(n):
                    if b[i] == last_color:
                        last_valid = True
                        break

        if not last_valid:
            return ('NO', None)

        # 逆向构建解决方案
        solution = []
        temp_required = {k: v.copy() for k, v in required.items()}
        required_list = [(b[i], i) for i in range(n) if a[i] != b[i]]

        for color in reversed(c):
            found = False
            # 优先使用必须修改的位置
            if color in temp_required and temp_required[color]:
                plank = temp_required[color].pop()
                solution.append(plank)
                found = True
                if not temp_required[color]:
                    del temp_required[color]
            # 使用任意有效位置
            if not found:
                for i in range(n):
                    if b[i] == color:
                        solution.append(i)
                        found = True
                        break
            # 使用最后保留的位置
            if not found:
                solution.append(solution[-1] if solution else 0)

        # 检查是否所有需求都被满足
        if any(len(v) > 0 for v in temp_required.values()):
            return ('NO', None)

        # 反转并转换为1-based索引
        final_solution = [x+1 for x in reversed(solution)]
        return ('YES', final_solution)
