from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ckbeautifulstrings.Ckbeautifulstrings_reward_calculator import CkbeautifulstringsRewardCalculator

# 导入依赖库
import sys
import re
import random

# === 源文件中的全局函数 ===

def getnext(index, fre, k, s, flag):
    if sum(fre) > len(s) - index:
        return "ERROR"
    if index == len(s):
        return ""
    cur = ord(s[index]) - 97 if index < len(s) else 0
    if not flag:
        spare = len(s) - index - sum(fre)
        nexts = ""
        if spare % k == 0:
            nexts += 'a' * (spare // k * k)
        for j in range(26):
            if fre[j] > 0:
                nexts += chr(j + 97) * fre[j]
        return nexts
    nexts = "ERROR"
    for j in range(cur, 26):
        new_flag = flag
        if j > cur:
            new_flag = False
        original_j = fre[j]
        fre[j] -= 1
        if fre[j] < 0:
            fre[j] += k
        temp = getnext(index + 1, fre, k, s, new_flag)
        if temp != "ERROR":
            nexts = chr(j + 97) + temp
            fre[j] = original_j
            return nexts
        fre[j] = original_j
    return nexts

def solve(n, k, s):
    if n % k != 0:
        return "-1"
    fre = [0] * 26
    ans = getnext(0, fre, k, s, True)
    return ans if ans != "ERROR" else "-1"


class CkbeautifulstringsInteraction(BaseInteraction):
    """Ckbeautifulstrings交互管理器"""
    
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
        score = CkbeautifulstringsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ckbeautifulstrings问题！"""
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

