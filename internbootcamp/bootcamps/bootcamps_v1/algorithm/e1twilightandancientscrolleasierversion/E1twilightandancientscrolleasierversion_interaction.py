from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.e1twilightandancientscrolleasierversion.E1twilightandancientscrolleasierversion_reward_calculator import E1twilightandancientscrolleasierversionRewardCalculator

# 导入依赖库
import re
import random
import bisect

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, words):
    if n == 0:
        return 0
    preprocessed = []
    for s in words:
        m = len(s)
        deletions = [s[:i] + s[i+1:] for i in range(m)]
        deletions.sort()
        preprocessed.append(deletions)
    
    prev_deletions = preprocessed[0]
    prev_prefix_sum = [0] * (len(prev_deletions) + 1)
    for i in range(len(prev_deletions)):
        prev_prefix_sum[i+1] = (prev_prefix_sum[i] + 1) % MOD
    
    for x in range(1, n):
        current_deletions = preprocessed[x]
        current_dp = []
        for s in current_deletions:
            j = bisect.bisect_right(prev_deletions, s)
            current_count = prev_prefix_sum[j]
            current_dp.append(current_count % MOD)
        
        current_prefix_sum = [0]
        current_sum = 0
        for cnt in current_dp:
            current_sum = (current_sum + cnt) % MOD
            current_prefix_sum.append(current_sum)
        
        prev_deletions = current_deletions
        prev_prefix_sum = current_prefix_sum
    
    return prev_prefix_sum[-1] % MOD


class E1twilightandancientscrolleasierversionInteraction(BaseInteraction):
    """E1twilightandancientscrolleasierversion交互管理器"""
    
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
        score = E1twilightandancientscrolleasierversionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个E1twilightandancientscrolleasierversion问题！"""
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

