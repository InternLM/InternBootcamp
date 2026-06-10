import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CdimaandstaircaseInstructionGenerator(BaseInstructionGenerator):
    """Cdimaandstaircase Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cdimaandstaircase指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'max_stairs': params.get('max_stairs', 10),
            'max_boxes': params.get('max_boxes', 10),
            'max_height_step': params.get('max_height_step', 100),
            'max_h': params.get('max_h', 100),
        }
    
    def case_generator(self):
        n = random.randint(1, self.params['max_stairs'])
        
        a = []
        current = random.randint(1, 10)
        a.append(current)
        for _ in range(n-1):
            current += random.randint(0, self.params['max_height_step'])
            a.append(current)

        m = random.randint(1, self.params['max_boxes'])
        boxes = []
        for _ in range(m):
            wi = random.choice([
                random.randint(1, max(1, n//2)),
                random.randint(max(1, n//2), n),
                1,
                n
            ])
            hi = random.randint(1, self.params['max_h'])
            boxes.append((wi, hi))

        expected = []
        current_max = 0
        for w, h in boxes:
            stair_height = a[w-1]
            box_bottom = max(stair_height, current_max)
            expected.append(box_bottom)
            current_max = box_bottom + h

        return {
            "n": n,
            "a": a,
            "m": m,
            "boxes": boxes,
            "expected_outputs": expected
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        # 单独生成带有换行的描述部分
        boxes_desc = []
        for i, (w, h) in enumerate(question_case['boxes']):
            boxes_desc.append(f"第{i+1}个箱子：宽度 {w}，高度 {h}")
        boxes_str = "\n".join(boxes_desc)

        input_lines = [
            str(question_case['n']),
            ' '.join(map(str, question_case['a'])),
            str(question_case['m'])
        ] + [f"{w} {h}" for w, h in question_case['boxes']]
        input_example = '\n'.join(input_lines)

        return f"""## 楼梯箱子问题

Dima有一个包含{question_case['n']}个台阶的楼梯，台阶高度为非递减序列：{' '.join(map(str, question_case['a']))}。现在依次投掷{question_case['m']}个箱子：

{boxes_str}

**规则说明**：
1. 每个箱子会覆盖前w个台阶
2. 箱子落地高度取决于台阶高度和之前堆叠的箱子的最大值
3. 输出结果应为每个箱子底部的最终高度

请严格按照顺序输出每个结果，每个数值单独一行放在[answer]标签内。

示例格式：
[answer]
42
13
7
[/answer]

当前问题的输入数据：
{input_example}
请计算并输出结果："""  # 修复换行符问题 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

