from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dskills.Dskills_reward_calculator import DskillsRewardCalculator

# 导入依赖库
import random
import re




class DskillsInteraction(BaseInteraction):
    """Dskills交互管理器"""
    
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
        score = DskillsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dskills问题！"""
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
    def compute_max_force(n, A, cf, cm, m, a_initial):
        sorted_a = sorted(a_initial)
        total = sum(sorted_a)

        # 处理全满的特殊情况
        if total + m >= n * A:
            return cf * n + cm * A, [A]*n

        # 计算可能的最大完美技能数
        perfect = 0
        for i in reversed(range(n)):
            cost = A - sorted_a[i]
            if m >= cost:
                perfect += 1
                m -= cost
            else:
                break

        # 提高最低技能
        min_level = sorted_a[0]
        for i in range(1, n-perfect):
            delta = sorted_a[i] - sorted_a[i-1]
            if m >= delta * i:
                min_level += delta
                m -= delta * i
            else:
                min_level += m // i
                m %= i
                break

        final_force = perfect * cf + min_level * cm
        final_levels = [max(a, min_level) for a in a_initial]
        # 升满完美技能
        for i in reversed(range(n)):
            if final_levels[i] < A and perfect > 0:
                final_levels[i] = A
                perfect -= 1
        return final_force, final_levels
