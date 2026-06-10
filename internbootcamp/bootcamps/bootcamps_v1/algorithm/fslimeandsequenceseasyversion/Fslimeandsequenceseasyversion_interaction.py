from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.fslimeandsequenceseasyversion.Fslimeandsequenceseasyversion_reward_calculator import FslimeandsequenceseasyversionRewardCalculator

# 导入依赖库
import re

# === 源文件中的全局变量 ===

MOD = 998244353


class FslimeandsequenceseasyversionInteraction(BaseInteraction):
    """Fslimeandsequenceseasyversion交互管理器"""
    
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
        score = FslimeandsequenceseasyversionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Fslimeandsequenceseasyversion问题！"""
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
    def compute_answer(n):
        mod = MOD
        if n == 0:
            return []

        # 预计算阶乘和逆阶乘
        fac = [1]*(n+1)
        for i in range(1, n+1):
            fac[i] = fac[i-1] * i % mod

        inv_fac = [1]*(n+1)
        inv_fac[n] = pow(fac[n], mod-2, mod)
        for i in range(n-1, -1, -1):
            inv_fac[i] = inv_fac[i+1] * (i+1) % mod

        # 使用滚动数组优化空间
        ans = [0]*(n+2)
        prev = [0]*(n+2)
        prev[0] = 1

        for i in range(1, n+1):
            curr = [0]*(n+2)
            for j in range(1, i+1):
                term1 = prev[j] * j % mod
                term2 = prev[j-1] * (i-j+1) % mod
                curr[j] = (term1 + term2) % mod

            # 实时累加结果，避免存储全表
            for j in range(1, i+1):
                ans[j] = (ans[j] + curr[j] * inv_fac[i]) % mod

            prev = curr  # 滚动更新

        # 最终调整
        return [ans[j] * fac[n] % mod for j in range(1, n+1)]
