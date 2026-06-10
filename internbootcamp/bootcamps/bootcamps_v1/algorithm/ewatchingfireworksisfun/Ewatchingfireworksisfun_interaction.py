from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ewatchingfireworksisfun.Ewatchingfireworksisfun_reward_calculator import EwatchingfireworksisfunRewardCalculator

# 导入依赖库
import random
import math

# === 源文件中的全局函数 ===

def build_sparse_table(arr, n):
    log_table = [0] * (n + 1)
    for i in range(2, n + 1):
        log_table[i] = log_table[i // 2] + 1
    k_max = log_table[n] + 1
    st = [[0] * (n + 1) for _ in range(k_max)]
    for i in range(1, n + 1):
        st[0][i] = arr[i]
    for j in range(1, k_max):
        for i in range(1, n + 1 - (1 << j) + 1):
            st[j][i] = min(st[j-1][i], st[j-1][i + (1 << (j-1))])
    return st, log_table

def query_min(st, log_table, l, r):
    length = r - l + 1
    k = log_table[length]
    return min(st[k][l], st[k][r - (1 << k) + 1])

def calculate_answer(n, m, d, fireworks):
    sum_bi = sum(b for a, b, t in fireworks)
    a_list = [a for a, b, t in fireworks]
    t_list = [t for a, b, t in fireworks]
    
    prev_dp = [0] * (n + 2)
    a1 = a_list[0]
    for j in range(1, n + 1):
        prev_dp[j] = abs(a1 - j)
    
    for i in range(1, m):
        ai = a_list[i]
        ti = t_list[i]
        delta_t = ti - t_list[i-1]
        tt = d * delta_t
        tt = min(tt, n)
        
        st, log_table = build_sparse_table(prev_dp, n)
        curr_dp = [0] * (n + 2)
        
        for j in range(1, n + 1):
            left = max(1, j - tt)
            right = min(n, j + tt)
            if left > right:
                curr_dp[j] = float('inf')
            else:
                min_prev = query_min(st, log_table, left, right)
                curr_dp[j] = min_prev + abs(ai - j)
        
        prev_dp, curr_dp = curr_dp, prev_dp
    
    min_final = min(prev_dp[j] for j in range(1, n + 1))
    return sum_bi - min_final


class EwatchingfireworksisfunInteraction(BaseInteraction):
    """Ewatchingfireworksisfun交互管理器"""
    
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
        score = EwatchingfireworksisfunRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ewatchingfireworksisfun问题！"""
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

