from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ecielthecommander.Ecielthecommander_reward_calculator import EcielthecommanderRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def generate_tree(n):
    """Generate a random tree using Prüfer sequence with shuffled node labels."""
    if n == 1: return []
    labels = list(range(1, n+1))
    random.shuffle(labels)
    
    if n == 2: return [(labels[0], labels[1])]
    
    prufer = [random.randint(0, n-2) for _ in range(n-2)]
    node_count = [0] * n
    for node in prufer: node_count[node] += 1
    
    edges = []
    leaf = None
    for node in prufer:
        if leaf is None:
            for i in range(n):
                if node_count[i] == 0 and i != node:
                    leaf = i
                    break
        edges.append((leaf, node))
        node_count[leaf] = -1
        node_count[node] -= 1
        if node_count[node] == 0 and leaf > node:
            leaf = node
        else:
            leaf = None
    
    last_nodes = [i for i in range(n) if node_count[i] != -1]
    edges.append((last_nodes[0], last_nodes[1]))
    
    return [(labels[a], labels[b]) for a, b in edges]



# === 源文件中的其他类 ===

class SolutionValidator:
    def __init__(self, n, edges, solution):
        self.n = n
        self.adj = [[] for _ in range(n+1)]
        for a, b in edges:
            self.adj[a].append(b)
            self.adj[b].append(a)
        self.rank = solution.split() if solution != "Impossible!" else []
        self.parent = [0]*(n+1)
        self.depth = [0]*(n+1)
        self._build_lca(1, 0)

    def _build_lca(self, u, p):
        stack = [(u, p, False)]
        while stack:
            u, p, visited = stack.pop()
            if visited:
                for v in self.adj[u]:
                    if v != p and v != self.parent[v]:
                        self.depth[v] = self.depth[u] + 1
                        self.parent[v] = u
            else:
                stack.append((u, p, True))
                for v in self.adj[u]:
                    if v != p:
                        stack.append((v, u, False))

    def _lca(self, u, v):
        while u != v:
            if self.depth[u] > self.depth[v]:
                u = self.parent[u]
            else:
                v = self.parent[v]
        return u

    def validate(self):
        if self.rank == ["Impossible!"]:
            return self._validate_impossible()
        
        if len(self.rank) != self.n:
            return False
        ranks = {}
        for i, r in enumerate(self.rank):
            if len(r) != 1 or not r.isupper():
                return False
            ranks[i+1] = r

        # Check all pairs with same rank
        rank_map = defaultdict(list)
        for node in range(1, self.n+1):
            rank_map[ranks[node]].append(node)

        for r, nodes in rank_map.items():
            if len(nodes) < 2: 
                continue
            # Check all pairs
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    a, b = nodes[i], nodes[j]
                    lca = self._lca(a, b)
                    path = []
                    while a != lca:
                        path.append(a)
                        a = self.parent[a]
                    path.append(lca)
                    temp = []
                    while b != lca:
                        temp.append(b)
                        b = self.parent[b]
                    path += reversed(temp)
                    # Check path
                    has_higher = False
                    for node in path:
                        if ranks[node] < r:
                            has_higher = True
                            break
                    if not has_higher:
                        return False
        return True

    def _validate_impossible(self):
        try:
            gen = SolutionGenerator(self.n, self.adj[1:])
            solution = gen.generate()
            return solution == "Impossible!"
        except:
            return False


class EcielthecommanderInteraction(BaseInteraction):
    """Ecielthecommander交互管理器"""
    
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
        score = EcielthecommanderRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ecielthecommander问题！"""
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

