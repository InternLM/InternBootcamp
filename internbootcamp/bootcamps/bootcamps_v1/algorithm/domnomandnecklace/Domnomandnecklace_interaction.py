from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.domnomandnecklace.Domnomandnecklace_reward_calculator import DomnomandnecklaceRewardCalculator

# 导入依赖库
import re
import random




class DomnomandnecklaceInteraction(BaseInteraction):
    """Domnomandnecklace交互管理器"""
    
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
        score = DomnomandnecklaceRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Domnomandnecklace问题！"""
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
    def compute_z(s):
        # 保持与C++完全一致的Z算法实现
        n = len(s)
        z = [0] * n
        z[0] = n  # 空字符匹配整个字符串
        l, r = 0, 0
        for i in range(1, n):
            if i > r:
                l = r = i
                while r < n and s[r - l] == s[r]:
                    r += 1
                z[i] = r - l
                r -= 1
            else:
                k = i - l
                if z[k] < r - i + 1:
                    z[i] = z[k]
                else:
                    l = i
                    while r < n and s[r - l] == s[r]:
                        r += 1
                    z[i] = r - l
                    r -= 1
        return z

    def solve(self, n, k, s):
        # 移除k=0处理分支
        if k == 0:
            return '0' * n
        z = self.compute_z(s)
        ans = [0] * (n + 2)  # 增加缓冲空间

        for lenAB in range(1, n + 1):
            # 检查前k个B是否满足条件
            valid = True
            current_pos = lenAB
            for _ in range(k - 1):
                if current_pos >= n:
                    valid = False
                    break
                required = lenAB
                if current_pos + required > n:
                    if z[current_pos] < n - current_pos:
                        valid = False
                        break
                else:
                    if z[current_pos] < required:
                        valid = False
                        break
                current_pos += lenAB

            if not valid:
                continue

            # 计算可选A的长度范围
            l = lenAB * k - 1
            if l >= n:
                continue

            a_start = lenAB * k
            if a_start >= n:
                max_a = 0
            else:
                max_a = z[a_start]

            possible_a = min(lenAB, max_a)
            r = l + possible_a

            # 修正差分数组标记
            end = min(r, n)
            ans[l] += 1
            if end < n:
                ans[end + 1] -= 1
            else:
                ans[n] -= 1

        # 重建结果数组
        res = []
        current = 0
        for i in range(n):
            current += ans[i]
            res.append('1' if current > 0 else '0')
        return ''.join(res)
