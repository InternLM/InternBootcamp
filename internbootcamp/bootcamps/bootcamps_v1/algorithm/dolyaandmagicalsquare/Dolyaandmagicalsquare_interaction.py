from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dolyaandmagicalsquare.Dolyaandmagicalsquare_reward_calculator import DolyaandmagicalsquareRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_case(n_input, k_input):
    MAX_PRECOMPUTE = 100
    f = [0]
    for _ in range(MAX_PRECOMPUTE):
        f.append(f[-1] * 4 + 1)
    p = [0]
    for g in range(MAX_PRECOMPUTE):
        p.append(p[-1] + (2 ** (g + 1) - 1))
    
    n, k = n_input, k_input

    if k == 1:
        return f"YES {n-1}"
    
    # 计算最大可能的分割次数（不考虑路径条件）
    max_f = (4**n - 1) // 3
    if k > max_f:
        return "NO"
    
    original_n = n
    
    # 直接遍历所有可能的j（不截断n）
    for j in range(original_n - 1, -1, -1):
        m_segment = original_n - j
        
        # 计算当前段的p值
        if m_segment < len(p):
            current_p = p[m_segment]
        else:
            current_p = 2 * (2**m_segment - 1) - m_segment
        
        if current_p > k:
            continue
        
        # 计算剩余可用分割次数
        other = 2 ** m_segment
        if j < len(f):
            f_j = f[j]
        else:
            f_j = (4**j - 1) // 3
        
        avail = (other - 1) ** 2 * f_j
        
        # 判断是否满足总分割次数
        if current_p + avail >= k:
            answer_m = original_n - m_segment
            return f"YES {answer_m}"
    
    return "NO"


class DolyaandmagicalsquareInteraction(BaseInteraction):
    """Dolyaandmagicalsquare交互管理器"""
    
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
        score = DolyaandmagicalsquareRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dolyaandmagicalsquare问题！"""
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

