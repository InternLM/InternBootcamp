from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cdoubleprofiles.Cdoubleprofiles_reward_calculator import CdoubleprofilesRewardCalculator

# 导入依赖库
import random
from itertools import combinations
from collections import defaultdict
import re




class CdoubleprofilesInteraction(BaseInteraction):
    """Cdoubleprofiles交互管理器"""
    
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
        score = CdoubleprofilesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cdoubleprofiles问题！"""
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
    def compute_answer(n, m, edges):
        """
        改进哈希计算逻辑，增加对大数的容错处理
        使用更安全的模运算防止数值溢出
        """
        MOD = 10**18 + 3  # 大素数防止哈希碰撞
        B = 37

        p = [1] * (n + 2)  # 扩展数组长度防止越界
        for i in range(1, n+2):
            p[i] = (p[i-1] * B) % MOD

        h = [0] * (n + 2)
        for v, u in edges:
            h[v] = (h[v] + p[u]) % MOD
            h[u] = (h[u] + p[v]) % MOD

        m1 = defaultdict(int)
        m2 = defaultdict(int)
        for i in range(1, n+1):
            m1[h[i]] += 1
            m2[(h[i] + p[i]) % MOD] += 1  # 增加模运算

        ans = 0
        for cnt in m1.values():
            ans += cnt * (cnt - 1) // 2
        for cnt in m2.values():
            ans += cnt * (cnt - 1) // 2
        return ans
