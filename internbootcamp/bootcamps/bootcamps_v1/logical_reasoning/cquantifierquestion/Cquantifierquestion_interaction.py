from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cquantifierquestion.Cquantifierquestion_reward_calculator import CquantifierquestionRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CquantifierquestionInteraction(BaseInteraction):
    """Cquantifierquestion交互管理器"""
    
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
        score = CquantifierquestionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cquantifierquestion问题！"""
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
    @classmethod
    def reference_solution(cls, identity):
        # 完全复制参考代码逻辑
        def toposort(graph):
            n = len(graph)
            res = []
            found = [0]*n

            for i in range(n):
                if found[i]:
                    continue
                stack = [i]
                while stack:
                    node = stack.pop()
                    if node < 0:
                        res.append(~node)
                    elif not found[node]:
                        found[node] = 1
                        stack.append(~node)
                        for nei in graph[node]:
                            if not found[nei]:
                                stack.append(nei)

            # Check cycle
            found = [0]*n
            for node in res:
                if found[node]:
                    return None
                stack = [node]
                found[node] = 1
                while stack:
                    current = stack.pop()
                    for nei in graph[current]:
                        if found[nei]:
                            return None
                        if not found[nei]:
                            found[nei] = 1
                            stack.append(nei)
            return res[::-1]

        n = identity['n']
        edges = identity['edges']
        coupl1 = [[] for _ in range(n)]
        coupl2 = [[] for _ in range(n)]
        for j, k in edges:
            u = j - 1
            v = k - 1
            coupl1[u].append(v)
            coupl2[v].append(u)

        order = toposort(coupl1)
        if order is None:
            return -1

        seen1 = list(range(n))
        seen2 = list(range(n))

        for node in order:
            for nei in coupl1[node]:
                if seen1[nei] > seen1[node]:
                    seen1[nei] = seen1[node]

        for node in reversed(order):
            for nei in coupl2[node]:
                if seen2[nei] > seen2[node]:
                    seen2[nei] = seen2[node]

        seen = [(seen1[i] == i and seen2[i] == i) for i in range(n)]
        count = sum(seen)
        if count == 0:
            return -1
        quant = ''.join('A' if c else 'E' for c in seen)
        return (count, quant)
