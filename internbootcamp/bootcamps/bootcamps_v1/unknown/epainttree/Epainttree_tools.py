import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.unknown.epainttree.Epainttree_reward_calculator import EpainttreeRewardCalculator

# 导入依赖库
import random
import functools
from collections import defaultdict

# === 源文件中的全局函数 ===

def generate_random_tree_edges(n):
    if n == 1:
        return []
    if n == 2:
        return [(1, 2)]
    prufer = [random.randint(1, n) for _ in range(n-2)]
    degree = defaultdict(int)
    for node in prufer:
        degree[node] += 1
    leaves = []
    for v in range(1, n+1):
        if degree[v] == 0:
            leaves.append(v)
    edges = []
    for node in prufer:
        leaf = leaves.pop(0)
        edges.append((leaf, node))
        degree[leaf] -= 1
        degree[node] -= 1
        if degree[node] == 0:
            leaves.append(node)
        leaves.sort()
    edges.append((leaves[0], leaves[1]))
    edges = [tuple(sorted(e)) for e in edges]
    return edges[:n-1]

def generate_points(n, min_coord=-10**9, max_coord=10**9):
    xs = random.sample(range(min_coord, max_coord + 1), n)
    ys = [x**2 + random.randint(-1000, 1000) for x in xs]
    return list(zip(xs, ys))

def generate_solution(n, edges, points):
    g = [[] for _ in range(n)]
    for u, v in edges:
        u0 = u - 1
        v0 = v - 1
        g[u0].append(v0)
        g[v0].append(u0)
    p_list = [{'x': x, 'y': y, 'id': i} for i, (x, y) in enumerate(points)]
    size = [1] * n

    def dfs(v, parent):
        total = 1
        for to in g[v]:
            if to != parent:
                total += dfs(to, v)
        size[v] = total
        return total
    dfs(0, -1)
    sorted_p = sorted(p_list, key=lambda pt: (-pt['y'], pt['x']))
    ans = [0] * n

    def rec(v, pts, parent):
        if not pts:
            return
        current = pts[0]
        ans[current['id']] = v
        remaining = pts[1:]
        if not remaining:
            return
        gx, gy = current['x'], current['y']
        def compare(a, b):
            val = (a['x'] - gx) * (b['y'] - gy) - (b['x'] - gx) * (a['y'] - gy)
            return -1 if val > 0 else 1 if val < 0 else 0
        remaining_sorted = sorted(remaining, key=functools.cmp_to_key(compare))
        cur = 0
        for to in g[v]:
            if to != parent:
                subset = remaining_sorted[cur:cur + size[to]]
                cur += size[to]
                rec(to, subset, v)
    rec(0, sorted_p, -1)
    return [ans[i] + 1 for i in range(n)]

def segments_intersect(a, b, c, d):
    def ccw(A, B, C):
        return (B[0]-A[0])*(C[1]-A[1]) - (B[1]-A[1])*(C[0]-A[0])
    ccw1 = ccw(a, b, c)
    ccw2 = ccw(a, b, d)
    ccw3 = ccw(c, d, a)
    ccw4 = ccw(c, d, b)
    
    if (ccw1 * ccw2 < 0) and (ccw3 * ccw4 < 0):
        return True
    
    def on_segment(p, a, b):
        return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])) and \
               (min(a[1], b[1]) <= p[1] <= max(a[1], b[1])) and \
               (ccw(a, b, p) == 0)
    
    return on_segment(c, a, b) or on_segment(d, a, b) or \
           on_segment(a, c, d) or on_segment(b, c, d)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EpainttreeVerificationTool(BaseTool):
    """Epainttree验证工具"""
    
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
            score = EpainttreeRewardCalculator.verify_score(
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
            logger.error(f"EpainttreeVerificationTool执行错误: {str(e)}")
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

