from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.amrkitayutathetreasurehunter.Amrkitayutathetreasurehunter_reward_calculator import AmrkitayutathetreasurehunterRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class AmrkitayutathetreasurehunterInteraction(BaseInteraction):
    """Amrkitayutathetreasurehunter交互管理器"""
    
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
        score = AmrkitayutathetreasurehunterRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Amrkitayutathetreasurehunter问题！"""
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
    def calculate_max_gems(n, d, gems):
        cnt = defaultdict(int)
        for p in gems:
            cnt[p] += 1

        MX = 30000
        max_offset = 260
        dp = [[-1] * (2*max_offset + 1) for _ in range(MX + 1)]
        initial_pos = d

        if initial_pos > MX:
            return 0
        dp[initial_pos][max_offset] = cnt[initial_pos]
        ans = cnt[0] + dp[initial_pos][max_offset]  # Include starting position

        for pos in range(initial_pos, MX + 1):
            for offset in range(2*max_offset + 1):
                if dp[pos][offset] == -1:
                    continue
                current_len = d + (offset - max_offset)
                for dl in (-1, 0, 1):
                    new_len = current_len + dl
                    if new_len <= 0:
                        continue
                    next_pos = pos + new_len
                    if next_pos > MX:
                        continue
                    new_offset = offset + dl
                    if 0 <= new_offset <= 2*max_offset:
                        total = dp[pos][offset] + cnt[next_pos]
                        if total > dp[next_pos][new_offset]:
                            dp[next_pos][new_offset] = total
                            ans = max(ans, total)
        return ans
