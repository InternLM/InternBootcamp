import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EplumberInstructionGenerator(BaseInstructionGenerator):
    """Eplumber Bootcamp指令生成器"""
    
    def __init__(self, max_size=5, **kwargs):
        """
        初始化Eplumber指令生成器
        
        Args:
            max_size: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_size = max_size  # 控制生成网格的最大行列数
        self.mod = 1000003
    
    def case_generator(self):
        mod = self.mod
        # 生成有效的案例，随机决定是否引入冲突
        n = random.randint(1, self.max_size)
        m = random.randint(1, self.max_size)
        if n * m > 500000:  # 保证n*m <=5e5
            n = m = 1

        # 初始化网格全为未填充
        grid = [['.' for _ in range(m)] for _ in range(n)]
        
        # 随机选择是否生成冲突案例（30%概率生成冲突）
        has_conflict = random.random() < 0.3

        # 随机确定每行和每列的约束方向
        row_dir = {}  # 被约束行的方向
        col_dir = {}  # 被约束列的方向
        
        constrained_rows = set()
        constrained_cols = set()

        # 随机选择部分行作为被约束的
        for i in range(n):
            if random.random() < 0.5 and n > 1:
                constrained_rows.add(i)
                row_dir[i] = random.choice([0, 1])
        
        # 随机选择部分列作为被约束的
        for j in range(m):
            if random.random() < 0.5 and m > 1:
                constrained_cols.add(j)
                col_dir[j] = random.choice([0, 1])

        # 填充部分单元格以满足约束条件
        for i in constrained_rows:
            # 选择该行中一个列来填充
            j = random.choice([j for j in range(m)])
            possible = self.get_possible_types(i, j, row_dir[i], col_dir.get(j, None))
            if not possible and j in col_dir:
                # 如果列也被约束，可能无法找到可能的类型，需要调整
                possible = self.get_possible_types(i, j, row_dir[i], col_dir[j])
                if not possible:
                    # 如果无法找到类型，可能需调整dir
                    row_dir[i] = 1 - row_dir[i]
                    possible = self.get_possible_types(i, j, row_dir[i], col_dir.get(j, None))
            if possible:
                grid[i][j] = str(random.choice(possible))
            else:
                # 无法满足约束，重新生成
                return self.case_generator()

        for j in constrained_cols:
            i = random.choice([i for i in range(n)])
            possible = self.get_possible_types(i, j, row_dir.get(i, None), col_dir[j])
            if not possible and i in row_dir:
                possible = self.get_possible_types(i, j, row_dir[i], col_dir[j])
                if not possible:
                    col_dir[j] = 1 - col_dir[j]
                    possible = self.get_possible_types(i, j, row_dir.get(i, None), col_dir[j])
            if possible:
                grid[i][j] = str(random.choice(possible))
            else:
                return self.case_generator()

        # 引入冲突（如果有冲突标志）
        if has_conflict and (constrained_rows or constrained_cols):
            # 随机选择一个已填充的单元格修改为冲突类型
            filled = [(i,j) for i in range(n) for j in range(m) if grid[i][j] != '.']
            if filled:
                i,j = random.choice(filled)
                current_type = int(grid[i][j])
                possible = self.get_possible_types(i, j, row_dir.get(i, None), col_dir.get(j, None))
                # 选择不在possible中的类型（确保冲突）
                conflict_types = [str(t) for t in [1,2,3,4] if t != current_type and (possible is None or t not in possible)]
                if conflict_types:
                    grid[i][j] = random.choice(conflict_types)
                else:
                    # 无法生成冲突，处理这种情况
                    has_conflict = False

        # 计算未被约束的行和列数
        unconstrained_rows = n - len(constrained_rows)
        unconstrained_cols = m - len(constrained_cols)
        expected = pow(2, unconstrained_rows + unconstrained_cols, mod)
        
        # 检查是否存在冲突
        if has_conflict:
            expected = 0

        # 将网格转换为字符串列表
        grid_str = [''.join(row) for row in grid]
        return {
            'n': n,
            'm': m,
            'grid': grid_str,
            'expected': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        grid = '\n'.join(question_case['grid'])
        prompt = f"""Little John 绘制了一个 {n} 行 {m} 列的网格，每个单元格可能为空（.）或包含1-4号水管。系统漏水当且仅当某管道的末端未连接其他管道或边界。请计算填充所有空单元格后，可能的不漏水方案数目模1000003。

输入:
{n} {m}
{grid}

规则：
- 水管类型1-4的末端方向如题图所示。
- 相邻单元格的末端必须匹配，例如，右边的单元格的左端必须连接当前单元格的右端。
- 网格边缘的管道末端需指向外部以避免漏水。

输出一个整数，模1000003后的结果，置于[answer]标签内。例如：[answer]0[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def get_possible_types(i, j, row_dir, col_dir):
        # 根据行和列约束生成可能的类型，None表示无约束
        possible = set([1,2,3,4])
        # 行约束
        if row_dir is not None:
            if row_dir == 0:
                if j % 2 == 0:
                    row_possible = {1,2}
                else:
                    row_possible = {3,4}
            else: # row_dir ==1
                if j % 2 ==0:
                    row_possible = {3,4}
                else:
                    row_possible = {1,2}
            possible &= row_possible
        # 列约束
        if col_dir is not None:
            if col_dir ==0:
                if i %2 ==0:
                    col_possible = {1,4}
                else:
                    col_possible = {2,3}
            else: # col_dir ==1
                if i%2 ==0:
                    col_possible = {2,3}
                else:
                    col_possible = {1,4}
            possible &= col_possible
        return list(possible) if possible else None
