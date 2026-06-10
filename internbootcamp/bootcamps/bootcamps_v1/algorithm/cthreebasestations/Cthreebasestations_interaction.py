from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cthreebasestations.Cthreebasestations_reward_calculator import CthreebasestationsRewardCalculator

# 导入依赖库
from bisect import bisect_left
from bisect import bisect_right
import random
import re




class CthreebasestationsInteraction(BaseInteraction):
    """Cthreebasestations交互管理器"""
    
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
        score = CthreebasestationsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cthreebasestations问题！"""
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
    def _compute_solution(n, houses):
        a = sorted([x * 2 for x in houses])
        if not a:
            return 0.0, [0.0, 0.0, 0.0]

        left, right = 0, 1 << 31

        # 二分查找最小d
        while left < right:
            mid = (left + right) // 2
            s = mid * 2
            x = bisect_right(a, a[0] + s)
            y = bisect_left(a, a[-1] - s)

            if x < y and (a[y-1] - a[x] > s):
                left = mid + 1
            else:
                right = mid

        d = left
        correct_d = d / 2.0

        # 计算基站坐标
        x_val = bisect_right(a, a[0] + d * 2)
        y_val = bisect_left(a, a[-1] - d * 2)

        # 处理全范围覆盖的情况
        if x_val >= len(a):
            return correct_d, [a[0]/2.0, a[0]/2.0, a[0]/2.0]

        # 计算三段分割点
        s1 = (a[0] + a[x_val-1])/4.0 if x_val > 0 else a[0]/2.0
        s2 = (a[x_val] + a[y_val-1])/4.0 if x_val < y_val else s1
        s3 = (a[y_val] + a[-1])/4.0 if y_val < len(a) else a[-1]/2.0

        return correct_d, [s1, s2, s3]
