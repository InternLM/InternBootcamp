from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpetyaandexam.Cpetyaandexam_reward_calculator import CpetyaandexamRewardCalculator

# 导入依赖库
import random
import re




class CpetyaandexamInteraction(BaseInteraction):
    """Cpetyaandexam交互管理器"""
    
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
        score = CpetyaandexamRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cpetyaandexam问题！"""
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
    def solve_case(n, T, a, b, types, times):
        combined = sorted(zip(times, types), key=lambda x: (x[0], x[1]))
        sorted_times = [x[0] for x in combined]
        sorted_types = [x[1] for x in combined]

        # 计算前缀时间和剩余easy数量
        prefix = []
        total_time = 0
        for typ in sorted_types:
            total_time += a if typ == 0 else b
            prefix.append(total_time)

        max_points = 0

        # 情况1：解决所有问题
        if prefix[-1] <= T:
            return n

        # 情况2：在第一个问题强制前解决easy
        first_mandatory = sorted_times[0]
        if first_mandatory > 0:
            available = first_mandatory - 1
            max_easy = min(available // a, sum(1 for t in sorted_types if t == 0))
            max_points = max(max_points, max_easy)

        # 预处理剩余easy数量
        remaining_easy = [0] * (n + 1)
        count = 0
        for i in range(n-1, -1, -1):
            if sorted_types[i] == 0:
                count += 1
            remaining_easy[i] = count

        # 检查每个可能的分割点
        current_total_time = 0
        for i in range(n):
            current_total_time += a if sorted_types[i] == 0 else b
            if current_total_time > T:
                break

            # 计算后续可用时间
            next_mandatory = sorted_times[i+1] if i < n-1 else T + 1
            available_time = next_mandatory - current_total_time - 1
            if available_time < 0:
                continue

            # 计算可添加的easy数量
            possible = min(available_time // a, remaining_easy[i+1])
            max_points = max(max_points, i + 1 + possible)

        return max_points
