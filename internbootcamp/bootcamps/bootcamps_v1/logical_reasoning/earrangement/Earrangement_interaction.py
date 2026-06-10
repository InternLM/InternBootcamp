from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.earrangement.Earrangement_reward_calculator import EarrangementRewardCalculator

# 导入依赖库
import re
import random
from collections import deque

# === 源文件中的全局函数 ===

def is_dag(edges, n_nodes):
    adj = [[] for _ in range(n_nodes + 1)]
    in_degree = [0] * (n_nodes + 1)
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
    queue = deque()
    for node in range(1, n_nodes + 1):
        if in_degree[node] == 0:
            queue.append(node)
    visited = 0
    while queue:
        u = queue.popleft()
        visited += 1
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    return visited == n_nodes

def calculate_count(n, ls, pref):
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1 << n):
        if dp[mask] == 0:
            continue
        cnt = bin(mask).count('1')
        for i in range(n):
            if pref[i] != -1 and pref[i] != (n - cnt - 1):
                continue
            if (ls[i] & mask) != ls[i]:
                continue
            if (mask & (1 << i)) != 0:
                continue
            new_mask = mask | (1 << i)
            dp[new_mask] += dp[mask]
    return dp[(1 << n) - 1]

def solve_puzzle(n, y, m, constraints):
    original_y = y
    y -= 2000
    if y <= 0:
        return "The times have changed"
    ls = [0] * n
    for u, v in constraints:
        ai = u - 1
        bi_seat = v - 1
        ls[ai] |= 1 << bi_seat
    pref = [-1] * n
    for i in range(n):
        while True:
            pref[i] += 1
            if pref[i] >= n:
                return "The times have changed"
            current_pref = pref[:i+1] + [-1] * (n - i - 1)
            current_count = calculate_count(n, ls, current_pref)
            if current_count < y:
                y -= current_count
            else:
                break
    arrangement = [str(p + 1) for p in pref]
    return ' '.join(arrangement)


class EarrangementInteraction(BaseInteraction):
    """Earrangement交互管理器"""
    
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
        score = EarrangementRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Earrangement问题！"""
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

