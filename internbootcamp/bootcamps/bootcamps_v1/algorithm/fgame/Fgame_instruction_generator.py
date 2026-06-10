import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class FgameInstructionGenerator(BaseInstructionGenerator):
    """Fgame Bootcamp指令生成器"""
    
    def __init__(self, max_n=3, max_r=5, **kwargs):
        """
        初始化Fgame指令生成器
        
        Args:
            max_n: 参数描述
            max_r: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数。
        :param max_n: 最大n值，用于生成测试案例时限制n的范围。
        :param max_r: 最大r值，限制修改次数。
        """
        super().__init__(**kwargs)
        self.max_n = max_n
        self.max_r = max_r
    
    def case_generator(self):
        """
        生成谜题实例。
        """
        n = random.randint(1, self.max_n)
        size = 2 ** n
        initial = [random.randint(0, 100) for _ in range(size)]
        r = random.randint(0, self.max_r)
        updates = []
        for _ in range(r):
            z = random.randint(0, size - 1)
            g = random.randint(0, 100)
            updates.append({"z": z, "g": g})
        return {
            "n": n,
            "r": r,
            "initial": initial,
            "updates": updates
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        将谜题实例转换为问题描述文本。
        """
        n = question_case["n"]
        r = question_case["r"]
        initial = " ".join(map(str, question_case["initial"]))
        updates = "\n".join([f"{u['z']} {u['g']}" for u in question_case["updates"]])
        example_input = f"{n} {r}\n{initial}"
        if r > 0:
            example_input += "\n" + updates

        prompt = f"""Allen和Bessie正在玩一个数字游戏。已知函数f接受n个二进制参数并返回实数值。游戏开始后，两人轮流随机设置变量的值，最终计算f的值。你的任务是计算游戏开始时和每次函数值变化后的期望值。

输入格式：
第一行是n和r（0 ≤ r ≤ 2^18），第二行有2^n个整数表示初始的f值，接着r行每行给出一个修改(z, g)表示将f在z处的值改为g。

输出格式：
输出r+1行，每行为对应阶段游戏的期望值，保留六位小数。

例如，给定输入：
2 2
0 1 2 3
2 5
0 4

正确输出：
1.500000
2.250000
3.250000

请将答案包含在[answer]标签内，每行一个结果，格式如下：
[answer]
1.500000
2.250000
3.250000
[/answer]

请输入以下测试案例的答案：
{example_input}"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

