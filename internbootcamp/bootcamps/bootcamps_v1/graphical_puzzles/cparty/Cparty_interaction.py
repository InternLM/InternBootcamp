from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cparty.Cparty_reward_calculator import CpartyRewardCalculator

# 导入依赖库
import re
import random
from itertools import combinations




class CpartyInteraction(BaseInteraction):
    """Cparty交互管理器"""
    
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
        score = CpartyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cparty问题！"""
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
    def _generate_connected_graph(self, n):
        """改进的连通图生成算法"""
        if n == 1:
            return []

        edges = set()
        nodes = list(range(1, n+1))
        visited = {nodes[0]}
        unvisited = set(nodes[1:])

        # Prim算法生成生成树
        while unvisited:
            u = random.choice(list(visited))
            v = random.choice(list(unvisited))
            edges.add(frozenset((u, v)))
            visited.add(v)
            unvisited.remove(v)

        # 添加随机边 (至少添加n-1条边)
        all_possible = {frozenset(e) for e in combinations(nodes, 2)}
        remaining = list(all_possible - edges)
        random.shuffle(remaining)

        extra = random.randint(0, len(remaining))
        edges.update(remaining[:extra])

        return sorted([sorted(list(e)) for e in edges])

    def _calculate_optimal_solution(self, n, edges):
        """基于位运算的高效算法（参考原题解）"""
        if n == 1:
            return 0, []

        # 转换为0-based邻接表
        adj = [0] * n
        for u, v in edges:
            u_idx = u - 1
            v_idx = v - 1
            adj[u_idx] |= 1 << v_idx
            adj[v_idx] |= 1 << u_idx

        # 添加自环
        for i in range(n):
            adj[i] |= 1 << i

        # 预处理覆盖关系
        full_mask = (1 << n) - 1
        if all(mask == full_mask for mask in adj):
            return 0, []

        # 初始化neigh数组
        max_mask = 1 << n
        coverage = [0] * max_mask
        for i in range(n):
            coverage[1 << i] = adj[i]

        # 预处理所有mask的覆盖关系
        for mask in range(max_mask):
            for i in range(n):
                if (mask & (1 << i)) and (coverage[mask ^ (1 << i)] & (1 << i)):
                    coverage[mask] = coverage[mask ^ (1 << i)] | adj[i]

        # 寻找最小集合
        best_mask = full_mask
        min_steps = n
        for mask in range(max_mask):
            if coverage[mask] == full_mask:
                cnt = bin(mask).count('1')
                if cnt < min_steps:
                    min_steps = cnt
                    best_mask = mask

        solution = [i+1 for i in range(n) if (best_mask & (1 << i))]
        return min_steps, solution
