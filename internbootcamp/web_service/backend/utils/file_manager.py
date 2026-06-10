"""
文件管理工具
"""
import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any


class FileManager:
    """文件管理器"""
    
    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def get_task_dir(self, task_id: str) -> Path:
        """获取任务目录"""
        task_dir = self.base_dir / task_id
        task_dir.mkdir(parents=True, exist_ok=True)
        return task_dir
    
    def get_result_path(self, task_id: str) -> str:
        """获取结果文件路径"""
        return str(self.get_task_dir(task_id) / "results.jsonl")
    
    def get_log_path(self, task_id: str) -> str:
        """获取日志文件路径"""
        return str(self.get_task_dir(task_id) / "task.log")
    
    def get_summary_path(self, task_id: str) -> str:
        """获取汇总文件路径"""
        return str(self.get_task_dir(task_id) / "summary.csv")
    
    def write_jsonl(self, filepath: str, data: Dict[str, Any], append: bool = True):
        """写入JSONL文件"""
        mode = 'a' if append else 'w'
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
    
    def read_jsonl(self, filepath: str, offset: int = 0, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """读取JSONL文件（支持增量读取）"""
        if not os.path.exists(filepath):
            return []
        
        results = []
        with open(filepath, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i < offset:
                    continue
                if limit and len(results) >= limit:
                    break
                if line.strip():
                    try:
                        results.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
        return results
    
    def count_lines(self, filepath: str) -> int:
        """统计文件行数"""
        if not os.path.exists(filepath):
            return 0
        with open(filepath, 'r', encoding='utf-8') as f:
            return sum(1 for line in f if line.strip())
    
    def read_log(self, filepath: str, tail_lines: Optional[int] = None) -> str:
        """读取日志文件"""
        if not os.path.exists(filepath):
            return ""
        
        with open(filepath, 'r', encoding='utf-8') as f:
            if tail_lines:
                lines = f.readlines()
                return ''.join(lines[-tail_lines:])
            return f.read()
    
    def file_exists(self, filepath: str) -> bool:
        """检查文件是否存在"""
        return os.path.exists(filepath)

