from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dflipthecards.Dflipthecards_reward_calculator import DflipthecardsRewardCalculator

# 导入依赖库
import random
import re
from io import StringIO
import sys




class DflipthecardsInteraction(BaseInteraction):
    """Dflipthecards交互管理器"""
    
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
        score = DflipthecardsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dflipthecards问题！"""
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
    def solve(input_str):
        """改进的验证算法，修正数组越界问题"""
        original_stdin = sys.stdin
        sys.stdin = StringIO(input_str)
        try:
            n = int(sys.stdin.readline())
            a = []
            for _ in range(n):
                x, y = map(int, sys.stdin.readline().split())
                a.append((x, y))

            m = 2 * n  # 正确设置数组大小
            pa = [0] * m
            f = [0] * m
            d = [0] * m

            for x, y in a:
                x -= 1
                y -= 1
                if x >= m or y >= m:  # 添加边界检查
                    return -1
                pa[x] = y
                pa[y] = x
                f[y] = 1

            ans = s = c = tot = 0
            hi, lo = m - 1, 0
            ll = rr = -1
            lr = rl = m

            while tot < n:
                upd = 0
                # 高频错误点修复：添加索引范围检查
                while hi >= max(lr, 0):
                    if hi >= m:  # 防止越界
                        hi = m - 1
                        continue
                    if not d[hi]:
                        if rl < hi or rr > pa[hi]:
                            return -1
                        upd = 1
                        rl, rr = hi, pa[hi]
                        if rl >= m or rr >= m:
                            return -1
                        d[rl] = d[rr] = 1
                        s += f[rl]
                        c += 1
                    hi -= 1

                while lo <= min(rr, m-1):
                    if lo < 0:  # 防止负索引
                        lo = 0
                        continue
                    if not d[lo]:
                        if ll > lo or lr < pa[lo]:
                            return -1
                        upd = 1
                        ll, lr = lo, pa[lo]
                        if ll >= m or lr >= m:
                            return -1
                        d[ll] = d[lr] = 1
                        s += f[ll]
                        c += 1
                    lo += 1

                if not upd:
                    ans += min(s, c - s)
                    tot += c
                    if tot < n:
                        if lo >= m:  # 处理越界情况
                            return -1
                        try:
                            ll, lr = lo, pa[lo]
                        except IndexError:
                            return -1
                        if ll >= m or lr >= m:
                            return -1
                        d[ll] = d[lr] = 1
                        lo += 1
                        s = f[ll]
                        c = 1

            return ans if (ll < rl and lr > rr) else -1
        finally:
            sys.stdin = original_stdin
