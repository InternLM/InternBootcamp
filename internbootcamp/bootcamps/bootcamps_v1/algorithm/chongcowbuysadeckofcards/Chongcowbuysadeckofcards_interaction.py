from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.chongcowbuysadeckofcards.Chongcowbuysadeckofcards_reward_calculator import ChongcowbuysadeckofcardsRewardCalculator

# 导入依赖库
import random




class ChongcowbuysadeckofcardsInteraction(BaseInteraction):
    """Chongcowbuysadeckofcards交互管理器"""
    
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
        score = ChongcowbuysadeckofcardsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Chongcowbuysadeckofcards问题！"""
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
    def calculate_min_turns(n, cards):
        # 预处理卡片数据
        color = [1 if c['color'] == 'B' else 0 for c in cards]
        r = [c['r'] for c in cards]
        b = [c['b'] for c in cards]

        total_r = sum(r)
        total_b = sum(b)
        max_rsave = total_r  # 红令牌最多能节省的总量

        # DP状态定义：dp[mask][rsave] = 最大bsave
        dp = [[-1]*(max_rsave+1) for _ in range(1<<n)]
        dp[0][0] = 0  # 初始状态

        for mask in range(1<<n):
            # 计算当前拥有的红蓝卡数量
            current_r = sum(0 if color[i] else 1 
                          for i in range(n) if (mask >> i) & 1)
            current_b = sum(1 if color[i] else 0 
                          for i in range(n) if (mask >> i) & 1)

            for rsave in range(max_rsave+1):
                if dp[mask][rsave] == -1:
                    continue

                # 尝试购买下一张卡片
                for next_card in range(n):
                    if (mask & (1 << next_card)) == 0:
                        # 计算实际需要支付的令牌
                        needed_r = max(r[next_card] - current_r, 0)
                        needed_b = max(b[next_card] - current_b, 0)

                        # 累计节省的令牌
                        new_rsave = rsave + (r[next_card] - needed_r)
                        new_bsave = dp[mask][rsave] + (b[next_card] - needed_b)
                        new_mask = mask | (1 << next_card)

                        # 更新状态
                        if new_rsave <= max_rsave and new_bsave > dp[new_mask][new_rsave]:
                            dp[new_mask][new_rsave] = new_bsave

        # 计算最终结果
        min_ops = max(total_r, total_b)  # 初始值
        full_mask = (1 << n) - 1

        for rsave in range(max_rsave+1):
            if dp[full_mask][rsave] != -1:
                required_r = max(total_r - rsave, 0)
                required_b = max(total_b - dp[full_mask][rsave], 0)
                min_ops = min(min_ops, max(required_r, required_b))

        return min_ops + n  # 加上购买卡片的n次操作
