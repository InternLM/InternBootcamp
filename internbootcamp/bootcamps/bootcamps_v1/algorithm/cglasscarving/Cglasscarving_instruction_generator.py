import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CglasscarvingInstructionGenerator(BaseInstructionGenerator):
    """Cglasscarving Bootcamp指令生成器"""
    
    def __init__(self, default_w=4, default_h=3, max_cuts=4):
        """
        初始化Cglasscarving指令生成器
        
        Args:
            default_w: 参数描述
            default_h: 参数描述
            max_cuts: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化玻璃切割训练场环境。
        :param default_w: 默认玻璃板宽度
        :param default_h: 默认玻璃板高度
        :param max_cuts: 默认切割次数
        """
        self.default_w = default_w
        self.default_h = default_h
        self.max_cuts = max_cuts
    
    def case_generator(self):
        """
        生成一个玻璃切割谜题实例，包含初始尺寸、切割序列及预期结果。
        """
        w = self.default_w
        h = self.default_h
        n = self.max_cuts

        cuts = []
        h_cuts = set()  # 记录所有H切割的y坐标
        v_cuts = set()  # 记录所有V切割的x坐标

        for _ in range(n):
            # 动态选择可用的切割方向
            can_h = len(h_cuts) < h - 1
            can_v = len(v_cuts) < w - 1
            if not can_h and not can_v:
                raise ValueError("无法生成更多切割步骤，请调整参数")

            choices = []
            if can_h:
                choices.append('H')
            if can_v:
                choices.append('V')
            
            op = random.choice(choices)
            
            if op == 'H':
                available = list(set(range(1, h)) - h_cuts)
                y = random.choice(available)
                cuts.append({'type': 'H', 'value': y})
                h_cuts.add(y)
            else:
                available = list(set(range(1, w)) - v_cuts)
                x = random.choice(available)
                cuts.append({'type': 'V', 'value': x})
                v_cuts.add(x)

        # 构建切割序列数组
        H = [0, h] + [0] * n
        V = [0, w] + [0] * n
        for i in range(n):
            cut = cuts[i]
            if cut['type'] == 'H':
                H[i+2] = cut['value']
                V[i+2] = V[i+1]
            else:
                V[i+2] = cut['value']
                H[i+2] = H[i+1]

        # 计算预期结果
        ansH = self.gao(H)
        ansV = self.gao(V)
        expected_areas = [ansH[i] * ansV[i] for i in range(n)]

        return {
            'w': w,
            'h': h,
            'cuts': cuts,
            'expected_areas': expected_areas
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """将问题案例转换为自然语言描述"""
        w = question_case['w']
        h = question_case['h']
        cuts = question_case['cuts']
        problem = (
            "Leonid有一块宽{w}毫米、高{h}毫米的玻璃板。他按顺序进行了以下{num_cuts}次切割：\n"
        ).format(w=w, h=h, num_cuts=len(cuts))
        
        for i, cut in enumerate(cuts, 1):
            problem += f"{i}. {cut['type']} {cut['value']}\n"
        
        problem += (
            "\n每次切割后，请计算当前最大玻璃碎片的面积（单位：平方毫米），并将所有结果按顺序排列，用[answer]标签包裹。\n"
            "例如：\n[answer]\n8\n4\n4\n2\n[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def gao(c):
        """参考代码中的gao函数实现"""
        n = len(c)
        a = sorted((val, idx) for idx, val in enumerate(c))
        l = list(range(-1, n))
        r = list(range(1, n+2))
        index = [0] * n
        for i, (val, idx) in enumerate(a):
            index[idx] = i

        mx = 0
        for i in range(1, n):
            mx = max(mx, a[i][0] - a[i-1][0])

        ans = [mx]
        for i in range(n-1, 2, -1):
            pos = index[i]
            left = l[pos]
            right = r[pos]
            if left >= 0:
                r[left] = right
            if right < n:
                l[right] = left
            current_gap = a[right][0] - a[left][0] if right < n else 0
            mx = max(mx, current_gap)
            ans.append(mx)

        ans.reverse()
        return ans[:n]
