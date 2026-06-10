from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cperfecttriples.Cperfecttriples_reward_calculator import CperfecttriplesRewardCalculator

# 导入依赖库
import random
import re




class CperfecttriplesInteraction(BaseInteraction):
    """Cperfecttriples交互管理器"""
    
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
        score = CperfecttriplesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cperfecttriples问题！"""
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
    def _get_st2(cls, count):
        """ 优化st2计算：通过位长度快速定位起始点 """
        if count == 0:
            return 0
        target = 3 * count
        bit_len = target.bit_length()
        exponent = (bit_len + 1) // 2  # 4^exponent初始估算
        st2 = 1 << (2 * exponent)

        # 精确调整
        while st2 > target:
            exponent -= 1
            st2 >>= 2
        while st2 * 4 <= target:
            st2 <<= 2
        return st2

    @classmethod
    def _getFirstInTriple(cls, count):
        st2 = cls._get_st2(count)
        return st2 + count - (st2 - 1) // 3 - 1

    @classmethod
    def _getValue(cls, position):
        # 保持原算法结构，优化计算效率
        triple_index = (position + 2) // 3
        first = cls._getFirstInTriple(triple_index)

        mod = position % 3
        if mod == 1:
            return first

        # 公共计算逻辑提取
        res = 0
        value = 1
        f = first
        while f > 0:
            x = f & 3
            if mod == 2:
                res += (value << 1) if x == 1 else (3*value if x ==2 else value)
            else:
                res += (3*value) if x ==1 else (value<<1 if x==3 else value)
            value <<= 2
            f >>= 2
        return res
