import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
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

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DnudistbeachVerificationTool(BaseTool):
    """Dnudistbeach验证工具"""
    
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
            score = DnudistbeachRewardCalculator.verify_score(
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
            logger.error(f"DnudistbeachVerificationTool执行错误: {str(e)}")
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

