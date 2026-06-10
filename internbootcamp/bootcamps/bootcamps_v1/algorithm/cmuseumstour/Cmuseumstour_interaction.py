from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmuseumstour.Cmuseumstour_reward_calculator import CmuseumstourRewardCalculator

# 导入依赖库
import random
from collections import deque

# === 源文件中的全局函数 ===

def calculate_answer(n, m, d, roads, schedules):
    adj = [[] for _ in range(n)]
    for u, v in roads:
        adj[u].append(v)
    open_table = [ [c == '1' for c in s] for s in schedules ]

    max_museums = 0

    visited = {}  # (current city, day in week) -> max museums count

    initial_museums = 0
    if open_table[0][0]:
        initial_museums = 1

    queue = deque()
    # State: (city, day, visited_museums_bitmask)
    initial_state = (0, 0, initial_museums, 1 << 0 if open_table[0][0] else 0)
    queue.append(initial_state)
    visited[(0, 0)] = (initial_museums, initial_state[3])

    max_museums = initial_museums

    while queue:
        u, t, count, mask = queue.popleft()

        next_t = (t + 1) % d

        for v in adj[u]:
            new_mask = mask
            new_count = count
            # Check if we can visit v's museum at next_t day
            if open_table[v][next_t] and not (mask & (1 << v)):
                new_count += 1
                new_mask |= 1 << v
            key = (v, next_t)
            if key not in visited or visited[key][0] < new_count or (visited[key][0] == new_count and visited[key][1] | new_mask != visited[key][1]):
                visited[key] = (new_count, new_mask)
                queue.append((v, next_t, new_count, new_mask))
                if new_count > max_museums:
                    max_museums = new_count

    return max_museums


class CmuseumstourInteraction(BaseInteraction):
    """Cmuseumstour交互管理器"""
    
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
        score = CmuseumstourRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cmuseumstour问题！"""
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

