from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ckuroandwalkingroute.Ckuroandwalkingroute_reward_calculator import CkuroandwalkingrouteRewardCalculator

# 导入依赖库
import random
from collections import deque
from collections import defaultdict




class CkuroandwalkingrouteInteraction(BaseInteraction):
    """Ckuroandwalkingroute交互管理器"""
    
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
        score = CkuroandwalkingrouteRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ckuroandwalkingroute问题！"""
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
    def _compute_under_except(self, adj, start, end):
        """
        计算underExcept值：从start出发不经过通向end路径的子树大小
        """
        if start == end:
            return 0

        path = self._find_path(adj, start, end)
        if not path:
            return 0

        next_node = path[1] if len(path) > 1 else None
        total = 1  # 包含start自己

        for neighbor in adj[start]:
            if neighbor == next_node:
                continue

            # 计算该邻接点子树的节点数
            count = 0
            visited = {start}
            stack = [neighbor]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                count += 1
                for v in adj[node]:
                    if v not in visited:
                        stack.append(v)
            total += count

        return total

    def _find_path(self, adj, start, end):
        """
        使用BFS找到start到end的路径
        """
        parent = {}
        queue = deque([start])
        parent[start] = None

        while queue:
            u = queue.popleft()
            if u == end:
                break
            for v in adj[u]:
                if v not in parent and v != parent.get(u):
                    parent[v] = u
                    queue.append(v)

        if end not in parent:
            return []

        # 重建路径
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = parent[current]
        return path[::-1]
