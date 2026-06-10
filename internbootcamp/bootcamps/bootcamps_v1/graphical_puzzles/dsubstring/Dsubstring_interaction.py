from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dsubstring.Dsubstring_reward_calculator import DsubstringRewardCalculator

# 导入依赖库
import random
from collections import deque
from collections import defaultdict




class DsubstringInteraction(BaseInteraction):
    """Dsubstring交互管理器"""
    
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
        score = DsubstringRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dsubstring问题！"""
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
    def has_cycle(self, n, edges):
        adj = [[] for _ in range(n)]
        in_degree = [0] * n
        for u, v in edges:
            adj[u].append(v)
            in_degree[v] += 1

        queue = deque()
        for i in range(n):
            if in_degree[i] == 0:
                queue.append(i)

        count = 0
        while queue:
            u = queue.popleft()
            count += 1
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        return count != n

    def compute_max_path(self, n, edges, letters):
        E = defaultdict(list)
        P = defaultdict(list)
        C = [0] * n

        for u, v in edges:
            E[u].append(v)
            P[v].append(u)
            C[u] += 1

        leafs = [u for u in E if len(E[u]) == 0]

        if not leafs:
            return -1

        DP = [ [0]*27 for _ in range(n) ]
        for i in range(n):
            c = ord(letters[i]) - ord('a')
            DP[i][c] = 1

        Q = deque(leafs)
        used = [False] * n

        while Q:
            u = Q.popleft()
            if used[u]:
                continue
            used[u] = True

            for c in range(27):
                max_val = 0
                for v in E[u]:
                    if DP[v][c] > max_val:
                        max_val = DP[v][c]
                DP[u][c] += max_val

            for v in P[u]:
                C[v] -= 1
                if C[v] == 0:
                    Q.append(v)

        if any(c > 0 for c in C):
            return -1
        else:
            max_value = max(max(row) for row in DP)
            return max_value
