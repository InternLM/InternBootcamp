from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.enastyaandunexpectedguest.Enastyaandunexpectedguest_reward_calculator import EnastyaandunexpectedguestRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def correct_solution(n, m, d, g, r):
    d_sorted = sorted(d)
    # Check if any adjacent islands exceed g distance
    for i in range(1, len(d_sorted)):
        if d_sorted[i] - d_sorted[i-1] > g:
            return -1
    m = len(d_sorted)
    INF = float('inf')
    dp = [[INF] * (g + 1) for _ in range(m)]
    dp[0][0] = 0
    heap = []
    import heapq
    heapq.heappush(heap, (0, 0, 0))  # (cycles, u, rem)

    while heap:
        cycles, u, rem = heapq.heappop(heap)
        if cycles > dp[u][rem]:
            continue
        for dv in [-1, 1]:
            v = u + dv
            if 0 <= v < m:
                distance = abs(d_sorted[u] - d_sorted[v])
                new_rem = rem + distance
                if new_rem > g:
                    continue
                if new_rem == g:
                    new_cycles = cycles + 1
                    new_r = 0
                else:
                    new_cycles = cycles
                    new_r = new_rem
                if dp[v][new_r] > new_cycles:
                    dp[v][new_r] = new_cycles
                    heapq.heappush(heap, (new_cycles, v, new_r))
    min_time = INF
    for i in range(m):
        time_needed = n - d_sorted[i]
        if time_needed <= g and dp[i][0] != INF:
            total_time = dp[i][0] * (g + r) + time_needed
            if total_time < min_time:
                min_time = total_time
    return min_time if min_time != INF else -1


class EnastyaandunexpectedguestInteraction(BaseInteraction):
    """Enastyaandunexpectedguest交互管理器"""
    
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
        score = EnastyaandunexpectedguestRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Enastyaandunexpectedguest问题！"""
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

