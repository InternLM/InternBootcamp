from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dbuildingbridge.Dbuildingbridge_reward_calculator import DbuildingbridgeRewardCalculator

# 导入依赖库
from math import hypot
import bisect
import random
import re




class DbuildingbridgeInteraction(BaseInteraction):
    """Dbuildingbridge交互管理器"""
    
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
        score = DbuildingbridgeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Dbuildingbridge问题！"""
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
    def compute_optimal_solution(a, b, west_ys, east_ys, l_list):
        delta = b - a
        min_total = float('inf')
        best_pair = (-1, -1)

        # 预处理西岸点的索引映射 (输入已排序，索引即为1-based编号)
        indexed_west = list(enumerate(west_ys, 1))

        for east_idx, (bj_y, lj) in enumerate(zip(east_ys, l_list), 1):
            # 计算最佳西岸匹配点
            target_y = (bj_y * a) / b
            pos = bisect.bisect_left(west_ys, target_y)

            # 检查候选窗口
            candidates = set()
            for offset in (-1, 0, 1):
                k = pos + offset
                if 0 <= k < len(west_ys):
                    candidates.add(k)

            # 遍历所有候选点
            for k in candidates:
                ai_y = west_ys[k]
                total = (
                    hypot(a, ai_y) +          # OAi
                    hypot(delta, bj_y - ai_y) + # AiBj
                    lj                        # lj
                )
                if total < min_total:
                    min_total = total
                    best_pair = (k+1, east_idx)  # 转换为1-based索引

        return best_pair, min_total
