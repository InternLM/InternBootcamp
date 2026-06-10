from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cflawedflow.Cflawedflow_reward_calculator import CflawedflowRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque

# === 源文件中的其他类 ===

class Edge:
    def __init__(self, from_, to_, w_, id_):
        self.from_ = from_
        self.to_ = to_
        self.w_ = w_
        self.id_ = id_


class CflawedflowInteraction(BaseInteraction):
    """Cflawedflow交互管理器"""
    
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
        score = CflawedflowRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cflawedflow问题！"""
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
    def _generate_connected_edges(n, m):
        parent = list(range(n+1))

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        edges = []
        existing = set()

        # Generate spanning tree to ensure connectivity
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        root = nodes[0]
        for node in nodes[1:]:
            a, b = root, node
            if a > b:
                a, b = b, a
            c = random.randint(1, 10000)
            edges.append((a, b, c))
            existing.add((a, b))
            parent[b] = a

        # Add remaining edges
        remaining = m - (n-1)
        candidates = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1) if (i, j) not in existing]
        while remaining > 0 and candidates:
            add_num = min(remaining, len(candidates))
            selected = random.sample(candidates, add_num)
            for a, b in selected:
                c = random.randint(1, 10000)
                edges.append((a, b, c))
                existing.add((a, b))
                candidates.remove((a, b))  # Prevent duplicate selection
            remaining -= add_num

        random.shuffle(edges)
        return edges[:m]

    @staticmethod
    def _generate_solution(n, edges):
        m = len(edges)
        graph = [[] for _ in range(n+1)]
        wall = [0]*(n+1)
        for idx, (a, b, c) in enumerate(edges):
            edge = Edge(a, b, c, idx)
            graph[a].append(edge)
            graph[b].append(edge)
            wall[a] += c
            wall[b] += c

        ans = [-1]*m
        win = [0]*(n+1)
        q = deque([1])

        while q:
            u = q.popleft()
            to_check = []
            for edge in graph[u]:
                if ans[edge.id_] != -1:
                    continue
                if edge.from_ == u:
                    v = edge.to_
                    ans[edge.id_] = 0
                else:
                    v = edge.from_
                    ans[edge.id_] = 1
                win[v] += edge.w_
                wall[v] -= edge.w_
                if v != n:
                    to_check.append(v)

            for v in to_check:
                if win[v] == wall[v]:
                    q.append(v)

        return ans
