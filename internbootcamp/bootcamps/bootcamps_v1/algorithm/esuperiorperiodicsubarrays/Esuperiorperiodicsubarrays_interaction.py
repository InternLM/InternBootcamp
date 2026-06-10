from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.esuperiorperiodicsubarrays.Esuperiorperiodicsubarrays_reward_calculator import EsuperiorperiodicsubarraysRewardCalculator

# 导入依赖库
import math
from collections import defaultdict
import random
import re

# === 源文件中的全局函数 ===

def solve_puzzle(n, a):
    if n == 1:
        return 0  # s必须≥1且<1，无解

    a_extended = a.copy()
    a_extended.extend(a)
    inf = min(a) - 1
    a_extended[-1] = inf  # 保证最后元素最小
    result = 0

    numbers_by_gcd = defaultdict(list)
    for i in range(1, n):
        current_gcd = math.gcd(i, n)
        numbers_by_gcd[current_gcd].append(i)

    for d in numbers_by_gcd:  # 遍历每个可能的gcd值
        if n % d != 0:
            continue
        
        # 计算每个模位的最大值
        m = [-math.inf] * d
        for i in range(n):
            mod = i % d
            if a_extended[i] > m[mod]:
                m[mod] = a_extended[i]
        
        l = 0
        r = 0
        max_r = len(a_extended) - 1  # 防止越界
        while l < n and r <= max_r:
            if a_extended[r] < m[r % d]:
                # 处理当前有效区间
                sorted_s = sorted(numbers_by_gcd[d])
                for s in sorted_s:
                    if s > (r - l):
                        break
                    # 计算有效区间长度
                    start = l
                    end = min(r - s, n - 1)
                    if start <= end:
                        result += end - start + 1
                l = r + 1
                r = l
            else:
                r += 1
    return result


class EsuperiorperiodicsubarraysInteraction(BaseInteraction):
    """Esuperiorperiodicsubarrays交互管理器"""
    
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
        score = EsuperiorperiodicsubarraysRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Esuperiorperiodicsubarrays问题！"""
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

