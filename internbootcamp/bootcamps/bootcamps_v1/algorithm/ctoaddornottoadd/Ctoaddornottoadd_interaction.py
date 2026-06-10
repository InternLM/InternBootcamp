from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctoaddornottoadd.Ctoaddornottoadd_reward_calculator import CtoaddornottoaddRewardCalculator

# 导入依赖库
# 无需额外导入

# === 源文件中的全局函数 ===

def compute_max_freq_min_num(n, k, arr):
    arr.sort()
    max_x = 0
    current_sum = 0
    left = 0
    for right in range(n):
        current_sum += arr[right]
        while (right - left + 1) * arr[right] - current_sum > k:
            current_sum -= arr[left]
            left += 1
        current_x = right - left + 1
        if current_x > max_x:
            max_x = current_x

    min_num = float('inf')
    current_sum = 0
    left = 0
    for right in range(n):
        current_sum += arr[right]
        while (right - left + 1) > max_x:
            current_sum -= arr[left]
            left += 1
        if (right - left + 1) == max_x:
            cost = max_x * arr[right] - current_sum
            if cost <= k and arr[right] < min_num:
                min_num = arr[right]
    return (max_x, min_num)


class CtoaddornottoaddInteraction(BaseInteraction):
    """Ctoaddornottoadd交互管理器"""
    
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
        score = CtoaddornottoaddRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ctoaddornottoadd问题！"""
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

