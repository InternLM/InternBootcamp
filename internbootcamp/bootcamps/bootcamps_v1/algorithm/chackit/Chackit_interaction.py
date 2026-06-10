from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.chackit.Chackit_reward_calculator import ChackitRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def f(s):
    N = 0
    p = 0
    L = len(s)
    for i in range(len(s)):
        k = L - i - 1
        for j in range(int(s[i])):
            term1 = 9 * k * (10 ** k) // 2
            term2 = (p + j) * (10 ** k)
            N += term1 + term2
        p += int(s[i])
    return N

def g(N):
    if N == 0:
        return '0'
    s = ''
    L = 200  # 调整为200位
    for i in range(L):
        d = 0
        for j in range(10):
            test_s = s + str(j) + '0' * (L - i - 1)
            current_f = f(test_s)
            if current_f >= N:
                if j > 0:
                    s += str(j-1)
                else:
                    s += '0'  # 处理j=0的情况
                d = 1
                break
        if not d:
            s += '9'
    s = s.lstrip('0') or '0'
    return s

def find_test_case(a):
    s_list = []
    p_list = []
    i = 1
    while True:
        target = i * a
        m = g(target)
        q = f(m) % a
        for idx in range(len(p_list)):
            if q == p_list[idx] and int(m) > int(s_list[idx]):
                l = int(s_list[idx])
                r = int(m) - 1
                return (l, r)
        s_list.append(m)
        p_list.append(q)
        i += 1


class ChackitInteraction(BaseInteraction):
    """Chackit交互管理器"""
    
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
        score = ChackitRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Chackit问题！"""
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

