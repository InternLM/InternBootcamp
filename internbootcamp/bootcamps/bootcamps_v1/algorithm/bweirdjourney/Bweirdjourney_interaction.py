from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bweirdjourney.Bweirdjourney_reward_calculator import BweirdjourneyRewardCalculator

# 导入依赖库
import random
import re




class BweirdjourneyInteraction(BaseInteraction):
    """Bweirdjourney交互管理器"""
    
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
        score = BweirdjourneyRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Bweirdjourney问题！"""
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
    def calculate_good_paths(n, m, edges):
        # 严格遵循参考代码逻辑
        special = 0
        found = [1] * n
        coupl = [[] for _ in range(n)]

        for u, v in edges:
            u0 = u - 1
            v0 = v - 1
            found[u0] = 0
            found[v0] = 0
            if u0 != v0:
                coupl[u0].append(v0)
                coupl[v0].append(u0)
            else:
                special += 1

        # 连通性检查
        root = 0
        while root < n and found[root]:
            root += 1

        if root < n:
            found[root] = 1
            bfs = [root]
            for node in bfs:
                for nei in coupl[node]:
                    if not found[nei]:
                        found[nei] = 1
                        bfs.append(nei)

        if not all(found):
            return 0

        # 计算结果
        sum_degree = sum(len(c)*(len(c)-1) for c in coupl) // 2
        sum_special = special * (special-1) // 2
        sum_mixed = special * (m - special)
        return sum_degree + sum_special + sum_mixed
