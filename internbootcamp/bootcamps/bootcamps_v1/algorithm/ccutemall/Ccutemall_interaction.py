from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccutemall.Ccutemall_reward_calculator import CcutemallRewardCalculator

# 导入依赖库
import random
import re




class CcutemallInteraction(BaseInteraction):
    """Ccutemall交互管理器"""
    
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
        score = CcutemallRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccutemall问题！"""
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
    def generate_tree(self, n):
        """使用改进的Prüfer序列生成更平衡的树结构"""
        if n == 1:
            return []
        if n == 2:
            return [(1, 2)]

        # 生成更平衡的Prüfer序列
        prufer = []
        for _ in range(n-2):
            # 偏好选择中间节点
            prufer.append(random.randint(max(1, n//4), min(n, 3*n//4)))

        degree = [1]*(n+1)
        for node in prufer:
            degree[node] += 1

        edges = []
        for node in prufer:
            for v in range(1, n+1):
                if degree[v] == 1:
                    edges.append((node, v))
                    degree[node] -= 1
                    degree[v] -= 1
                    break

        # 处理剩余节点时保持随机性
        remaining = [v for v in range(1, n+1) if degree[v] == 1]
        edges.append((remaining.pop(), remaining.pop()))

        # 随机打乱边并确保节点顺序
        random.shuffle(edges)
        return [(u, v) if u < v else (v, u) for u, v in edges]

    def _calculate_solution(self, n, edges):
        """修正的DFS解法"""
        if n % 2 != 0:
            return -1

        # 构建邻接表
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        self.count = 0

        def dfs(node, parent):
            size = 1
            for neighbor in adj[node]:
                if neighbor == parent:
                    continue
                child_size = dfs(neighbor, node)
                size += child_size
                if child_size % 2 == 0:
                    self.count += 1
            return size

        total_size = dfs(1, -1)
        # 验证总大小
        return self.count if total_size % 2 == 0 else -1
