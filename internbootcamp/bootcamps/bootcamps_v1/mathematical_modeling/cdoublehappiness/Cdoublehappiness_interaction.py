from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.cdoublehappiness.Cdoublehappiness_reward_calculator import CdoublehappinessRewardCalculator

# 导入依赖库
import random
import re
from math import isqrt




class CdoublehappinessInteraction(BaseInteraction):
    """Cdoublehappiness交互管理器"""
    
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
        score = CdoublehappinessRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cdoublehappiness问题！"""
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
    def _sieve(self, l, r):
        """高效生成区间[l, r]内的质数列表"""
        if r < 2:
            return []

        # 生成基础质数用于筛法
        limit = isqrt(r) + 1
        sieve = [True] * (limit + 1)
        sieve[0:2] = [False, False]
        for i in range(2, isqrt(limit) + 1):
            if sieve[i]:
                sieve[i*i : limit+1 : i] = [False] * len(sieve[i*i : limit+1 : i])
        base_primes = [i for i, prime in enumerate(sieve) if prime]

        # 区间筛法
        segment_size = r - l + 1
        sieve = [True] * segment_size
        for p in base_primes:
            start = max(p * p, ((l + p - 1) // p) * p)
            for i in range(start, r+1, p):
                sieve[i - l] = False

        # 处理小质数的平方
        for i in range(max(2, l), isqrt(r) + 1):
            if sieve[i - l]:
                for j in range(i*i, r+1, i):
                    sieve[j - l] = False

        return [i + l for i in range(segment_size) if sieve[i]]
