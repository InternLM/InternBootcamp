from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.cryptography.cpostcard.Cpostcard_reward_calculator import CpostcardRewardCalculator

# 导入依赖库
import re
import random




class CpostcardInteraction(BaseInteraction):
    """Cpostcard交互管理器"""
    
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
        score = CpostcardRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cpostcard问题！"""
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
    def _calculate_min_length(cls, s):
        """计算最小可能长度"""
        return len(s) - 2*(s.count('?') + s.count('*'))

    @classmethod
    def _calculate_max_length(cls, s):
        """计算最大可能长度"""
        base = len(s) - s.count('?') - s.count('*')
        stars = s.count('*')
        return base + 100*stars if stars > 0 else base

    @classmethod
    def _is_case_possible(cls, s, k):
        min_len = cls._calculate_min_length(s)
        max_len = cls._calculate_max_length(s)
        return min_len <= k <= max_len

    @classmethod
    def _is_valid_solution(cls, encrypted, candidate):
        ptr = 0
        i = 0
        while i < len(encrypted):
            if i+1 < len(encrypted) and encrypted[i+1] in ['?', '*']:
                # 处理带符号的字符
                char = encrypted[i]
                symbol = encrypted[i+1]
                i += 2

                # 查找候选字符串中的匹配情况
                count = 0
                while ptr < len(candidate) and candidate[ptr] == char:
                    ptr += 1
                    count += 1

                if symbol == '?':  # 0或1次
                    if count not in [0, 1]:
                        return False
                elif symbol == '*':  # 任意次数（含0）
                    if count < 0:
                        return False
            else:
                # 处理普通字符
                if ptr >= len(candidate) or candidate[ptr] != encrypted[i]:
                    return False
                ptr += 1
                i += 1

        return ptr == len(candidate)
