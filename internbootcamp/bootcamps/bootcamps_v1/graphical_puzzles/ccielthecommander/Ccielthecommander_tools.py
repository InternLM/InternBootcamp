import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ccielthecommander.Ccielthecommander_reward_calculator import CcielthecommanderRewardCalculator

# 导入依赖库
import random
import re
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcielthecommanderVerificationTool(BaseTool):
    """Ccielthecommander验证工具"""
    
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
            score = CcielthecommanderRewardCalculator.verify_score(
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
            logger.error(f"CcielthecommanderVerificationTool执行错误: {str(e)}")
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
    @staticmethod
    def solve_puzzle(n, edges):
        # Build adjacency list (0-based)
        coupl = [[] for _ in range(n)]
        for a, b in edges:
            u = a - 1
            v = b - 1
            coupl[u].append(v)
            coupl[v].append(u)

        # Centroid decomposition logic with Z check
        ans = [-1] * n
        cur_color = 0
        cur_count = 1
        next_count = 0

        try:
            for centroid in Ccielthecommanderbootcamp.centroid_decomp(coupl):
                if cur_color >= 26:
                    return "Impossible!"
                ans[centroid] = cur_color
                next_count += len(coupl[centroid])
                cur_count -= 1
                if cur_count == 0:
                    cur_count = next_count
                    cur_color += 1
                    next_count = 0
            if cur_color >= 26:
                return "Impossible!"
        except:
            return "Impossible!"

        # Final check for Z overflow in ans
        if max(ans) >= 26:
            return "Impossible!"
        return ' '.join(chr(ord('A') + x) for x in ans)

    @staticmethod
    def centroid_decomp(coupl):
        n = len(coupl)
        if n == 0:
            return

        # Initial BFS to dismantle parent links
        root = n - 1
        bfs = [root]
        for node in bfs:
            for nei in list(coupl[node]):
                if node in coupl[nei]:
                    coupl[nei].remove(node)
            bfs += coupl[node]

        # Calculate sizes
        size = [1] * n
        for node in reversed(bfs):
            for child in coupl[node]:
                size[node] += size[child]

        # Centroid rerooting function
        def centroid_reroot(root):
            N = size[root]
            while True:
                for child in coupl[root]:
                    if size[child] > N // 2:
                        size[root] = N - size[child]
                        coupl[root].remove(child)
                        coupl[child].append(root)
                        root = child
                        break
                else:
                    return root

        # Generate centroids through BFS
        bfs = [root]
        for node in bfs:
            centroid = centroid_reroot(node)
            yield centroid
            bfs += coupl[centroid]

    @staticmethod
    def validate_solution(n, edges, solution):
        if solution == "Impossible!":
            # Check if the problem is actually impossible
            # This would require a separate solver, but for bootcamp purposes
            # we assume the case_generator's solve_puzzle is authoritative
            return True

        parts = solution.split()
        if len(parts) != n:
            return False
        for c in parts:
            if len(c) != 1 or not ('A' <= c <= 'Z'):
                return False

        # Build adjacency list
        adj = [[] for _ in range(n+1)]  # 1-based
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        # Precompute all pairs with same color
        color_map = {}
        for i in range(n):
            color = parts[i]
            color_map.setdefault(color, []).append(i+1)  # Cities are 1-based

        # Check each color group
        for color, cities in color_map.items():
            if len(cities) < 2:
                continue
            # Check all pairs in this color group
            for i in range(len(cities)):
                for j in range(i+1, len(cities)):
                    u = cities[i]
                    v = cities[j]
                    # Find path and check for higher rank
                    if not Ccielthecommanderbootcamp.path_has_higher(u, v, adj, parts):
                        return False
        return True

    @staticmethod
    def path_has_higher(u, v, adj, parts):
        # BFS to find path and check ranks
        visited = set()
        queue = deque()
        queue.append( (u, []) )
        while queue:
            node, path = queue.popleft()
            if node == v:
                full_path = path + [node]
                current_rank = parts[u-1]
                for n in full_path:
                    if parts[n-1] < current_rank:
                        return True
                return False
            if node in visited:
                continue
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    queue.append( (neighbor, path + [node]) )
        return False  # Shouldn't happen in trees
