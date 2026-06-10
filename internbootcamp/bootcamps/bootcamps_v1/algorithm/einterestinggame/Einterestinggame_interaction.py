from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.einterestinggame.Einterestinggame_reward_calculator import EinterestinggameRewardCalculator

# 导入依赖库
from functools import reduce
from operator import xor
import re
import random




class EinterestinggameInteraction(BaseInteraction):
    """Einterestinggame交互管理器"""
    
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
        score = EinterestinggameRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Einterestinggame问题！"""
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
    def split(self, stone, k):
        total = k * (k - 1) // 2
        numerator = stone + total
        if numerator % k != 0:
            return []
        a = numerator // k
        if a < k:
            return []
        piles = [a - i for i in range(k)]
        if sum(piles) != stone:
            return []
        return piles

    def mex(self, s):
        i = 0
        while i in s:
            i += 1
        return i

    def precompute(self):
        self.win_dict = {1: -1, 2: -1}
        known = {1: 0, 2: 0}
        for stone in range(3, self.max_n + 1):
            mex_set = set()
            win_k = -1
            max_k = int((2 * stone) ** 0.5) + 1
            for k in range(2, max_k + 1):
                piles = self.split(stone, k)
                if not piles:
                    continue
                try:
                    xor_val = reduce(xor, (known[p] for p in piles))
                except KeyError:
                    continue
                mex_set.add(xor_val)
                if xor_val == 0 and win_k == -1:
                    win_k = k
            mex_val = self.mex(mex_set)
            known[stone] = mex_val
            self.win_dict[stone] = win_k
