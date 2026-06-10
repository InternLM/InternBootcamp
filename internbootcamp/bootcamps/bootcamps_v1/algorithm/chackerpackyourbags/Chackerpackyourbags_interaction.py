from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.chackerpackyourbags.Chackerpackyourbags_reward_calculator import ChackerpackyourbagsRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re
import bisect




class ChackerpackyourbagsInteraction(BaseInteraction):
    """Chackerpackyourbags交互管理器"""
    
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
        score = ChackerpackyourbagsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Chackerpackyourbags问题！"""
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
    def optimal_solution(vouchers, x):
        duration_map = defaultdict(list)
        for l, r, cost in vouchers:
            duration = r - l + 1
            duration_map[duration].append((l, cost))

        # 预处理每个duration的最小成本
        pre_min = {}
        for d in duration_map:
            sorted_list = sorted(duration_map[d], key=lambda x: x[0])
            min_prefix = []
            current_min = float('inf')
            for l, c in reversed(sorted_list):
                current_min = min(current_min, c)
                min_prefix.append(current_min)
            min_prefix.reverse()
            pre_min[d] = (sorted_list, min_prefix)

        min_cost = float('inf')

        for l, r, cost in vouchers:
            current_duration = r - l + 1
            need_duration = x - current_duration
            if need_duration not in pre_min:
                continue

            sorted_list, min_prefix = pre_min[need_duration]
            idx = bisect.bisect_right(sorted_list, (r, float('inf')))

            if idx < len(min_prefix):
                min_cost = min(min_cost, cost + min_prefix[idx])

        return min_cost if min_cost != float('inf') else -1
