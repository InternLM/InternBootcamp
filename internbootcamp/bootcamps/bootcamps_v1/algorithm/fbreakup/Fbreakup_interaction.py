from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.fbreakup.Fbreakup_reward_calculator import FbreakupRewardCalculator

# 导入依赖库
import random
from collections import deque




class FbreakupInteraction(BaseInteraction):
    """Fbreakup交互管理器"""
    
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
        score = FbreakupRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Fbreakup问题！"""
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
    def _generate_single_case(self):
        """生成需要切断一条边的案例（链式结构）"""
        n = random.randint(self.min_nodes, self.max_nodes)
        s, t = 1, n
        roads = []
        for i in range(n-1):
            w = random.randint(self.min_budget, self.max_budget)
            roads.append( (i+1, i+2, w) )

        # 找预算最小的边
        min_idx, (x,y,min_w) = min(enumerate(roads), key=lambda x: x[1][2])
        return {
            'n': n,
            'm': n-1,
            's': s,
            't': t,
            'roads': roads,
            'expected': {
                'min_budget': min_w,
                'c': 1,
                'roads': [min_idx+1]  # 道路编号从1开始
            }
        }

    def _generate_double_case(self):
        """生成需要切断两条边的案例（并行双路径结构）"""
        # s=1, t=4
        roads = [
            (1,2, random.randint(10,50)),  # 路径1-边1
            (2,4, random.randint(10,50)),  # 路径1-边2
            (1,3, random.randint(10,50)),  # 路径2-边1
            (3,4, random.randint(10,50)),  # 路径2-边2
            (2,3, self.max_budget*2)       # 高成本边，不应被选
        ]
        # 最优解为选两条路径各一个最低成本边
        path1 = [roads[0][2], roads[1][2]]
        path2 = [roads[2][2], roads[3][2]]
        min1 = min(path1)
        min2 = min(path2)
        solution = {
            'min_budget': min1 + min2,
            'c': 2,
            'roads': [
                roads.index(r)+1 for r in roads 
                if r[2] in (min1, min2)
            ]
        }
        return {
            'n': 4,
            'm': 5,
            's': 1,
            't': 4,
            'roads': roads,
            'expected': solution
        }

    def _generate_impossible_case(self):
        """生成无法断开连接的案例"""
        return {
            'n': 3,
            'm': 4,
            's': 1,
            't': 3,
            'roads': [
                (1,2, 10), (2,3, 20),
                (1,3, 30), (1,3, 40)
            ],
            'expected': -1
        }

    @staticmethod
    def _is_disconnected(n, roads, s, t, deleted_roads):
        """判断删除指定边后是否断开连接"""
        deleted = set(deleted_roads)
        adj = [[] for _ in range(n+1)]
        for idx, (x,y,w) in enumerate(roads):
            if (idx+1) not in deleted:
                adj[x].append(y)
                adj[y].append(x)

        # BFS检查连通性
        visited = [False]*(n+1)
        queue = deque([s])
        visited[s] = True
        while queue:
            u = queue.popleft()
            if u == t:
                return False
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    queue.append(v)
        return True
