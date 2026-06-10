import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class BplanetlapitulettiInstructionGenerator(BaseInstructionGenerator):
    """Bplanetlapituletti Bootcamp指令生成器"""
    
    def __init__(self, h_min=1, h_max=100, m_min=1, m_max=100):
        """
        初始化Bplanetlapituletti指令生成器
        
        Args:
            h_min: 参数描述
            h_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.h_min = h_min
        self.h_max = h_max
        self.m_min = m_min
        self.m_max = m_max
    
    def case_generator(self):
        h = random.randint(self.h_min, self.h_max)
        m = random.randint(self.m_min, self.m_max)
        
        # 生成随机合法起始时间逻辑优化
        valid_time = self._find_valid_time(h, m, "00:00")  # 保证存在解
        start_hh, start_mm = map(int, valid_time.split(':'))
        
        # 随机回退步数生成起始时间
        steps_back = random.randint(0, h*m-1)
        for _ in range(steps_back):
            start_mm -= 1
            if start_mm < 0:
                start_mm = m-1
                start_hh -= 1
                if start_hh < 0:
                    start_hh = h-1
        s_time = f"{start_hh:02d}:{start_mm:02d}"
        return {'h': h, 'm': m, 's': s_time}
    
    @staticmethod
    def prompt_func(question_case):
        h = question_case['h']
        m = question_case['m']
        s = question_case['s']
        prompt = f"""行星Bplanetlapituletti的镜像时间谜题
数字镜像规则：
┌───┬───┬───┬───┬───┐
│ 0 → 0 │ 1 → 1 │ 2 → 5 │
│ 5 → 2 │ 8 → 8 │ 其他 → 无效 │
└───────────────────┘

时间格式要求：
- 小时范围：00 至 {h-1:02d}
- 分钟范围：00 至 {m-1:02d}

验证规则：
1. 原时间所有数字必须可镜像
2. 镜像时间构成方式：
   - 镜像后的小时 = 原分钟数字镜像并反转顺序
   - 镜像后的分钟 = 原小时数字镜像并反转顺序
3. 镜像时间必须满足有效时间范围

当前观测时间：{s}
请计算之后最近的合法镜像时刻（包含当前时间），答案格式：[answer]HH:MM[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _nums(cls):
        return {'0':'0','1':'1','2':'5','5':'2','8':'8'}

    @classmethod
    def _is_valid_time(cls, hh, mm, h, m):
        hh_str = f"{hh:02d}"
        mm_str = f"{mm:02d}"
        nums = cls._nums()

        # 检查原始数字有效性
        for c in hh_str + mm_str:
            if c not in nums:
                return False

        # 构建镜像时间
        try:
            mirrored_hh = int(nums[mm_str[1]] + nums[mm_str[0]])
            mirrored_mm = int(nums[hh_str[1]] + nums[hh_str[0]])
        except KeyError:
            return False

        # 验证镜像时间范围
        return 0 <= mirrored_hh < h and 0 <= mirrored_mm < m

    @classmethod
    def _find_valid_time(cls, h, m, start_time):
        current_hh, current_mm = map(int, start_time.split(':'))
        for _ in range(h * m):
            if cls._is_valid_time(current_hh, current_mm, h, m):
                return f"{current_hh:02d}:{current_mm:02d}"

            # 时间递增逻辑
            current_mm += 1
            if current_mm >= m:
                current_mm = 0
                current_hh += 1
                if current_hh >= h:
                    current_hh = 0
        return f"{current_hh:02d}:{current_mm:02d}"  # 理论上不会执行到这
