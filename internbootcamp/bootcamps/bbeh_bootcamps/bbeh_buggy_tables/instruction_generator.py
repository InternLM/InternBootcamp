from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_buggy_tables.libs.bbeh_buggy_tables_generator import (
    BBEHBuggyTablesGenerator,
)
from internbootcamp.bootcamps.bbeh_bootcamps.bbeh_buggy_tables.libs.bbeh_buggy_tables_solver import (
    BBEHBuggyTablesSolver,
)


class BbehBuggyTablesInstructionGenerator(BaseInstructionGenerator):
    """BBEH buggy tables 任务的指令生成器。"""

    def __init__(
        self,
        seed: int | None = None,
        task_file_path: str | None = None,
    ):
        super().__init__()
        self._seed = seed
        self._generation_index = 0
        default_task_path = Path(__file__).resolve().parent / "data" / "task.json"
        self._generator = BBEHBuggyTablesGenerator(
            task_file_path or str(default_task_path)
        )
        self._solver = BBEHBuggyTablesSolver()

    def _set_seed(self) -> None:
        if self._seed is None:
            return
        combined_seed = int(self._seed) + self._generation_index
        random.seed(combined_seed)
        np.random.seed(combined_seed & 0xFFFFFFFF)

    def _solve_from_clean_table(self, clean_table: list, query_info: dict) -> float | None:
        """直接从 clean_table 求解，跳过修复步骤（更快）"""
        try:
            # 快速验证查询信息
            if not query_info or not query_info.get('type') or not query_info.get('column'):
                return None
            
            # 创建 DataFrame
            df = pd.DataFrame(clean_table)
            
            # 批量替换 null 字符串
            df = df.replace(['null', 'NULL', 'None', ''], np.nan)
            
            # 快速验证查询列是否存在
            query_column = query_info.get('column')
            if query_column not in df.columns:
                return None
            
            # 转换查询列为数值类型
            df[query_column] = pd.to_numeric(df[query_column], errors='coerce')
            
            # 如果有条件，也需要转换条件列为数值类型
            condition = query_info.get('condition', {})
            if condition:
                condition_column = condition.get('column')
                if condition_column and condition_column in df.columns:
                    df[condition_column] = pd.to_numeric(df[condition_column], errors='coerce')
            
            # 执行查询（execute_query 会处理条件过滤和最终计算）
            result = self._solver.execute_query(df, query_info)
            if result is not None and not np.isnan(result):
                # 根据查询类型做适当的四舍五入
                query_type = query_info.get('type')
                if query_type in ['mean', 'stdev']:
                    result = round(result, 2)
                elif query_type in ['sum', 'median']:
                    result = round(result, 1)
                return float(result)
        except Exception:
            pass
        return None

    def case_generator(self) -> Dict[str, Any]:
        """生成案例，使用优化后的快速求解方法"""
        max_retries = 10  # 限制重试次数，避免无限重试
        for retry in range(max_retries):
            try:
                self._set_seed()
                example = self._generator.generate_example()
                
                # 优先使用 clean_table 直接求解（更快）
                clean_table = example.get("clean_table")
                query_info = example.get("query_info")
                
                if clean_table and query_info:
                    expected_answer = self._solve_from_clean_table(clean_table, query_info)
                else:
                    # 如果没有 clean_table，回退到原始方法
                    expected_answer = self._solver.solve(example)
                    if expected_answer is not None:
                        try:
                            expected_answer = float(expected_answer)
                            if np.isnan(expected_answer):
                                expected_answer = None
                        except (TypeError, ValueError):
                            expected_answer = None
                
                # 验证答案是否有效
                if expected_answer is None or np.isnan(expected_answer):
                    if retry < max_retries - 1:
                        self._generation_index += 1
                        continue  # 重试生成新例子
                    # 最后一次重试，即使答案无效也返回
                    expected_answer = None
                
                identity: Dict[str, Any] = {
                    "input": example["input"],
                    "query_info": query_info,
                    "clean_table": clean_table,
                    "expected_answer": expected_answer,
                }
                self._generation_index += 1
                return identity
                
            except Exception as e:
                if retry < max_retries - 1:
                    self._generation_index += 1
                    continue  # 重试
                # 最后一次重试失败，抛出异常
                raise RuntimeError(f"Failed to generate example after {max_retries} retries: {str(e)}")
        
        # 理论上不会到达这里
        raise RuntimeError(f"Failed to generate example after {max_retries} retries")

    def prompt_func(self, identity: Dict[str, Any]) -> str:
        input_payload = identity.get("input", {})
        table = input_payload.get("table", [])
        bug_description = input_payload.get("bug_description", "")
        query = input_payload.get("query", "")

        table_str = json.dumps(table, ensure_ascii=False, indent=2)
        prompt_lines = [
            "你是一名数据修复与分析专家，需要处理含有缺陷的表格数据。",
            "按照以下步骤完成任务：",
            "1. 根据 bug 描述修复表格，注意恢复潜在缺失值或被污染的列。",
            "2. 在修复后的表格上执行查询。",
            "3. 给出最终的数值答案，保留两位小数。",
            "",
            "输入表格（JSON 行列表形式）：",
            table_str,
            "",
            f"Bug 描述：{bug_description}",
            f"查询：{query}",
            "",
            "请在推理结束后输出：",
            "最终答案: <你的数值结果>",
        ]
        return "\n".join(prompt_lines)


