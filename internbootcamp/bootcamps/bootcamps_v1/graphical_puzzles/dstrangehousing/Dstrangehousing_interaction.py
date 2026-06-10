from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dstrangehousing.Dstrangehousing_reward_calculator import DstrangehousingRewardCalculator

# 导入依赖库
import random
from collections import deque




class DstrangehousingInteraction(BaseInteraction):
    """Dstrangehousing交互管理器"""
    
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
        score = DstrangehousingRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dstrangehousing问题！"""
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
    def _generate_valid_case(self):
        """生成保证有解的连通二分图"""
        n = random.randint(3, self.max_houses)
        partition = {i: i%2 for i in range(1, n+1)}  # 简单二分

        # 确保图连通
        edges = []
        visited = set([1])
        queue = deque([1])

        while len(visited) < n:
            u = queue.popleft()
            candidates = [v for v in range(1, n+1) 
                        if v not in visited and partition[v] != partition[u]]
            if candidates:
                v = random.choice(candidates)
                edges.append((u, v))
                visited.add(v)
                queue.append(v)
            else:  # 添加跨分区边保持连通
                for v in range(1, n+1):
                    if v not in visited and partition[v] == partition[u]:
                        edges.append((u, v))
                        visited.add(v)
                        queue.append(v)
                        break

        # 添加额外边（保持二分性）
        possible_edges = []
        for u in range(1, n):
            for v in range(u+1, n+1):
                if partition[u] != partition[v] and (u, v) not in edges:
                    possible_edges.append((u, v))

        add_num = min(len(possible_edges), self.max_paths - len(edges))
        edges.extend(random.sample(possible_edges, add_num))

        return {'n': n, 'm': len(edges), 'edges': edges}

    def _generate_invalid_case(self):
        """生成包含奇数环的不可解案例"""
        cycle_size = random.choice([3, 5, 7])
        n = cycle_size
        edges = [(i, i%cycle_size +1) for i in range(1, cycle_size+1)]

        # 添加额外边保持连通
        for _ in range(random.randint(0, 3)):
            u = random.randint(1, n)
            v = random.randint(1, n)
            if u != v and (u, v) not in edges and (v, u) not in edges:
                edges.append((u, v))

        return {'n': n, 'm': len(edges), 'edges': edges}

    @classmethod
    def _is_bipartite(cls, edges, n):
        """判断是否为二分图（可解条件）"""
        color = {}
        adj = {u: [] for u in range(1, n+1)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        for u in range(1, n+1):
            if u not in color:
                queue = deque([u])
                color[u] = 0
                while queue:
                    current = queue.popleft()
                    for neighbor in adj[current]:
                        if neighbor not in color:
                            color[neighbor] = color[current] ^ 1
                            queue.append(neighbor)
                        elif color[neighbor] == color[current]:
                            return False
        return True
