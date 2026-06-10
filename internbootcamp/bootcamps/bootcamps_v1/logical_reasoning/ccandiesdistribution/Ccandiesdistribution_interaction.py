from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.ccandiesdistribution.Ccandiesdistribution_reward_calculator import CcandiesdistributionRewardCalculator

# 导入依赖库
import random
from collections import deque




class CcandiesdistributionInteraction(BaseInteraction):
    """Ccandiesdistribution交互管理器"""
    
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
        score = CcandiesdistributionRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccandiesdistribution问题！"""
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
    def generate_valid_case(self, case_type):
        n = random.randint(self.min_n, self.max_n)
        a = []

        # 生成策略优化
        if case_type == 'valid_standard':
            # 使用拓扑排序生成合法案例
            graph = [[] for _ in range(n)]
            in_degree = [0]*n
            q = deque()

            # 构造约束关系
            for i in range(n):
                for j in range(i+1, n):
                    if random.random() < 0.3:
                        graph[i].append(j)
                        in_degree[j] += 1
                    else:
                        graph[j].append(i) 
                        in_degree[i] += 1

            # 拓扑排序生成合法值
            while q:
                u = q.popleft()
                a.append(random.randint(1, n))
                for v in graph[u]:
                    in_degree[v] -= 1
                    if in_degree[v] == 0:
                        q.append(v)
            a += [random.randint(1, n) for _ in range(n - len(a))]
        else:  # valid_duplicates
            base = random.randint(1, n//2)
            a = [base + i % 3 for i in range(n)]
            random.shuffle(a)

        # 计算合法约束
        l = [sum(a[j] > a[i] for j in range(i)) for i in range(n)]
        r = [sum(a[j] > a[i] for j in range(i+1, n)) for i in range(n)]

        return {
            'n': n,
            'l': l,
            'r': r,
            'solvable': True,
            'type': case_type
        }

    def generate_invalid_case(self, case_type):
        n = random.randint(self.min_n, self.max_n)
        l = [0]*n
        r = [0]*n

        if case_type == 'invalid_boundary':
            # 边界条件无效：首位儿童左边有人，末位儿童右边有人
            targets = [0, n-1] if n > 1 else [0]
            for i in targets:
                if i == 0:
                    l[i] = random.randint(1, 3)
                else:
                    r[i] = random.randint(1, 3)

        elif case_type == 'invalid_overflow':
            # 数值超限：单个值超过理论最大值
            i = random.randint(0, n-1)
            max_possible = i if i < n-1 else 0
            l[i] = max_possible + random.randint(1, 2)

        elif case_type == 'invalid_sum':
            # 总和矛盾：l_i + r_i > 可能的最大值
            i = random.randint(0, n-1)
            max_total = (n - 1) - (i + (n - i - 1))
            if max_total < 0: max_total = 0
            current_sum = random.randint(max_total + 1, max_total + 3)
            l[i] = current_sum // 2
            r[i] = current_sum - l[i]

        return {
            'n': n,
            'l': l,
            'r': r,
            'solvable': False,
            'type': case_type
        }
