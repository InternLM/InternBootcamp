import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from typing import Dict
from typing import Any




class BinterestingarrayInstructionGenerator(BaseInstructionGenerator):
    """Binterestingarray Bootcamp指令生成器"""
    
    def __init__(self, n_min=5, n_max=10, m_min=3, m_max=5, p_unsolvable=0.3):
        """
        初始化Binterestingarray指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
            p_unsolvable: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.m_min = m_min
        self.m_max = m_max
        self.p_unsolvable = p_unsolvable
    
    def case_generator(self) -> Dict[str, Any]:
        # 增加更多不可解的情况类型
        if random.random() > self.p_unsolvable:
            # 生成可解案例时确保覆盖不同区间类型
            n = random.randint(self.n_min, self.n_max)
            m = random.randint(self.m_min, self.m_max)
            a = [random.randint(0, (1<<30)-1) for _ in range(n)]
            
            # 生成不同区间类型：全范围/左半段/右半段/随机区间
            intervals = [
                (1, n),  # 全数组
                (1, n//2),  # 左半段
                (n//2+1, n),  # 右半段
                *[tuple(sorted((random.randint(1, n), random.randint(1, n)))) 
                 for _ in range(m-3)]  # 随机区间
            ]
            random.shuffle(intervals)
            
            constraints = []
            for l, r in intervals[:m]:
                q = a[l-1]
                for num in a[l:r]:  # 计算实际的区间AND
                    q &= num
                constraints.append((l, r, q))
            
            return {
                "n": n,
                "m": m,
                "constraints": constraints,
                "solution_exists": True
            }
        else:
            # 生成更丰富的不可解案例
            n = random.randint(3, self.n_max)
            conflict_type = random.choice(['bit', 'composite', 'overlap'])
            
            if conflict_type == 'bit':  # 单一位冲突
                k = random.randint(0, 29)
                constraints = [
                    (1, n, 1 << k),
                    (random.randint(1, n), random.randint(1, n), 
                     random.randint(0, (1 << 30)-1) & ~(1 << k))
                ]
            elif conflict_type == 'composite':  # 复合位冲突
                constraints = [
                    (1, 2, 3),  # binary 11
                    (1, 1, 1),
                    (2, 2, 1),
                    (1, 2, 1)  # 实际AND应为1，但要求3
                ]
                n = 2
            else:  # 区间重叠冲突
                constraints = [
                    (1, 3, 4),   # binary 100
                    (1, 2, 5),   # binary 101
                    (2, 3, 6)    # binary 110
                ]
                n = 3
            
            return {
                "n": n,
                "m": len(constraints),
                "constraints": constraints,
                "solution_exists": False
            }
    
    @staticmethod
    def prompt_func(question_case: Dict) -> str:
        constraints_str = "\n".join(
            f"{l} {r} {q}" for l, r, q in question_case["constraints"]
        )
        return f"""给定数组长度n={question_case['n']}和m={question_case['m']}个约束条件，每个约束形如l r q，要求区间[l,r]的按位与等于q。请判断是否存在满足所有约束的数组，若存在输出YES及数组，否则输出NO。答案放在[answer]和[/answer]之间。

输入数据示例：
{question_case['n']} {question_case['m']}
{constraints_str}

要求：
1. 数组元素必须满足所有区间约束
2. 元素取值范围：[0, 2^30)
3. 按位与操作定义：对应二进制位都为1时结果位才为1

答案格式：
[answer]
YES
a1 a2 ... an
[/answer]
或：
[answer]
NO
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

