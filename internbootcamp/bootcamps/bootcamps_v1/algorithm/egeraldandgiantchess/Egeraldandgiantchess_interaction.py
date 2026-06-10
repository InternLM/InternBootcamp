from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.egeraldandgiantchess.Egeraldandgiantchess_reward_calculator import EgeraldandgiantchessRewardCalculator

# 导入依赖库
import re

# === 源文件中的全局变量 ===

global_fac = [1]

global_inv = [1]

mod_value = 10**9 + 7



# === 源文件中的全局函数 ===

def init_global_fac_inv(maxn):
    global global_fac, global_inv, mod_value
    if maxn < len(global_fac):
        return
    current_len = len(global_fac)
    for i in range(current_len, maxn + 1):
        global_fac.append((global_fac[-1] * i) % mod_value)
        inv_i = pow(i, mod_value - 2, mod_value)
        new_inv = (global_inv[-1] * inv_i) % mod_value
        global_inv.append(new_inv)

def culC(a, b):
    if a < 0 or b < 0 or a < b:
        return 0
    init_global_fac_inv(a)
    return global_fac[a] * global_inv[b] % mod_value * global_inv[a - b] % mod_value

def path(sx, sy, tx, ty):
    dx = tx - sx
    dy = ty - sy
    if dx < 0 or dy < 0:
        return 0
    return culC(dx + dy, dx)

def compute_solution(h, w, blocks):
    mod = 10**9 + 7
    blocks_sorted = sorted(blocks, key=lambda x: (x[0], x[1]))
    blocks_sorted.append((h, w))
    n = len(blocks_sorted)
    dp = [0] * n

    for i in range(n):
        r, c = blocks_sorted[i]
        total = path(1, 1, r, c)
        for j in range(i):
            pr, pc = blocks_sorted[j]
            if pr <= r and pc <= c:
                ways = path(pr, pc, r, c) * dp[j]
                total = (total - ways) % mod
        dp[i] = total % mod
    return dp[-1]


class EgeraldandgiantchessInteraction(BaseInteraction):
    """Egeraldandgiantchess交互管理器"""
    
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
        score = EgeraldandgiantchessRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Egeraldandgiantchess问题！"""
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

