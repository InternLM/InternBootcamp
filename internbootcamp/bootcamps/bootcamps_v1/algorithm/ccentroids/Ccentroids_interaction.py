from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccentroids.Ccentroids_reward_calculator import CcentroidsRewardCalculator

# 导入依赖库
import random
import re




class CcentroidsInteraction(BaseInteraction):
    """Ccentroids交互管理器"""
    
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
        score = CcentroidsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccentroids问题！"""
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
    def generate_random_tree(n):
        if n == 1:
            return []
        edges = []
        for i in range(2, n+1):
            p = random.randint(1, i-1)
            edges.append((p, i))
        random.shuffle(edges)
        return edges

    @staticmethod
    def solve_problem(n, edges):
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        # 第一次DFS寻找重心
        siz = [0]*(n+1)
        res = float('inf')
        rt = 0
        def dfs1(x, F):
            nonlocal res, rt
            siz[x] = 1
            mx = 0
            for y in adj[x]:
                if y == F:
                    continue
                dfs1(y, x)
                siz[x] += siz[y]
                mx = max(mx, siz[y])
            mx = max(mx, n - siz[x])
            if mx < res or (mx == res and x < rt):
                res = mx
                rt = x
        dfs1(1, 0)

        # 第二次DFS建立父节点关系
        siz = [0]*(n+1)
        parent = {}
        def dfs2(x, F):
            parent[x] = F
            siz[x] = 1
            for y in adj[x]:
                if y == F:
                    continue
                dfs2(y, x)
                siz[x] += siz[y]
        dfs2(rt, 0)

        # 获取直接子节点
        sub = []
        for y in adj[rt]:
            if parent[y] == rt:  # 关键修正：确保只处理子节点
                sub.append((siz[y], y))
        sub.sort(reverse=True, key=lambda x: x[0])

        ans = [0]*(n+1)
        ans[rt] = 1

        # 递归求解答案
        def solve(x, F, sum_val, pre):
            if sum_val <= n//2:
                ans[x] = 1
            for i in range(min(2, len(sub))):
                s, node = sub[i]
                if node == pre:
                    continue
                if (n - siz[x] - s) <= n//2:
                    ans[x] = 1
            for y in adj[x]:
                if y == F:
                    continue
                solve(y, x, sum_val, pre)

        # 遍历所有子节点
        for y in adj[rt]:
            if parent[y] != rt:  # 关键修正：过滤非子节点
                continue
            solve(y, rt, n - siz[y], y)

        return ans[1:n+1]
