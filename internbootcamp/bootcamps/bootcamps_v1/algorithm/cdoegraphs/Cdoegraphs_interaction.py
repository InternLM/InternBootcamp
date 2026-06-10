from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cdoegraphs.Cdoegraphs_reward_calculator import CdoegraphsRewardCalculator

# 导入依赖库
import re
import random
from functools import lru_cache




class CdoegraphsInteraction(BaseInteraction):
    """Cdoegraphs交互管理器"""
    
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
        score = CdoegraphsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cdoegraphs问题！"""
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
    def compute_doe_fib(n):
        """Generates the Fibonacci sequence for Doe graph sizes up to order n (0-based)."""
        if n < 0:
            return []
        fib = [1]  # D(0)
        if n == 0:
            return fib
        fib.append(2)  # D(1)
        for i in range(2, n + 1):
            fib.append(fib[i-1] + fib[i-2])
        return fib

    @classmethod
    def dfs(cls, a, b, k, fib_tuple):
        if a == b:
            return 0
        if k == 1:
            return 1
        if a > b:
            a, b = b, a
        return cls._dfs(a, b, k, fib_tuple)

    @classmethod
    def _dfs(cls, a, b, k, fib_tuple):
        if a == b:
            return 0
        if k == 1:
            return 1
        if k == 0:
            return 0

        size_k_1 = fib_tuple[k-1]
        if a > size_k_1 and b > size_k_1:
            return cls._dfs(a - size_k_1, b - size_k_1, k-2, fib_tuple)
        if a <= size_k_1 and b <= size_k_1:
            path_in = cls._dfs(a, b, k-1, fib_tuple)
            path1 = cls.dfs1(k-1, 0, a, fib_tuple) + cls.dfs2(k-1, 1, b, fib_tuple) + 2
            path2 = cls.dfs1(k-1, 1, a, fib_tuple) + cls.dfs2(k-1, 0, b, fib_tuple) + 2
            return min(path_in, path1, path2)
        else:
            path1 = min(cls.dfs1(k-1, 0, a, fib_tuple), cls.dfs1(k-1, 1, a, fib_tuple))
            path2 = cls.dfs2(k-2, 0, b - size_k_1, fib_tuple) + 1
            return path1 + path2

    @classmethod
    @lru_cache(maxsize=None)
    def dfs1(cls, a, b, c, fib_tuple):
        if a == 1:
            return 1 if (c + b) == 2 else 0
        if a == 0:
            return 0
        size_a_1 = fib_tuple[a-1]
        if b:
            if c > size_a_1:
                return cls.dfs1(a-2, 1, c - size_a_1, fib_tuple)
            else:
                option1 = cls.dfs1(a-1, 1, c, fib_tuple)
                option2 = cls.dfs1(a-1, 0, c, fib_tuple)
                return min(option1, option2) + 1 + (a-1) // 2
        else:
            if c > size_a_1:
                return cls.dfs1(a-2, 0, c - size_a_1, fib_tuple) + 1
            else:
                option1 = cls.dfs1(a-1, 0, c, fib_tuple)
                option2 = cls.dfs1(a-1, 1, c, fib_tuple) + 2
                return min(option1, option2)

    @classmethod
    @lru_cache(maxsize=None)
    def dfs2(cls, a, b, c, fib_tuple):
        if a == 1:
            return 1 if (c + b) == 2 else 0
        if a == 0:
            return 0
        size_a_1 = fib_tuple[a-1]
        if b:
            if c > size_a_1:
                return cls.dfs2(a-2, 1, c - size_a_1, fib_tuple)
            else:
                option1 = cls.dfs2(a-1, 1, c, fib_tuple)
                option2 = cls.dfs2(a-1, 0, c, fib_tuple)
                return min(option1, option2) + 1 + (a-1) // 2
        else:
            if c > size_a_1:
                return cls.dfs2(a-2, 0, c - size_a_1, fib_tuple) + 1
            else:
                option1 = cls.dfs2(a-1, 0, c, fib_tuple)
                option2 = cls.dfs2(a-1, 1, c, fib_tuple) + 2
                return min(option1, option2)
