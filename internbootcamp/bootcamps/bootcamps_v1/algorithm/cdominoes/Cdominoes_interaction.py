from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cdominoes.Cdominoes_reward_calculator import CdominoesRewardCalculator

# 导入依赖库
import random
import math
from collections import defaultdict




class CdominoesInteraction(BaseInteraction):
    """Cdominoes交互管理器"""
    
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
        score = CdominoesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cdominoes问题！"""
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
    def generate_valid_set(self):
        """生成包含可优化空间的有效集合"""
        total = self.n * self.m
        while True:
            types = ['00', '01', '10', '11']
            probs = [0.25, 0.25, 0.25, 0.25]
            dominoes = random.choices(types, weights=probs, k=total)
            if sum(1 for d in dominoes if d in ['01','10']) > 0:
                return dominoes

    def build_optimal_matrix(self, domino_set):
        """按照官方解题算法构建最优矩阵"""
        # 统计类型
        k = defaultdict(int)
        for d in domino_set:
            if d in ['00','11']:
                k[d] += 1
            else:
                k['mix'] += 1

        # 初始化二维矩阵
        matrix = [[] for _ in range(self.n)]

        # 类型划分（参考官方解法）
        a = k['11'] // self.n
        b = (k['mix'] // 2) // self.n
        c = k['00'] // self.n

        # 基础分配
        for row in matrix:
            row += ['11']*a
            row += ['01']*b
            row += ['10']*b
            row += ['00']*c

        # 余数处理
        rem_11 = k['11'] % self.n
        rem_mix = k['mix'] % (2*self.n)
        rem_00 = k['00'] % self.n

        # Phase 1: 分配余数11
        for i in range(rem_11):
            matrix[i].append('11')

        # Phase 2: 分配余数mix
        for i in range(rem_mix):
            matrix[i%self.n].append('01' if i%2 else '10')

        # Phase 3: 分配余数00
        for i in range(rem_00):
            matrix[i].append('00')

        # 填充并校验每行长度
        for row in matrix:
            random.shuffle(row)
            while len(row) < self.m:
                # 异常处理：补充虚拟domino（理论上不应触发）
                row.append('00')
            del row[self.m:]  # 精确截断

        return matrix

    def scramble_matrix(self, matrix):
        """生成随机输入矩阵"""
        scrambled = []
        for row in matrix:
            new_row = []
            for d in row:
                if d in ['01','10']:
                    new_row.append(random.choice([d, d[::-1]]))
                else:
                    new_row.append(d)
            random.shuffle(new_row)
            scrambled.append(new_row)
        return scrambled
