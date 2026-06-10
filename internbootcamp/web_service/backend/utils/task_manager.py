"""
任务管理器 - 管理后台任务的生命周期
"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from internbootcamp.web_service.backend.models.schemas import TaskInfo, TaskStatus, TaskType


class TaskManager:
    """任务管理器"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskInfo] = {}
        self.task_futures: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()
    
    def create_task(self, task_type: TaskType, result_path: str, log_path: str) -> str:
        """创建新任务"""
        task_id = str(uuid.uuid4())
        task_info = TaskInfo(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            result_path=result_path,
            log_path=log_path,
        )
        self.tasks[task_id] = task_info
        return task_id
    
    async def start_task(self, task_id: str, coro):
        """启动任务"""
        async with self._lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not found")
            
            self.tasks[task_id].status = TaskStatus.RUNNING
            self.tasks[task_id].updated_at = datetime.now()
            
            # 创建后台任务
            task = asyncio.create_task(self._run_task(task_id, coro))
            self.task_futures[task_id] = task
    
    async def _run_task(self, task_id: str, coro):
        """运行任务（内部方法）"""
        try:
            await coro
            async with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.COMPLETED
                    self.tasks[task_id].updated_at = datetime.now()
        except Exception as e:
            async with self._lock:
                if task_id in self.tasks:
                    self.tasks[task_id].status = TaskStatus.FAILED
                    self.tasks[task_id].error_message = str(e)
                    self.tasks[task_id].updated_at = datetime.now()
        finally:
            # 清理任务future
            if task_id in self.task_futures:
                del self.task_futures[task_id]
    
    async def update_progress(self, task_id: str, completed: int, total: int):
        """更新任务进度"""
        async with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].completed_samples = completed
                self.tasks[task_id].total_samples = total
                self.tasks[task_id].progress = (completed / total * 100) if total > 0 else 0.0
                self.tasks[task_id].updated_at = datetime.now()
    
    async def cancel_task(self, task_id: str):
        """取消任务"""
        async with self._lock:
            if task_id in self.task_futures:
                self.task_futures[task_id].cancel()
            
            if task_id in self.tasks:
                self.tasks[task_id].status = TaskStatus.CANCELLED
                self.tasks[task_id].updated_at = datetime.now()
    
    def get_task(self, task_id: str) -> Optional[TaskInfo]:
        """获取任务信息"""
        return self.tasks.get(task_id)
    
    def list_tasks(self, task_type: Optional[TaskType] = None) -> list[TaskInfo]:
        """列出所有任务"""
        tasks = list(self.tasks.values())
        if task_type:
            tasks = [t for t in tasks if t.task_type == task_type]
        # 按创建时间倒序排列
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)
    
    async def delete_task(self, task_id: str):
        """删除任务"""
        async with self._lock:
            if task_id in self.task_futures:
                self.task_futures[task_id].cancel()
                del self.task_futures[task_id]
            
            if task_id in self.tasks:
                del self.tasks[task_id]


# 全局任务管理器实例
task_manager = TaskManager()

