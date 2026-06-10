from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.elittleelephantandlcm.Elittleelephantandlcm_reward_calculator import ElittleelephantandlcmRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class ElittleelephantandlcmInteraction(BaseInteraction):
    """Elittleelephantandlcm交互管理器"""
    
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
        score = ElittleelephantandlcmRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Elittleelephantandlcm问题！"""
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
    def _solve(a):
        # 优化后的高效解法实现
        if not a:
            return 0

        # 预处理频率统计
        freq = defaultdict(int)
        max_val = max(a) if a else 0
        for num in a:
            freq[num] += 1

        # 构建dist数组
        dist = {}
        current = 0
        for x in range(max_val, 0, -1):
            current += freq.get(x, 0)
            dist[x] = current

        # 预计算所有数的约数
        divisors = defaultdict(list)
        for d in range(1, max_val + 1):
            for multiple in range(d, max_val + 1, d):
                divisors[multiple].append(d)

        ans = 1  # 初始值对应X=1的情况

        # 主计算逻辑
        for X in range(2, max_val + 1):
            divs = divisors.get(X, [])
            sz = len(divs)
            if sz < 1:
                continue

            # 计算big乘积项
            big = 1
            for j in range(sz - 1):
                d_current = divs[j]
                d_next = divs[j+1]
                cnt = dist.get(d_current, 0) - dist.get(d_next, 0)
                big = (big * pow(j+1, cnt, MOD)) % MOD

            # 处理最后一个约数项
            last_d = divs[-1]
            big = (big * pow(sz, dist.get(last_d, 0), MOD)) % MOD

            # 计算small乘积项
            small = 1
            if sz >= 2:
                for j in range(sz - 2):
                    d_current = divs[j]
                    d_next = divs[j+1]
                    cnt = dist.get(d_current, 0) - dist.get(d_next, 0)
                    small = (small * pow(j+1, cnt, MOD)) % MOD

                second_last_d = divs[-2]
                small = (small * pow(sz-1, dist.get(second_last_d, 0), MOD)) % MOD
            else:
                small = 0

            # 累加有效贡献
            contribution = (big - small) % MOD
            ans = (ans + contribution) % MOD

        return ans % MOD
