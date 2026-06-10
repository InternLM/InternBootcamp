from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ddensesubsequence.Ddensesubsequence_reward_calculator import DdensesubsequenceRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def solve(m, s):
    n = len(s)
    if n == 0 or m == 0:
        return ""
    
    # Frequency list generation
    sorted_chars = sorted(s)
    freq = []
    current_char = sorted_chars[0]
    count = 1
    
    for c in sorted_chars[1:]:
        if c == current_char:
            count += 1
        else:
            freq.append((current_char, count))
            current_char = c
            count = 1
    freq.append((current_char, count))
    
    # Find minimal solution
    for idx, (char, total) in enumerate(freq):
        required = 0
        last_covered = -1
        last_candidate = -1
        valid = True
        
        for i in range(n):
            if s[i] < char:
                last_covered = i
                last_candidate = i
            elif s[i] == char:
                last_candidate = i
            
            # Check window violation
            if i - last_covered >= m:
                if last_candidate > last_covered:
                    required += 1
                    last_covered = last_candidate
                else:
                    valid = False
                    break
        
        # Final check for the last window
        if valid and (n - last_covered) > m:
            valid = False
        
        if valid:
            # Calculate required count
            min_chars = []
            for c, _ in freq[:idx+1]:
                if c < char:
                    min_chars.append(c)
            return char * required + ''.join(sorted(min_chars))
        else:
            continue
    
    # Fallback to all smallest characters
    return ''.join(sorted(s))


class DdensesubsequenceInteraction(BaseInteraction):
    """Ddensesubsequence交互管理器"""
    
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
        score = DdensesubsequenceRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ddensesubsequence问题！"""
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

