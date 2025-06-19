

### 谜题描述

The objective of the Bridges puzzle (Hashiwokakero) is to connect all numbered \"islands\" on a grid using horizontal/vertical bridges, adhering to these principles:

1. **Island Numbers**: Each island (node) displays a number (1-8) indicating how many bridges must connect to it.  
   - Example: A \"3\" island must have exactly 3 bridges linked to it.

2. **Bridge Placement**:  
   - Bridges connect **two adjacent islands** horizontally/vertically.  
   - Bridges cannot cross islands, other bridges, or \"turn\" mid-connection.  

3. **Bridge Limits**:  
   - A maximum of **2 bridges** can connect any pair of islands.  
   - Bridges may overlap in straight lines if they connect different island pairs (no crossing).  

4. **Connectivity**:  
   - All islands must be interconnected into a **single continuous network** via bridges.  

Key Constraints:  
- Bridges cannot be placed diagonally.  
- Islands cannot have fewer/more bridges than their number.  
- Overlapping bridges (parallel lines) must align in the same direction without intersecting.  


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random
from collections import defaultdict

class Bridgesbootcamp(Basebootcamp):
    def __init__(self, width=5, height=5):
        self.width = width
        self.height = height

    def case_generator(self):
        direction = random.choice(['horizontal', 'vertical'])
        islands = []
        bridges = []

        if direction == 'horizontal':
            x = random.randint(0, self.width-1)
            y1 = random.randint(0, self.height-3)
            y2 = y1 + 2
            islands = [
                {'x': x, 'y': y1, 'num': 2},
                {'x': x, 'y': y2, 'num': 2},
            ]
            bridges = [{'from': (x, y1), 'to': (x, y2), 'count': 2}]
        else:
            y = random.randint(0, self.height-1)
            x1 = random.randint(0, self.width-3)
            x2 = x1 + 2
            islands = [
                {'x': x1, 'y': y, 'num': 2},
                {'x': x2, 'y': y, 'num': 2},
            ]
            bridges = [{'from': (x1, y), 'to': (x2, y), 'count': 2}]

        return {
            'islands': islands,
            'bridges': bridges
        }

    @staticmethod
    def prompt_func(question_case) -> str:
        islands = question_case['islands']
        islands_desc = []
        for island in islands:
            islands_desc.append(f"坐标({island['x']}, {island['y']})的岛屿数字为{island['num']}。")
        islands_text = '\n'.join(islands_desc)
        prompt = f"""你是Hashiwokakero谜题的解题专家，请根据以下规则连接所有岛屿：

规则：
1. 每个岛屿上的数字表示必须连接的桥梁数目。
2. 桥梁必须水平或竖直连接相邻的岛屿，中间不能有其他岛屿或桥梁阻挡。
3. 每对岛屿之间最多可以建造两座桥梁。
4. 所有岛屿必须通过桥梁连通成一个单一网络。
5. 桥梁不能交叉或转弯。

当前的岛屿分布如下：
{islands_text}

请建造桥梁以满足所有条件，并将答案按照以下格式放置于[answer]和[/answer]之间。每个桥梁的格式为：(x1,y1)-(x2,y2):数量，多个桥梁用换行分隔。

示例：
[answer]
(0,0)-(0,2):2
(1,3)-(3,3):1
[/answer]"""
        return prompt

    @staticmethod
    def extract_output(output):
        pattern = re.compile(r'\[answer\](.*?)\[/answer\]', re.DOTALL)
        matches = pattern.findall(output)
        if not matches:
            return None
        return matches[-1].strip()

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            bridges = []
            pattern = re.compile(r'\((\d+)\s*,\s*(\d+)\)\s*-\s*\((\d+)\s*,\s*(\d+)\)\s*:\s*(\d+)')
            matches = pattern.findall(solution)
            for m in matches:
                x1, y1, x2, y2, cnt = map(int, m)
                if cnt not in (1, 2):
                    return False
                if (x1, y1) > (x2, y2):
                    x1, x2, y1, y2 = x2, x1, y2, y1
                bridges.append({'from': (x1, y1), 'to': (x2, y2), 'count': cnt})

            island_coords = {(i['x'], i['y']) for i in identity['islands']}
            for bridge in bridges:
                if bridge['from'] not in island_coords or bridge['to'] not in island_coords:
                    return False
                x1, y1 = bridge['from']
                x2, y2 = bridge['to']
                if not (x1 == x2 or y1 == y2):
                    return False

                if x1 == x2:
                    y_min, y_max = sorted([y1, y2])
                    for y in range(y_min+1, y_max):
                        if (x1, y) in island_coords:
                            return False
                else:
                    x_min, x_max = sorted([x1, x2])
                    for x in range(x_min+1, x_max):
                        if (x, y1) in island_coords:
                            return False

            bridge_counts = defaultdict(int)
            for bridge in bridges:
                pair = (bridge['from'], bridge['to'])
                bridge_counts[pair] += bridge['count']
            if any(v > 2 for v in bridge_counts.values()):
                return False

            island_num = {(i['x'], i['y']): i['num'] for i in identity['islands']}
            usage = defaultdict(int)
            for bridge in bridges:
                usage[bridge['from']] += bridge['count']
                usage[bridge['to']] += bridge['count']
            for coord, num in island_num.items():
                if usage.get(coord, 0) != num:
                    return False

            bridges_path = []
            for bridge in bridges:
                x1, y1 = bridge['from']
                x2, y2 = bridge['to']
                if x1 == x2:
                    y_start, y_end = sorted([y1, y2])
                    bridges_path.append(('vertical', x1, y_start, y_end))
                else:
                    x_start, x_end = sorted([x1, x2])
                    bridges_path.append(('horizontal', y1, x_start, x_end))

            for i in range(len(bridges_path)):
                ti, ai, si, ei = bridges_path[i]
                for j in range(i+1, len(bridges_path)):
                    tj, aj, sj, ej = bridges_path[j]
                    if ti == tj:
                        continue
                    if ti == 'horizontal':
                        y_h = ai
                        xh_s, xh_e = si, ej
                        x_v = aj
                        yv_s, yv_e = sj, ej
                    else:
                        x_v = ai
                        yv_s, yv_e = si, ei
                        y_h = aj
                        xh_s, xh_e = sj, ej
                    if (xh_s <= x_v <= xh_e) and (yv_s <= y_h <= yv_e):
                        return False

            coord_to_id = {(i['x'], i['y']): idx for idx, i in enumerate(identity['islands'])}
            parent = list(range(len(coord_to_id)))

            def find(u):
                while parent[u] != u:
                    parent[u] = parent[parent[u]]
                    u = parent[u]
                return u

            def union(u, v):
                pu, pv = find(u), find(v)
                if pu != pv:
                    parent[pu] = pv

            for bridge in bridges:
                u = coord_to_id[bridge['from']]
                v = coord_to_id[bridge['to']]
                union(u, v)

            roots = {find(i) for i in range(len(parent))}
            return len(roots) == 1

        except Exception as e:
            return False
