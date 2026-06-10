from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eparty.Eparty_reward_calculator import EpartyRewardCalculator

# 导入依赖库
import random
from collections import deque
import re




class EpartyInteraction(BaseInteraction):
    """Eparty交互管理器"""
    
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
        score = EpartyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Eparty问题！"""
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
    @staticmethod
    def _generate_connected_graph(n):
        edges = set()
        nodes = list(range(1, n+1))
        random.shuffle(nodes)

        # Generate a spanning tree
        for i in range(1, n):
            j = random.randint(0, i-1)
            u, v = sorted((nodes[j], nodes[i]))
            edges.add((u, v))

        # Add additional edges
        all_edges = [(u, v) for u in range(1, n+1) for v in range(u+1, n+1)]
        remaining = [e for e in all_edges if e not in edges]
        max_possible = n * (n-1) // 2
        m = random.randint(n-1, max_possible)
        edges.update(random.sample(remaining, k=m - (n-1)))

        return sorted(edges)

    @staticmethod
    def _solve_min_steps(n, edges):
        edges_list = [(u, v) for u in range(1, n+1) for v in range(u+1, n+1)]
        edge_to_bit = {e: i for i, e in enumerate(edges_list)}

        initial_mask = 0
        for u, v in edges:
            initial_mask |= 1 << edge_to_bit[(u, v) if u < v else (v, u)]

        target = (1 << len(edges_list)) - 1
        if initial_mask == target:
            return 0

        visited = {initial_mask: 0}
        queue = deque([(initial_mask, 0)])

        while queue:
            mask, steps = queue.popleft()

            for a in range(1, n+1):
                friends = set()
                for u in range(1, n+1):
                    if u == a:
                        continue
                    e = tuple(sorted((a, u)))
                    if mask & (1 << edge_to_bit[e]):
                        friends.add(u)

                friends.add(a)
                new_mask = mask
                for i in friends:
                    for j in friends:
                        if i < j:
                            new_mask |= 1 << edge_to_bit[(i, j)]

                if new_mask == target:
                    return steps + 1
                if new_mask not in visited or steps + 1 < visited[new_mask]:
                    visited[new_mask] = steps + 1
                    queue.append((new_mask, steps + 1))

        return n  # Fallback
