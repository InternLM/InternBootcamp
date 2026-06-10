from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cilyaandthetree.Cilyaandthetree_reward_calculator import CilyaandthetreeRewardCalculator

# 导入依赖库
import random
import math
import re
from typing import List
from typing import Dict
from typing import Any
from collections import defaultdict




class CilyaandthetreeInteraction(BaseInteraction):
    """Cilyaandthetree交互管理器"""
    
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
        score = CilyaandthetreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cilyaandthetree问题！"""
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
    def _generate_valid_tree(self, n: int) -> List[List[int]]:
        """生成以1为根的合法树结构"""
        if n == 1:
            return []

        nodes = list(range(2, n+1))
        random.shuffle(nodes)
        edges = []
        connected = {1}
        for node in nodes:
            parent = random.choice(list(connected))
            edges.append([parent, node])
            connected.add(node)
        return edges

    def _compute_solution(self, n: int, a: List[int], edges: List[List[int]]) -> List[int]:
        """正确实现参考算法逻辑"""
        # 构建邻接表（1-based）
        adj = defaultdict(list)
        for x, y in edges:
            adj[x].append(y)
            adj[y].append(x)

        # 初始化数据结构
        res = [0] * (n+1)  # 1-based索引
        res[1] = a[0]
        cnt = defaultdict(int)
        max_depth = defaultdict(int)

        # 预计算根节点所有因数
        root_val = a[0]
        divisors = set()
        d = 1
        while d*d <= root_val:
            if root_val % d == 0:
                divisors.add(d)
                if d != root_val//d:
                    divisors.add(root_val//d)
            d += 1

        # 初始化因数计数
        for d in divisors:
            cnt[d] = 1

        # DFS遍历
        stack = [(1, 0, root_val)]  # (current, parent, current_gcd)
        path = []

        while stack:
            node, parent, current_gcd = stack.pop()
            path.append(node)

            # 计算当前路径长度
            current_depth = len(path)

            # 计算当前节点的可能最大值
            max_val = current_gcd
            for d in sorted(divisors, reverse=True):
                if cnt[d] >= current_depth - 1:
                    max_val = max(max_val, d)
                    break

            res[node] = max_val

            # 处理子节点
            for child in adj[node]:
                if child == parent:
                    continue

                # 计算子节点的GCD
                child_gcd = math.gcd(current_gcd, a[child-1])

                # 更新因数计数
                for d in divisors:
                    if a[child-1] % d == 0:
                        cnt[d] += 1

                stack.append((child, node, child_gcd))

            # 回溯时恢复计数
            if path:
                last_node = path.pop()
                for d in divisors:
                    if a[last_node-1] % d == 0:
                        cnt[d] = max(cnt[d]-1, 0)

        return [res[i] for i in range(1, n+1)]
