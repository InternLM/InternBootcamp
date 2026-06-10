import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import bisect
import re




class DirrigationInstructionGenerator(BaseInstructionGenerator):
    """Dirrigation Bootcamp指令生成器"""
    
    def __init__(self, m_max=1000, n_max=1000):
        """
        初始化Dirrigation指令生成器
        
        Args:
            m_max: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化城市数量上限和前n届数量上限
        """
        super().__init__()
        self.m_max = max(1, m_max)   # 确保最小值为1
        self.n_max = max(1, n_max)   # 确保最小值为1
    
    def case_generator(self):
        """
        生成完整的问题实例，包含输入参数和预计算的正确答案
        """
        import random
        m = random.randint(1, self.m_max)  # m至少为1
        n = random.randint(1, self.n_max)  # n至少为1
        a = [random.randint(1, m) for _ in range(n)]  # 保证城市编号有效
        k_val = random.randint(n + 1, n + 10**6)  # 确保k > n
        
        # 生成完整的问题描述字典
        case = {
            'n': n,
            'm': m,
            'a': a,
            'k': k_val,
            'answer': self._compute_answer(n, m, a, k_val)  # 预存正确答案
        }
        return case  # 返回单一字典
    
    @staticmethod
    def prompt_func(question_case):
        """生成符合规范的问题描述"""
        return (
            f"## 奥林匹克主办城市选择问题\n\n"
            f"**已知条件**\n"
            f"- 前 {question_case['n']} 届主办城市：{question_case['a']}\n"
            f"- 共有 {question_case['m']} 个候选城市（编号1-{question_case['m']}）\n\n"
            f"**选择规则**\n"
            f"1. 从第 {question_case['n']+1} 届开始，每年选择历史上主办次数最少的城市\n"
            f"2. 若有多个城市次数相同，选择编号最小的\n\n"
            f"**查询请求**\n"
            f"请计算第 {question_case['k']} 届的主办城市编号，并将答案放置于[answer]和[/answer]之间\n\n"
            f"**答案格式示例**\n"
            f"[answer]3[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _compute_answer(self, n, m, a, k_val):
        """计算正确答案的核心算法"""
        if m == 0 or not a:
            return None

        counter = [0] * m
        for ai in a:
            counter[ai-1] += 1

        # 双重排序键：先按次数升序，再按编号升序
        count_order = sorted(range(m), key=lambda x: (counter[x], x))
        years = [0] * m

        # 计算阶段边界
        for i in range(m-1):
            if i+1 >= len(count_order):
                break
            diff = counter[count_order[i+1]] - counter[count_order[i]]
            years[i+1] = years[i] + diff * (i + 1)

        # 计算最大有效年份
        max_k = max(counter) * m - sum(counter)
        query_k = k_val - n

        # 处理超大规模年份
        if query_k > max_k:
            return ((query_k - max_k - 1) % m) + 1
        else:
            # 二分查找阶段边界
            idx = bisect.bisect_right(years, query_k) - 1
            # 获取候选城市列表
            candidates = sorted(count_order[:idx+1])
            # 计算最终位置
            return candidates[(query_k - years[idx] - 1) % len(candidates)] + 1
