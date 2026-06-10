import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CslavaandtanksInstructionGenerator(BaseInstructionGenerator):
    """Cslavaandtanks Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, min_n=2, **kwargs):
        """
        初始化Cslavaandtanks指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_n = min_n
        self.max_n = max_n  # 默认设为1000以保证验证效率
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        return {'n': n}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        prompt = f"""你正在玩一个名为“和平闪电”的游戏。你的任务是驾驶轰炸机摧毁分布在1×{n}的网格中的所有坦克。网格的每个单元格编号从1到{n}。每次轰炸一个单元格时，其中的所有坦克会受到一次伤害。

规则说明：
1. 当一个坦克第一次受到伤害时，它会立即移动到相邻的单元格。位于1号的坦克只能移动到2号，位于{n}号的坦克只能移动到{n-1}号。中间的坦克（比如位置i，2≤i≤{n-1}）第一次被炸时可以选择移动到i-1或i+1号单元格。
2. 当坦克第二次受到伤害时，它会被摧毁，并不再移动。
3. 你的目标是找到轰炸次数最少的方案，确保所有坦克都被摧毁，无论它们的初始位置如何。

请为这个{n}格的战场设计一个轰炸方案。输出应包含两行：第一行为最少次数m，第二行为m个整数表示轰炸顺序。答案请按照以下格式，包含在[answer]和[/answer]之间：

例如，当n=2时，正确的输出格式是：
[answer]
3
2 1 2
[/answer]

请确保你的答案严格遵循输出格式，并将最终答案放在标签内。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

