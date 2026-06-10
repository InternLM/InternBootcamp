from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmikeandfoam.Cmikeandfoam_reward_calculator import CmikeandfoamRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def prime_factors(n):
    """返回唯一质因数列表（已排序）"""
    if n == 1:
        return []
    factors = set()
    while n % 2 == 0:
        factors.add(2)
        n = n // 2
    i = 3
    max_i = int(n**0.5) + 1
    while i <= max_i and n > 1:
        while n % i == 0:
            factors.add(i)
            n = n // i
            max_i = int(n**0.5) + 1
        i += 2
    if n > 1:
        factors.add(n)
    return sorted(factors)

def generate_correct_output(n, q, a, queries):
    """生成正确的输出序列"""
    mark = defaultdict(bool)
    freq = defaultdict(int)
    ans = 0
    tot = 0
    output = []
    
    for x in queries:
        val = a[x-1]
        factors = prime_factors(val)
        lim = 1 << len(factors)
        
        # 计算互质的元素数量
        tmp = 0
        for mask in range(1, lim):
            bits = bin(mask).count('1')
            sign = 1 if bits % 2 else -1
            product = 1
            for j in range(len(factors)):
                if mask & (1 << j):
                    product *= factors[j]
            tmp += sign * freq[product]
        
        if not mark[x]:
            # 添加操作
            ans += (tot - tmp)
            tot += 1
            # 更新素数组合频率
            for mask in range(1, lim):
                product = 1
                for j in range(len(factors)):
                    if mask & (1 << j):
                        product *= factors[j]
                freq[product] += 1
            mark[x] = True
        else:
            # 移除操作
            ans -= (tot - 1 - tmp) if val == 1 else (tot - tmp)
            tot -= 1
            # 更新素数组合频率
            for mask in range(1, lim):
                product = 1
                for j in range(len(factors)):
                    if mask & (1 << j):
                        product *= factors[j]
                freq[product] -= 1
                if freq[product] == 0:
                    del freq[product]
            mark[x] = False
        
        output.append(ans)
    
    return output


class CmikeandfoamInteraction(BaseInteraction):
    """Cmikeandfoam交互管理器"""
    
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
        score = CmikeandfoamRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cmikeandfoam问题！"""
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

