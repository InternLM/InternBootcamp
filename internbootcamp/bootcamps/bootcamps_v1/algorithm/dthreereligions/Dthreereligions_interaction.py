from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dthreereligions.Dthreereligions_reward_calculator import DthreereligionsRewardCalculator

# 导入依赖库
import random
from string import ascii_lowercase
import re

# === 源文件中的全局函数 ===

def preprocess_nxt(s):
    n = len(s)
    nx = [-1] * 26
    nxt = [[-1] * 26 for _ in range(n + 1)]
    for i in range(n, -1, -1):
        if i < n:
            c = ord(s[i]) - ord('a')
            nx[c] = i + 1
        for j in range(26):
            nxt[i][j] = nx[j]
    return nxt

def trans(nxt, k, d):
    return -1 if k == -1 else nxt[k][d]

def better(a, b):
    if a == -1:
        return b
    if b == -1:
        return a
    return min(a, b)

def simulate_operations(s, operations):
    nxt = preprocess_nxt(s)
    dp = [[[-1 for _ in range(251)] for _ in range(251)] for __ in range(251)]
    dp[0][0][0] = 0
    st1, st2, st3 = [], [], []
    c1, c2, c3 = 0, 0, 0
    expected_outputs = []
    for op in operations:
        parts = op.split()
        cmd, id = parts[0], int(parts[1])
        if cmd == '+':
            d = ord(parts[2]) - ord('a')
            if id == 1:
                st1.append(d)
                new_c1 = c1 + 1
                for i in range(c2 + 1):
                    for j in range(c3 + 1):
                        val = trans(nxt, dp[c1][i][j], d)
                        if i > 0:
                            di = st2[i-1]
                            val = better(val, trans(nxt, dp[new_c1][i-1][j], di))
                        if j > 0:
                            dj = st3[j-1]
                            val = better(val, trans(nxt, dp[new_c1][i][j-1], dj))
                        dp[new_c1][i][j] = val
                c1 += 1
            elif id == 2:
                st2.append(d)
                new_c2 = c2 + 1
                for i in range(c1 + 1):
                    for j in range(c3 + 1):
                        val = trans(nxt, dp[i][c2][j], d)
                        if i > 0:
                            di = st1[i-1]
                            val = better(val, trans(nxt, dp[i-1][new_c2][j], di))
                        if j > 0:
                            dj = st3[j-1]
                            val = better(val, trans(nxt, dp[i][new_c2][j-1], dj))
                        dp[i][new_c2][j] = val
                c2 += 1
            else:
                st3.append(d)
                new_c3 = c3 + 1
                for i in range(c1 + 1):
                    for j in range(c2 + 1):
                        val = trans(nxt, dp[i][j][c3], d)
                        if i > 0:
                            di = st1[i-1]
                            val = better(val, trans(nxt, dp[i-1][j][new_c3], di))
                        if j > 0:
                            dj = st2[j-1]
                            val = better(val, trans(nxt, dp[i][j-1][new_c3], dj))
                        dp[i][j][new_c3] = val
                c3 += 1
        else:
            if id == 1:
                st1.pop()
                c1 -= 1
            elif id == 2:
                st2.pop()
                c2 -= 1
            else:
                st3.pop()
                c3 -= 1
        current_dp = dp[c1][c2][c3]
        expected_outputs.append('YES' if current_dp != -1 else 'NO')
    return expected_outputs


class DthreereligionsInteraction(BaseInteraction):
    """Dthreereligions交互管理器"""
    
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
        score = DthreereligionsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dthreereligions问题！"""
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

