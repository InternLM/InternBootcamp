"""
API 客户端 - 与后端 FastAPI 通信
"""
import requests
from typing import Dict, Any, List, Optional


class APIClient:
    """API 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发起请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    # ==================== 任务管理 ====================
    
    def list_tasks(self, task_type: Optional[str] = None) -> Dict[str, Any]:
        """获取任务列表"""
        params = {}
        if task_type:
            params["task_type"] = task_type
        return self._make_request("GET", "/api/tasks", params=params)
    
    def get_task(self, task_id: str) -> Dict[str, Any]:
        """获取任务详情"""
        return self._make_request("GET", f"/api/tasks/{task_id}")
    
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """取消任务"""
        return self._make_request("POST", f"/api/tasks/{task_id}/cancel")
    
    def delete_task(self, task_id: str) -> Dict[str, Any]:
        """删除任务"""
        return self._make_request("DELETE", f"/api/tasks/{task_id}")
    
    def get_task_logs(self, task_id: str, tail: Optional[int] = None) -> Dict[str, Any]:
        """获取任务日志"""
        params = {}
        if tail:
            params["tail"] = tail
        return self._make_request("GET", f"/api/tasks/{task_id}/logs", params=params)
    
    # ==================== 数据生成 ====================
    
    def create_data_generation_task(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建数据生成任务"""
        return self._make_request("POST", "/api/data-generation/create", json=config)
    
    # ==================== 模型评测 ====================
    
    def create_evaluation_task(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建评测任务"""
        return self._make_request("POST", "/api/evaluation/create", json=config)
    
    def get_evaluation_results(self, task_id: str, offset: int = 0, limit: int = 50) -> Dict[str, Any]:
        """获取评测结果（增量）"""
        params = {"offset": offset, "limit": limit}
        return self._make_request("GET", f"/api/evaluation/{task_id}/results", params=params)
    
    def get_evaluation_summary(self, task_id: str) -> Dict[str, Any]:
        """获取评测汇总统计"""
        return self._make_request("GET", f"/api/evaluation/{task_id}/summary")
    
    def download_evaluation_results(self, task_id: str, file_type: str = "jsonl") -> bytes:
        """下载评测结果文件"""
        url = f"{self.base_url}/api/evaluation/{task_id}/download"
        params = {"file_type": file_type}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            return b""
    
    # ==================== 结果分析 ====================
    
    def analyze_file(self, file_path: str, max_samples: int = 4096) -> Dict[str, Any]:
        """分析评测结果文件（仅返回统计信息）"""
        params = {"file_path": file_path, "max_samples": max_samples}
        return self._make_request("POST", "/api/evaluation/analyze-file", params=params)
    
    def get_file_samples(
        self, 
        file_path: str, 
        offset: int = 0, 
        limit: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """获取文件的样本列表（分页，支持排序）"""
        params = {"file_path": file_path, "offset": offset, "limit": limit}
        if sort_by:
            params["sort_by"] = sort_by
            params["sort_order"] = sort_order
        return self._make_request("GET", "/api/evaluation/analyze-file/samples", params=params)
    
    # ==================== 评测配置管理 ====================
    
    def save_evaluation_config(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """保存评测配置"""
        params = {"name": name}
        return self._make_request("POST", "/api/evaluation/configs", params=params, json=config)
    
    def list_evaluation_configs(self) -> Dict[str, Any]:
        """获取所有评测配置"""
        return self._make_request("GET", "/api/evaluation/configs")
    
    def get_evaluation_config(self, config_id: str) -> Dict[str, Any]:
        """获取指定评测配置"""
        return self._make_request("GET", f"/api/evaluation/configs/{config_id}")
    
    def update_evaluation_config(self, config_id: str, name: Optional[str] = None, config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """更新评测配置"""
        params = {}
        if name:
            params["name"] = name
        json_data = config if config else None
        return self._make_request("PUT", f"/api/evaluation/configs/{config_id}", params=params, json=json_data)
    
    def delete_evaluation_config(self, config_id: str) -> Dict[str, Any]:
        """删除评测配置"""
        return self._make_request("DELETE", f"/api/evaluation/configs/{config_id}")

