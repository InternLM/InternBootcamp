from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.eguessthetree.Eguessthetree_reward_calculator import EguessthetreeRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class EguessthetreeInteraction(BaseInteraction):
    """Eguessthetree交互管理器"""
    
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
        score = EguessthetreeRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Eguessthetree问题！"""
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
    def _generate_initial_n(self, yes_case):
        if yes_case:
            return random.choice([n for n in range(self.min_n, self.max_n+1) if n ==1 or n>=3])
        return random.randint(self.min_n, self.max_n)

    def _generate_valid_case(self, n):
        if n == 1:
            return {'n':1, 'c':[1], 'expected_answer':'YES'}

        # 生成符合约束的树结构
        root = n
        children = self._split_subtrees(n-1)
        c = [root] + children
        random.shuffle(c)
        return {'n':n, 'c':c, 'expected_answer':'YES'}

    def _split_subtrees(self, total):
        if total == 0:
            return []
        if total == 1:
            return [1]

        # 至少分割为两个子树且每个>=1
        k = random.randint(2, total)
        parts = []
        while sum(parts) < total:
            remain = total - sum(parts)
            max_part = min(remain - (k - len(parts) - 1), remain)
            part = random.randint(1, max_part)
            parts.append(part)

        # 确保内部节点有足够子节点
        return [p if p >=2 else 1 for p in parts]

    def _generate_invalid_case(self, n):
        for _ in range(100):
            # 类型1: 缺少根节点
            if random.random() < 0.5:
                c = [random.randint(1, n-1) for _ in range(n)]
                if n not in c:
                    return {'n':n, 'c':c, 'expected_answer':'NO'}

            # 类型2: 存在根节点但结构冲突
            else:
                c = [n] + random.choices([1,1,2,3], k=n-1)
                if not self._is_valid_solution(n, c):
                    return {'n':n, 'c':c, 'expected_answer':'NO'}

        return {'n':2, 'c':[1,1], 'expected_answer':'NO'}

    def _is_valid_solution(self, n, c):
        # 快速预检查
        if sum(c) != n*(n+1)//2 and n > 1:  # 修正总和验证逻辑
            return False

        # 完整回溯验证
        avail = defaultdict(int)
        for num in c:
            if num > n:
                return False
            avail[num] += 1

        try:
            self._backtrack(avail, [], sum(c), n)
            return False
        except self.SolutionFound:
            return True

    def _backtrack(self, avail, stack, sumleft, n):
        if not stack and sumleft == 0:
            raise self.SolutionFound()

        # 添加叶子节点分支
        if avail[1] > 0:
            avail[1] -= 1
            self._backtrack(avail, stack + [1], sumleft - 1, n)
            avail[1] += 1

        # 合并子树分支
        if len(stack) >= 2:
            s = 0
            for i in range(1, len(stack)+1):
                s += stack[-i]
                if s > n:
                    break
                if avail[s] > 0:
                    avail[s] -= 1
                    self._backtrack(avail, stack[:-i] + [s], sumleft - s, n)
                    avail[s] += 1
