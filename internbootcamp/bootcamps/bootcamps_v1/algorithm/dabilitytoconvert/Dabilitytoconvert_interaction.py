from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dabilitytoconvert.Dabilitytoconvert_reward_calculator import DabilitytoconvertRewardCalculator

# 导入依赖库
import re
import random




class DabilitytoconvertInteraction(BaseInteraction):
    """Dabilitytoconvert交互管理器"""
    
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
        score = DabilitytoconvertRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dabilitytoconvert问题！"""
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
    def calculate_min_x(self, n, k_str):
        INF = 10**19
        length = len(k_str)
        if length == 0:
            return 0

        # 预处理n的位数阈值
        tr = len(str(n))

        # 初始化权值数组
        pown = [1] * 70
        for i in range(1, 70):
            pown[i] = pown[i-1] * n if pown[i-1] <= INF // n else INF

        # DP表：dp[i][j] = (min_value, digits_count)
        dp = [[(INF, 0) for _ in range(length)] for __ in range(length)]

        # 填充DP表
        for l in range(1, length+1):
            for i in range(length - l + 1):
                j = i + l - 1
                current_str = k_str[i:j+1]

                # 候选1：整个子串作为单个数字
                if len(current_str) <= tr:
                    num = int(current_str)
                    if num < n and num < dp[i][j][0]:
                        dp[i][j] = (num, 1)

                # 候选2：分割子串
                for mid in range(i, j):
                    left_val, left_len = dp[i][mid]
                    right_val, right_len = dp[mid+1][j]
                    if right_len >= len(pown) or pown[right_len] == INF:
                        continue
                    combined = left_val * pown[right_len] + right_val
                    if combined < dp[i][j][0] and combined <= INF:
                        dp[i][j] = (combined, left_len + right_len)

        return dp[0][length-1][0] if dp[0][length-1][0] <= 1e18 else None
