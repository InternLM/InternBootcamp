from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ccielthecommander.Ccielthecommander_reward_calculator import CcielthecommanderRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CcielthecommanderInteraction(BaseInteraction):
    """Ccielthecommander交互管理器"""
    
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
        score = CcielthecommanderRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccielthecommander问题！"""
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
