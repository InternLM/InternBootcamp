import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CfootballRewardCalculator(BaseRewardCalculator):
    """Cfootball奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r"\[answer\](.*?)\[/answer\]", output, re.DOTALL)
        if not matches:
            return None
        return matches[-1].strip()
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity["n"]
        k_val = identity["k"]
        # 判断当前案例是否有解
        case_has_solution = (n == 1 and k_val == 0) or (n > 1 and k_val <= (n - 1) // 2)
        sol_str = str(solution).strip()

        if sol_str == "-1":
            return not case_has_solution  # 模型输出-1且案例无解时正确

        if not case_has_solution:
            return False  # 案例无解但模型未输出-1

        # 解析模型输出的比赛记录
        lines = sol_str.split("\n")
        if not lines:
            return False

        try:
            m = int(lines[0])
        except ValueError:
            return False

        expected_m = n * k_val  # 每队赢k次，总比赛数应为n*k
        if m != expected_m:
            return False

        if n == 1 and k_val == 0:
            # 特例：仅一队且k=0时应无比赛
            return m == 0 and len(lines) == 1

        if len(lines) != m + 1:
            return False  # 比赛数量与声明不符

        matches = []
        # 验证每行比赛记录合法性
        for line in lines[1:]:
            parts = line.strip().split()
            if len(parts) != 2:
                return False
            try:
                a, b = int(parts[0]), int(parts[1])
            except ValueError:
                return False
            if a == b or a < 1 or a > n or b < 1 or b > n:
                return False
            matches.append((a, b))

        # 检查每对球队是否至多比赛一次
        pairs = set()
        for a, b in matches:
            pair = tuple(sorted((a, b)))  # 标准化比赛对表示
            if pair in pairs:
                return False
            pairs.add(pair)

        # 检查每队胜利次数是否为k
        win_counts = {team: 0 for team in range(1, n + 1)}
        for a, _ in matches:
            win_counts[a] += 1

        return all(count == k_val for count in win_counts.values())
    
    # 其他额外方法

