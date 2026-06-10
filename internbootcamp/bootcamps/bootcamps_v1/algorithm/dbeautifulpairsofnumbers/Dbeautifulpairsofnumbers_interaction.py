from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dbeautifulpairsofnumbers.Dbeautifulpairsofnumbers_reward_calculator import DbeautifulpairsofnumbersRewardCalculator

# 导入依赖库
import random
import re




class DbeautifulpairsofnumbersInteraction(BaseInteraction):
    """Dbeautifulpairsofnumbers交互管理器"""
    
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
        score = DbeautifulpairsofnumbersRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dbeautifulpairsofnumbers问题！"""
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
    @classmethod
    def initialize_data(cls):
        if cls.initialized:
            return
        # Precompute factorial and inverse factorial arrays
        cls.fac = [1] * cls.maxn
        for i in range(1, cls.maxn):
            cls.fac[i] = cls.fac[i-1] * i % cls.mod

        cls.ifac = [1] * cls.maxn
        cls.ifac[cls.maxn - 1] = pow(cls.fac[cls.maxn - 1], cls.mod - 2, cls.mod)
        for i in range(cls.maxn - 2, -1, -1):
            cls.ifac[i] = cls.ifac[i + 1] * (i + 1) % cls.mod

        # Precompute s array
        cls.s = [0] * cls.maxn
        for i in range(1, cls.maxn):
            cls.s[i] = cls.s[i-1] + i

        # Initialize f array using dynamic programming
        cls.f = [[0] * cls.maxn for _ in range(cls.maxn)]
        for i in range(1, cls.maxn):
            cls.f[i][1] = 1

        for j in range(2, cls.maxn):
            if cls.s[j] >= cls.maxn:
                break
            if cls.s[j] < cls.maxn:
                cls.f[cls.s[j]][j] = cls.fac[j] % cls.mod
            for i in range(cls.s[j] + 1, cls.maxn):
                prev_i = i - j
                if prev_i >= 0:
                    term1 = cls.f[prev_i][j]
                    term2 = (cls.f[prev_i][j-1] * j) % cls.mod
                    cls.f[i][j] = (term1 + term2) % cls.mod

        cls.initialized = True

    @classmethod
    def compute_answer(cls, n, k):
        if k < 1 or k > n:
            return 0
        new_n = n - 1
        res = 0
        s_k_1 = cls.s[k-1]
        for i in range(s_k_1, new_n + 1):
            t = new_n - i - (k - 1)
            if t < 0:
                break
            comb = cls.C(k + t, t)
            if (i + k) >= cls.maxn or k >= cls.maxn:
                f_val = 0
            else:
                f_val = cls.f[i + k][k]
            res = (res + f_val * comb) % cls.mod
        return res

    @classmethod
    def C(cls, n, m):
        if m < 0 or m > n:
            return 0
        return cls.fac[n] * cls.ifac[m] % cls.mod * cls.ifac[n - m] % cls.mod
