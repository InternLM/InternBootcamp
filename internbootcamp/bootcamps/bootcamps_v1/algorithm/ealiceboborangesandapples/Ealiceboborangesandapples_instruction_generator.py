import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import re
import random




class EaliceboborangesandapplesInstructionGenerator(BaseInstructionGenerator):
    """Ealiceboborangesandapples Bootcamp指令生成器"""
    
    def __init__(self, max_value=10**6):
        """
        初始化Ealiceboborangesandapples指令生成器
        
        Args:
            max_value: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_value = max_value
    
    def case_generator(self):
        while True:
            x = random.randint(1, self.max_value)
            y = random.randint(1, self.max_value)
            if x * y > 1:
                if math.gcd(x, y) == 1:  # 确保合法实例与非法实例均衡生成
                    if random.choice([True, False]):
                        return {'x': x, 'y': y}
                else:
                    if random.choice([True, False]):
                        return {'x': x, 'y': y}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        x = question_case['x']
        y = question_case['y']
        prompt = f"""Alice和Bob发现袋子里有{x}个橙子和{y}个苹果。Alice拿了1个橙子，Bob拿了1个苹果。他们按卡片序列执行以下操作：
- A卡：Alice将所有水果给Bob，并重新从袋子拿取等量水果
- B卡：Bob将所有水果给Alice，并重新从袋子拿取等量水果
最终必须刚好拿完所有水果。请给出合法的压缩卡片序列（如3B）或输出Impossible。

答案请包裹在[answer][/answer]标签中。示例：[answer]1A1B[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def decompress(cls, compressed):
        if not re.fullmatch(r'([1-9]\d*[AB])+', compressed):
            return None

        parts = re.findall(r'([1-9]\d*)([AB])', compressed)
        return ''.join(c * int(n) for n, c in parts)

    @classmethod
    def validate_sequence(cls, sequence, x, y):
        bag_orange = x - 1
        bag_apple = y - 1
        a_orange, a_apple = 1, 0
        b_orange, b_apple = 0, 1

        for c in sequence:
            if c == 'A':
                transfer_orange = a_orange
                transfer_apple = a_apple
                new_a_orange = a_orange
                new_a_apple = a_apple
                if (transfer_orange > bag_orange) or (transfer_apple > bag_apple):
                    return False

                b_orange += transfer_orange
                b_apple += transfer_apple
                bag_orange -= transfer_orange
                bag_apple -= transfer_apple

                a_orange = new_a_orange
                a_apple = new_a_apple

            elif c == 'B':
                transfer_orange = b_orange
                transfer_apple = b_apple
                new_b_orange = b_orange
                new_b_apple = b_apple
                if (transfer_orange > bag_orange) or (transfer_apple > bag_apple):
                    return False

                a_orange += transfer_orange
                a_apple += transfer_apple
                bag_orange -= transfer_orange
                bag_apple -= transfer_apple

                b_orange = new_b_orange
                b_apple = new_b_apple

            else:
                return False

        return bag_orange == 0 and bag_apple == 0
