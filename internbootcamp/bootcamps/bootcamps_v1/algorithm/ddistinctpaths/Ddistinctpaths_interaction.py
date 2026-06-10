from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ddistinctpaths.Ddistinctpaths_reward_calculator import DdistinctpathsRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class DdistinctpathsInteraction(BaseInteraction):
    """Ddistinctpaths交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = DdistinctpathsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ddistinctpaths问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法
    def generate_valid_full_grid(self, n, m, k):
        grid = [[0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for j in range(m):
                used = set()
                if i > 0:
                    used.add(grid[i-1][j])
                if j > 0:
                    used.add(grid[i][j-1])
                available = [c for c in range(1, k+1) if c not in used]
                if not available:
                    return None
                grid[i][j] = min(available)
        return grid

    @staticmethod
    def compute_solution(n, m, k, grid):
        if n + m > 11 or (n + m - 1) > k:
            return 0
        grid = [[cell-1 if cell !=0 else -1 for cell in row] for row in grid]
        a = [[-1]*(m+2) for _ in range(n+2)]
        for i in range(n):
            for j in range(m):
                a[i+1][j+1] = grid[i][j] if grid[i][j] != -1 else -1
        lim2 = [[0]*(m+2) for _ in range(n+2)]
        s = 0
        for i in range(1, n+1):
            for j in range(1, m+1):
                if a[i][j] != -1:
                    s |= 1 << a[i][j]
                    if i < n:
                        lim2[i][j] |= 1 << a[i][j]
                    if j < m:
                        lim2[i][j] |= 1 << a[i][j]
        for i in range(n, 0, -1):
            for j in range(m, 0, -1):
                lim2[i][j] |= lim2[i+1][j] | lim2[i][j+1]
                if a[i][j] != -1 and (lim2[i][j] & (1 << a[i][j])):
                    return 0
        v = []
        for color in range(k):
            if not (s & (1 << color)):
                v.append(color)
        if not v:
            return 1
        # DFS to compute answer
        memo = {}
        def dfs(x, y, cnt, lim):
            if x > n:
                return 1
            if y > m:
                return dfs(x+1, 1, cnt, lim)
            key = (x, y, cnt, tuple(map(tuple, lim)))
            if key in memo:
                return memo[key]
            current_lim = lim[x-1][y] | lim[x][y-1]
            total = 0
            for color in range(k):
                if a[x][y] != -1 and color != a[x][y]:
                    continue
                if current_lim & (1 << color):
                    continue
                if lim2[x][y] & (1 << color):
                    continue
                if not (s & (1 << color)):
                    if a[x][y] == -1 and (cnt >= len(v) or color > v[cnt]):
                        continue
                new_lim = [row[:] for row in lim]
                new_lim[x][y] = current_lim | (1 << color)
                new_cnt = cnt
                if a[x][y] == -1 and not (s & (1 << color)):
                    if color == v[cnt]:
                        new_cnt = min(len(v)-1, cnt + 1)
                res = dfs(x, y+1, new_cnt, new_lim)
                if a[x][y] == -1 and color in v and cnt < len(v) and color == v[cnt]:
                    total = (total + res * (len(v) - cnt)) % MOD
                else:
                    total = (total + res) % MOD
            memo[key] = total
            return total
        lim_init = [[0]*(m+2) for _ in range(n+2)]
        result = dfs(1, 1, 0, lim_init)
        return result
