import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CproblemfornazarInstructionGenerator(BaseInstructionGenerator):
    """Cproblemfornazar Bootcamp指令生成器"""
    
    def __init__(self, max_lr=10**18):
        """
        初始化Cproblemfornazar指令生成器
        
        Args:
            max_lr: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_lr = max_lr
    
    def case_generator(self):
        # 生成边界案例的比例提升到50%
        if random.random() < 0.5:
            max_stage = self._find_max_stage()
            if max_stage == 0:
                return {'l': 1, 'r': 1}
            
            # 生成4种边界类型：阶段开始/中间/结束/跨阶段
            boundary_type = random.choice([1,2,3,4])
            
            if boundary_type == 1:  # 阶段边界
                stage = random.randint(1, max_stage)
                pos = (1 << stage) - 1  # 阶段结束位置
                delta = random.choice([-1, 0, 1])
                candidate = max(1, min(pos + delta, self.max_lr))
                return self._build_case_around(candidate)
            
            elif boundary_type == 2:  # 奇偶切换点
                stage = random.randint(1, max_stage-1)
                pos = (1 << stage) - 1
                return self._build_case_around(pos)
            
            elif boundary_type == 3:  # 大数边界
                return {'l': self.max_lr-10, 'r': self.max_lr}
            
            else:  # 跨多阶段案例
                stage1 = random.randint(1, max_stage-3)
                stage2 = stage1 + 3
                start = (1 << stage1) - 100
                end = (1 << stage2) + 100
                end = min(end, self.max_lr)
                start = max(1, start)
                r = random.randint(start, end)
                l = random.randint(start, r)
                return {'l': l, 'r': r}
        
        # 生成普通案例（覆盖各种数值范围）
        return self._generate_normal_case()
    
    @staticmethod
    def prompt_func(question_case):
        l = question_case['l']
        r = question_case['r']
        return f"""作为数学天才，你需要解决以下数列求和问题：

数列生成规则：
1. 生成阶段按奇偶交替，第1阶段（奇数阶段）生成1个奇数，第2阶段（偶数阶段）生成2个偶数，第3阶段生成4个奇数，依此类推，每个阶段的数目是前一个阶段的两倍
2. 数列起始值：
   - 奇数阶段：从当前最小的未使用奇数开始
   - 偶数阶段：从当前最小的未使用偶数开始
3. 示例数列开始部分：1, 2,4, 3,5,7,9, 6,8,10,12,14,16,18,20,...

现在需要计算第{l}个到第{r}个数字的和（包含两端），结果对10^9+7取模。

请按以下步骤解答：
1. 确定每个数字所属的阶段
2. 计算各阶段对应数字的和
3. 对总和取模

将最终答案放在[answer]标签内，例如：[answer]123456789[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _find_max_stage(self):
        """动态计算最大可能的阶段数"""
        total, stage = 0, 0
        while True:
            add = 1 << stage
            if total + add > self.max_lr:
                return stage
            total += add
            stage += 1

    def _build_case_around(self, pos):
        """生成围绕特定位置的测试案例"""
        if random.choice([True, False]):
            l = max(1, pos - random.randint(0, 100))
            r = min(self.max_lr, pos + random.randint(0, 100))
        else:
            r = min(self.max_lr, pos + random.randint(0, 1000))
            l = max(1, r - random.randint(0, 1000))
        return {'l': l, 'r': r}

    def _generate_normal_case(self):
        """生成覆盖不同范围的普通案例"""
        range_type = random.choice([
            'tiny', 'small', 'medium', 'large', 'huge'
        ])

        ranges = {
            'tiny': (1, 100),
            'small': (100, 10**6),
            'medium': (10**6, 10**12),
            'large': (10**12, 10**15),
            'huge': (10**15, self.max_lr)
        }
        min_r, max_r = ranges[range_type]
        r = self._get_random_in_range(min_r, max_r)
        l = random.randint(1, r)
        return {'l': l, 'r': r}

    def _get_random_in_range(self, min_val, max_val):
        """高效生成指定范围的随机数"""
        span = max_val - min_val
        if span < 0:
            return min_val
        return min_val + random.randint(0, span)

    @staticmethod
    def _calculate_sum(x):
        sum_total = 0
        stage_size = 1  # 当前阶段元素个数
        is_odd = True    # 当前阶段奇偶性
        next_odd = 1     # 下一个奇数起始值
        next_even = 2    # 下一个偶数起始值
        remaining = x

        while remaining > 0:
            take = min(stage_size, remaining)

            if is_odd:
                start = next_odd
                end = start + 2*(take-1)
                segment_sum = take * (start + end) // 2
                next_odd = end + 2
            else:
                start = next_even
                end = start + 2*(take-1)
                segment_sum = take * (start + end) // 2
                next_even = end + 2

            sum_total = (sum_total + segment_sum) % MOD
            remaining -= take
            stage_size *= 2
            is_odd = not is_odd

        return sum_total
