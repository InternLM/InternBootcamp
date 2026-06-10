from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.clatinsquare.Clatinsquare_reward_calculator import ClatinsquareRewardCalculator

# 导入依赖库
import re
import json
from random import randint
from random import choices
from random import shuffle
import random




class ClatinsquareInteraction(BaseInteraction):
    """Clatinsquare交互管理器"""
    
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
        score = ClatinsquareRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Clatinsquare问题！"""
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
    def _compute_final(cls, n, initial_matrix, operations):
        # 转换为0-based索引
        v = [[x-1 for x in row] for row in initial_matrix]
        e = [0, 0, 0]  # 行、列、值的偏移量
        p = [0, 1, 2]  # 映射顺序：行、列、值

        for c in operations:
            if c == 'R':
                e[p[1]] = (e[p[1]] + 1) % n
            elif c == 'L':
                e[p[1]] = (e[p[1]] - 1) % n
            elif c == 'D':
                e[p[0]] = (e[p[0]] + 1) % n
            elif c == 'U':
                e[p[0]] = (e[p[0]] - 1) % n
            elif c == 'I':
                p[1], p[2] = p[2], p[1]  # 交换列和值的映射
            elif c == 'C':
                p[0], p[2] = p[2], p[0]  # 交换行和值的映射

        # 生成最终矩阵
        w = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                # 原始坐标和值
                z = [i, j, v[i][j]]
                # 应用偏移和映射后的坐标
                I = (z[p[0]] + e[p[0]]) % n
                J = (z[p[1]] + e[p[1]]) % n
                K = (z[p[2]] + e[p[2]]) % n
                w[I][J] = K + 1  # 转换回1-based
        return w
