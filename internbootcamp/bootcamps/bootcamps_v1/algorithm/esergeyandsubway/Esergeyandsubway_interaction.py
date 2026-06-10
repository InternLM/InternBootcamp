from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.esergeyandsubway.Esergeyandsubway_reward_calculator import EsergeyandsubwayRewardCalculator

# 导入依赖库
import random




class EsergeyandsubwayInteraction(BaseInteraction):
    """Esergeyandsubway交互管理器"""
    
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
        score = EsergeyandsubwayRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Esergeyandsubway问题！"""
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
        """
        使用Prüfer序列生成随机树。
        """
        if n == 1:
            return []
        if n == 2:
            return [(1, 2)]

        prufer = [random.randint(1, n) for _ in range(n-2)]
        degree = [0] * (n + 1)
        for node in prufer:
            degree[node] += 1

        leaves = []
        for i in range(1, n + 1):
            if degree[i] == 0:
                leaves.append(i)

        edges = []
        for node in prufer:
            leaf = leaves.pop(0)
            edges.append((leaf, node))
            degree[node] -= 1
            if degree[node] == 0:
                leaves.append(node)
            leaves.sort()

        edges.append((leaves[0], leaves[1]))
        return edges

    @staticmethod
    def solve(n, edges_list):
        """
        根据给定的树结构计算正确的结果。
        """
        adj = [[] for _ in range(n+1)]
        for a, b in edges_list:
            adj[a].append(b)
            adj[b].append(a)

        root = 1
        q = [root]
        odd = [0] * (n+1)
        even = [0] * (n+1)
        odd_size = [0] * (n+1)
        even_size = [1] * (n+1)
        rank = [0] * (n+1)
        rank[root] = 1

        i = 0
        while i < len(q):
            node = q[i]
            for v in adj[node]:
                if rank[v] == 0:
                    rank[v] = rank[node] + 1
                    q.append(v)
            i += 1

        for node in reversed(q):
            for v in adj[node]:
                if rank[v] > rank[node]:
                    odd[node] += even[v] + even_size[v]
                    even[node] += odd[v] + odd_size[v]
                    even_size[node] += odd_size[v]
                    odd_size[node] += even_size[v]

        for node in q:
            for v in adj[node]:
                if rank[v] > rank[node]:
                    deven = odd[node] - (even[v] + even_size[v]) + (odd_size[node] - even_size[v])
                    dodd = even[node] - (odd[v] + odd_size[v]) + (even_size[node] - odd_size[v])
                    even[v] += deven
                    odd[v] += dodd
                    even_size[v] = odd_size[node]
                    odd_size[v] = even_size[node]

        ans = 0
        for i in range(1, n+1):
            ans += even[i] // 2
            ans += (odd[i] + odd_size[i]) // 2
        ans = ans // 2
        return ans
