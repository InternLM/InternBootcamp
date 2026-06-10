import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EcielthecommanderVerificationTool(BaseTool):
    """Ecielthecommander验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = EcielthecommanderRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"EcielthecommanderVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法

