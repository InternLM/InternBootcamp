from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.evectors.Evectors_reward_calculator import EvectorsRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import List

# === 源文件中的全局函数 ===

def rotate_clockwise(x: int, y: int, times: int) -> (int, int):
    """顺时针旋转向量，times为旋转次数"""
    for _ in range(times % 4):
        x, y = y, -x
    return x, y

def possible(dx: int, dy: int, p: int, q: int) -> bool:
    """验证差分向量是否符合线性组合条件"""
    bm = p**2 + q**2
    if bm == 0:
        return dx == 0 and dy == 0
    return ((-p*dx - q*dy) % bm == 0) and ((-q*dx + p*dy) % bm == 0)

def is_possible(ax: int, ay: int, bx: int, by: int, p: int, q: int) -> bool:
    """验证所有旋转可能性"""
    for rot in range(4):
        rx, ry = rotate_clockwise(ax, ay, rot)
        dx, dy = bx - rx, by - ry
        if possible(dx, dy, p, q) or possible(-dy, dx, p, q):
            return True
    return False


class EvectorsInteraction(BaseInteraction):
    """Evectors交互管理器"""
    
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
        score = EvectorsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Evectors问题！"""
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
    def _gen_solvable_case(self) -> Dict:
        """生成保证可解的案例"""
        ax = random.randint(-self.max_coord, self.max_coord)
        ay = random.randint(-self.max_coord, self.max_coord)
        p = random.randint(-self.max_coord, self.max_coord)
        q = random.randint(-self.max_coord, self.max_coord)

        # 随机选择旋转次数和系数
        rot = random.randint(0, 3)
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)

        # 构造合法B向量
        rx, ry = rotate_clockwise(ax, ay, rot)
        bx = rx + a*p + b*q
        by = ry + a*q - b*p
        return {'A': [ax, ay], 'B': [bx, by], 'C': [p, q]}

    def _gen_unsolvable_zeroC(self) -> Dict:
        """生成C=0时的不可解案例"""
        ax = random.randint(-self.max_coord, self.max_coord)
        ay = random.randint(-self.max_coord, self.max_coord)
        p = q = 0

        # 寻找不在旋转对称点上的B
        while True:
            bx = random.randint(-self.max_coord, self.max_coord)
            by = random.randint(-self.max_coord, self.max_coord)
            if not any((bx, by) == rotate_clockwise(ax, ay, r) for r in range(4)):
                return {'A': [ax, ay], 'B': [bx, by], 'C': [p, q]}

    def _gen_unsolvable_general(self) -> Dict:
        """生成普通不可解案例"""
        for _ in range(100):
            case = self._gen_solvable_case()
            ax, ay = case['A']
            bx, by = case['B']
            p, q = case['C']

            # 微调B向量破坏可解性
            delta = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            new_bx = bx + delta[0]
            new_by = by + delta[1]
            if not is_possible(ax, ay, new_bx, new_by, p, q):
                return {'A': [ax, ay], 'B': [new_bx, new_by], 'C': [p, q]}
        return {'A': [0,0], 'B': [1,0], 'C': [0,0]}  # 最终后备案例
