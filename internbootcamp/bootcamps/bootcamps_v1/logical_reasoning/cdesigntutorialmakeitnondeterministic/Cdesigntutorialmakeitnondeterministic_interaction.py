from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cdesigntutorialmakeitnondeterministic.Cdesigntutorialmakeitnondeterministic_reward_calculator import CdesigntutorialmakeitnondeterministicRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_handle_order(names, p_list):
    if not names or len(p_list) != len(names):
        return "NO"
    n = len(names)
    p = p_list
    Flag = True
    current_user = names[p[0]-1]
    a, b = current_user
    Tmp = a if a < b else b
    for i in range(1, len(p)):
        current_user = names[p[i]-1]
        a, b = current_user
        current_min = a if a < b else b
        current_max = b if a < b else a
        if Tmp >= current_min:
            if Tmp >= current_max:
                Flag = False
                break
            else:
                Tmp = current_max
        else:
            Tmp = current_min
    return "YES" if Flag else "NO"

def generate_random_string(min_length=1, max_length=50):
    length = random.randint(min_length, max_length)
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length))


class CdesigntutorialmakeitnondeterministicInteraction(BaseInteraction):
    """Cdesigntutorialmakeitnondeterministic交互管理器"""
    
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
        score = CdesigntutorialmakeitnondeterministicRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cdesigntutorialmakeitnondeterministic问题！"""
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

