from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.ccontinuouscity.Ccontinuouscity_reward_calculator import CcontinuouscityRewardCalculator

# 导入依赖库
import random
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Set




class CcontinuouscityInteraction(BaseInteraction):
    """Ccontinuouscity交互管理器"""
    
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
        score = CcontinuouscityRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccontinuouscity问题！"""
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
    def construct_valid_structure(self, L: int, R: int) -> Tuple[bool, Optional[Dict]]:
        """实现完整的结构构造逻辑"""
        n = 32
        edges = []
        cl = [0] * (n-1)
        cr = [1] * (n-1)

        # 初始化第一个块
        edges.append((1, n, L))
        current_L = L + 1

        for vi in range(1, 30):  # 构造中间块
            if current_L > R:
                break

            max_step = min(1 << (vi-1), R - current_L + 1)
            if max_step <= 0:
                break

            cl[vi] = cr[vi-1]
            cr[vi] = cl[vi]

            # 连接所有之前的块
            for j in range(vi-1, -1, -1):
                delta = cr[j] - cl[j]
                if cr[vi] + delta <= cl[vi] + max_step:
                    edges.append((j+1, vi+1, cr[vi] - cl[j]))
                    cr[vi] += delta

            # 添加到终点的边
            edge_weight = current_L - cl[vi]
            edges.append((vi+1, n, edge_weight))
            current_L += max_step

        if current_L - 1 < R:
            return False, None

        return True, {
            'n': n,
            'm': len(edges),
            'edges': edges
        }

    @staticmethod
    def validate_paths(n: int, edges: List[Tuple[int,int,int]], L: int, R: int) -> bool:
        """优化的路径验证算法"""
        # 构建邻接表
        adj = [[] for _ in range(n+1)]
        edge_map = {}
        for a, b, c in edges:
            adj[a].append((b, c))
            edge_map[(a,b)] = c

        # 使用动态规划计算所有路径长度
        dp = [set() for _ in range(n+1)]
        dp[1].add(0)

        for u in range(1, n+1):
            if not dp[u]:
                continue
            for v, w in adj[u]:
                dp[v].update({path_len + w for path_len in dp[u]})

        all_lengths = dp[n]
        if not all_lengths:
            return False

        # 检查范围
        min_len = min(all_lengths)
        max_len = max(all_lengths)
        if min_len != L or max_len != R:
            return False

        # 检查连续性和唯一性
        expected = set(range(L, R+1))
        return all_lengths == expected
