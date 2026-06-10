from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dnudistbeach.Dnudistbeach_reward_calculator import DnudistbeachRewardCalculator

# 导入依赖库
import random
import re
from collections import deque

# === 源文件中的全局函数 ===

def generate_valid_graph(n, m):
    """生成每个节点度数至少为1的图（不要求连通）"""
    if n < 2:
        raise ValueError("n must be at least 2")
    if m < n//2:
        m = max(m, n//2)  # 保证足够的最小边数
    
    edges = set()
    nodes = list(range(1, n+1))
    random.shuffle(nodes)
    
    # 保证每个节点至少有一个边
    remaining = nodes.copy()
    while remaining:
        if len(remaining) == 1:
            # 最后一个节点随机连接到已有节点
            node = remaining.pop()
            candidates = [x for x in nodes if x != node]
            if not candidates:
                raise ValueError("Can't create valid graph")
            neighbor = random.choice(candidates)
            edge = tuple(sorted((node, neighbor)))
            edges.add(edge)
        else:
            a = remaining.pop()
            b = remaining.pop()
            edge = tuple(sorted((a, b)))
            edges.add(edge)
    
    # 添加剩余边
    possible_edges = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1) if (i, j) not in edges]
    while len(edges) < m and possible_edges:
        edge = possible_edges.pop(random.randint(0, len(possible_edges)-1))
        edges.add(edge)
    
    return sorted(edges)[:m]

def solve_case(n, m, k, fortresses, roads):
    bad = {f-1 for f in fortresses}
    adj = [[] for _ in range(n)]
    
    for a, b in roads:
        a0, b0 = a-1, b-1
        adj[a0].append(b0)
        adj[b0].append(a0)
    
    total_degree = [len(neighbors) for neighbors in adj]
    good_degree = [len(neighbors) for neighbors in adj]
    
    for u in bad:
        for v in adj[u]:
            good_degree[v] -= 1
    
    low, high = 0.0, 1.0
    best_solution = []
    
    for _ in range(50):
        mid = (low + high) / 2
        removed = set()
        current_good = good_degree.copy()
        queue = deque()
        
        for city in range(n):
            if city not in bad and total_degree[city] > 0:
                ratio = current_good[city] / total_degree[city]
                if ratio <= mid - 1e-9:
                    queue.append(city)
                    removed.add(city)
        
        temp_removed = set(removed)
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in bad and v not in temp_removed:
                    current_good[v] -= 1
                    if current_good[v]/total_degree[v] <= mid - 1e-9:
                        queue.append(v)
                        temp_removed.add(v)
        
        valid_cities = [city for city in range(n) if city not in bad and city not in temp_removed]
        if valid_cities:
            low = mid
            best_solution = [c+1 for c in valid_cities]
        else:
            high = mid
    
    return best_solution


class DnudistbeachInteraction(BaseInteraction):
    """Dnudistbeach交互管理器"""
    
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
        score = DnudistbeachRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dnudistbeach问题！"""
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

