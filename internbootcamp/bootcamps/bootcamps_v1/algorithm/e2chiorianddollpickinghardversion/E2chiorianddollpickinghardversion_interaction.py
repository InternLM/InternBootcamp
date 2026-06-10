from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.e2chiorianddollpickinghardversion.E2chiorianddollpickinghardversion_reward_calculator import E2chiorianddollpickinghardversionRewardCalculator

# 导入依赖库
import random
import re
from math import comb

# === 源文件中的全局变量 ===

MOD = 998244353


class E2chiorianddollpickinghardversionInteraction(BaseInteraction):
    """E2chiorianddollpickinghardversion交互管理器"""
    
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
        score = E2chiorianddollpickinghardversionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个E2chiorianddollpickinghardversion问题！"""
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
    @staticmethod
    def build_linear_basis(a_list, m):
        basis = [0] * m
        for x in a_list:
            if x == 0:
                continue
            for i in reversed(range(m)):  # 固定从高位到低位处理
                if (x >> i) & 1:
                    if basis[i]:
                        x ^= basis[i]
                    else:
                        basis[i] = x
                        # 消去低位
                        for j in reversed(range(i)):
                            if (basis[i] >> j) & 1:
                                basis[i] ^= basis[j]
                        # 消去高位
                        for j in range(i+1, m):
                            if (basis[j] >> i) & 1:
                                basis[j] ^= basis[i]
                        break
        non_zero = [b for b in basis if b != 0]
        return non_zero, basis

    @staticmethod
    def solve_case(n, m, a_list):
        if m == 0:
            return [pow(2, n, MOD)]

        non_zero, basis = E2chiorianddollpickinghardversionbootcamp.build_linear_basis(a_list, m)
        cnt = len(non_zero)
        pow2 = pow(2, n - cnt, MOD)
        result = [0]*(m+1)

        if 2 * cnt <= m:
            f = [0]*(m+1)

            def dfs(val, idx):
                if idx == cnt:
                    bits = bin(val).count('1')
                    if bits <= m:
                        f[bits] += 1
                    return
                dfs(val, idx+1)
                dfs(val ^ non_zero[idx], idx+1)

            dfs(0, 0)
            for i in range(m+1):
                result[i] = (f[i] * pow2) % MOD
        else:
            # 修正组合数计算逻辑
            comb_table = [[0]*(m+1) for _ in range(m+1)]
            for i in range(m+1):
                comb_table[i][0] = 1
                for j in range(1, i+1):
                    comb_table[i][j] = (comb_table[i-1][j] + comb_table[i-1][j-1]) % MOD

            # 构建对偶基
            new_b = []
            for i in range(m):
                cur = 1 << i
                for j in range(m):
                    if basis[j] and ((basis[j] >> i) & 1):
                        cur ^= 1 << j
                if cur != 0:
                    new_b.append(cur)

            dual_cnt = len(new_b)
            f = [0]*(m+1)

            def dfs_dual(val, idx):
                if idx == dual_cnt:
                    bits = bin(val).count('1')
                    if bits <= m:
                        f[bits] += 1
                    return
                dfs_dual(val, idx+1)
                dfs_dual(val ^ new_b[idx], idx+1)

            dfs_dual(0, 0)

            inv_pow = pow(2, dual_cnt, MOD)
            inv_pow = pow(inv_pow, MOD-2, MOD)
            total_mul = (pow2 * inv_pow) % MOD

            for i in range(m+1):
                res = 0
                for j in range(m+1):
                    if f[j] == 0:
                        continue
                    tmp = 0
                    for k in range(0, min(i, j)+1):
                        c = (comb_table[j][k] * comb_table[m-j][i-k]) % MOD
                        if k % 2 == 0:
                            tmp = (tmp + c) % MOD
                        else:
                            tmp = (tmp - c) % MOD
                    res = (res + f[j] * tmp) % MOD
                result[i] = (res * total_mul) % MOD

        return [x % MOD for x in result]
