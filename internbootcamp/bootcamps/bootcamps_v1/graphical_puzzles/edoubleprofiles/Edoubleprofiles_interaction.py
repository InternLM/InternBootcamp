from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.edoubleprofiles.Edoubleprofiles_reward_calculator import EdoubleprofilesRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class EdoubleprofilesInteraction(BaseInteraction):
    """Edoubleprofiles交互管理器"""
    
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
        score = EdoubleprofilesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Edoubleprofiles问题！"""
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
    @classmethod
    def _compute_answer(cls, case):
        """优化哈希算法实现"""
        MOD = 10**18 + 3
        SEED = 29
        n, edges = case['n'], case['edges']

        # 初始化哈希基数
        p = [1] * (n + 2)
        for i in range(1, n+1):
            p[i] = (p[i-1] * SEED) % MOD

        # 构建特征哈希
        h = defaultdict(int)
        for u, v in edges:
            h[u] = (h[u] + p[v]) % MOD
            h[v] = (h[v] + p[u]) % MOD

        # 统计哈希等价类
        counter = defaultdict(int)
        for uid in range(1, n+1):
            counter[h[uid]] += 1

        # 计算等价类贡献
        ans = sum(c * (c-1) // 2 for c in counter.values())

        # 检查直接边贡献
        processed = set()
        for u, v in edges:
            if (u, v) in processed:
                continue
            if (h[u] + p[u]) % MOD == (h[v] + p[v]) % MOD:
                ans += 1
            processed.add((u, v))

        return ans
