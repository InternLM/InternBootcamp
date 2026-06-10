import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict




class CelectionsInstructionGenerator(BaseInstructionGenerator):
    """Celections Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Celections指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_voters = params.get('max_voters', 20)
        self.max_bribe = params.get('max_bribe', 100)
        self.max_candidates = params.get('max_candidates', 3)
    
    def case_generator(self):
        for _ in range(100):  # 重试次数上限
            n = random.randint(1, self.max_voters)
            my_votes = random.randint(0, n)
            remaining = n - my_votes

            # 处理全票支持自己的情况
            if remaining == 0:
                return {
                    'n': n,
                    'voters': [(0,0)] * n,
                    'min_cost': 0
                }

            # 修正候选人数量生成逻辑
            max_possible_candidates = min(self.max_candidates, remaining)
            others_num = random.randint(1, max_possible_candidates)
            
            # 确保每个候选人至少获得1票
            base_counts = [1] * others_num
            remaining_after_base = remaining - others_num
            if remaining_after_base < 0:
                continue  # 无法满足最小分配条件，重新生成

            # 分配剩余票数
            for _ in range(remaining_after_base):
                idx = random.randint(0, others_num-1)
                base_counts[idx] += 1

            # 构建选民数据
            voters = [(0,0) for _ in range(my_votes)]
            for i in range(others_num):
                candidate = i + 1
                count = base_counts[i]
                # 生成贿赂成本并排序确保贪心算法有效性
                bribes = sorted([random.randint(0, self.max_bribe) for _ in range(count)], reverse=True)
                voters.extend([(candidate, b) for b in bribes])

            random.shuffle(voters)  # 随机打乱顺序

            # 计算最小成本
            min_cost = self.calculate_min_cost(voters)
            if min_cost is not None and min_cost != float('inf'):
                return {
                    'n': n,
                    'voters': voters,
                    'min_cost': min_cost
                }
        raise ValueError("无法生成有效案例，请调整参数设置")
    
    @staticmethod
    def prompt_func(question_case) -> str:
        voters = question_case['voters']
        n = question_case['n']
        input_lines = [f"{n}"]
        for ai, bi in voters:
            input_lines.append(f"{ai} {bi}")
        input_str = "\n".join(input_lines)
        prompt = (
            "你正在参与俄罗斯一个小城市的市长选举。你需要计算确保你的得票数严格超过其他所有候选人的最小贿赂金额。每个选民用两个整数表示：ai表示当前支持的候选人编号（0表示你），bi表示让该选民改投你所需的金额。\n\n"
            "输入格式：\n"
            "第一行包含整数n（选民总数）。随后n行每行两个整数ai和bi。\n\n"
            "当前问题：\n"
            f"{input_str}\n\n"
            "输出要求：\n"
            "输出一个整数表示最小花费，用[answer]和[/answer]标签包裹答案。例如：[answer]42[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_min_cost(voters):
        c0 = sum(1 for ai, _ in voters if ai == 0)
        candidate_bribes = defaultdict(list)

        # 收集贿赂成本并按候选人分组
        for ai, bi in voters:
            if ai != 0:
                candidate_bribes[ai].append(bi)

        # 对每个候选人的贿赂成本排序（降序，便于后续处理）
        for k in candidate_bribes:
            candidate_bribes[k].sort(reverse=True)

        # 预处理所有可能的贿赂方案
        all_costs = []
        total_available = 0
        for cand in candidate_bribes.values():
            all_costs.extend(cand)
            total_available += len(cand)

        # 处理无需贿赂的情况
        if not candidate_bribes:
            return 0

        # 预处理每个候选人的前缀和
        prefix_sums = {}
        for cand, costs in candidate_bribes.items():
            prefix = [0]
            s = 0
            for cost in costs:
                s += cost
                prefix.append(s)
            prefix_sums[cand] = prefix

        min_cost = float('inf')
        max_possible = c0 + total_available

        # 确定s的范围优化：s只需要到达最大候选人的当前票数+1
        max_current_votes = max(len(v) for v in candidate_bribes.values())
        s_candidates = range(max(1, max_current_votes - c0 + 1), max_possible + 1)
        if not s_candidates:
            return float('inf')

        # 计算所有可能的s值
        for s in s_candidates:
            required = s - c0
            if required <= 0:
                current_cost = 0
                if all(len(v) < s for v in candidate_bribes.values()):
                    current_cost = 0
                else:
                    continue
            else:
                total_bribes = 0
                total_obtained = 0
                remaining_costs = []

                # 第一部分：必须贿赂的选票
                for cand, costs in candidate_bribes.items():
                    needed = max(len(costs) - (s - 1), 0)
                    if needed > len(costs):
                        break
                    total_bribes += prefix_sums[cand][needed]
                    total_obtained += needed
                    remaining_costs.extend(costs[needed:])
                else:  # 正常完成循环时才执行后续逻辑
                    # 第二部分：补充需要的额外选票
                    if total_obtained >= required:
                        current_cost = total_bribes
                    else:
                        additional_needed = required - total_obtained
                        if len(remaining_costs) < additional_needed:
                            continue
                        remaining_sorted = sorted(remaining_costs)
                        current_cost = total_bribes + sum(remaining_sorted[:additional_needed])

                    if current_cost < min_cost:
                        min_cost = current_cost

        return min_cost if min_cost != float('inf') else None
