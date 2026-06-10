import json
import logging
import os
from typing import Any, Optional, Tuple, Dict
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from internbootcamp.bootcamps.music_bootcamp.music_utils import (
    create_score_from_data, analyze_parallel_motion
)
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ParallelIntervalDetectorTool(BaseTool):
    """平行五八度检测工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)

    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        
        # 保存任务信息
        self._instance_dict[instance_id] = {
            "identity": identity if identity else {},
            "call_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行平行五八度检测"""
        try:
            current_data = parameters.get("current_data")
            
            if not current_data or len(current_data) < 2:
                return "数据不足，无法检测平行进行（至少需要两个和弦）。", 0.0, {"error": "insufficient_data"}
            
            # 创建 Score 并分析
            score = create_score_from_data(current_data)
            has_p5, has_p8, details = analyze_parallel_motion(score)
            
            if not has_p5 and not has_p8:
                response = "未发现平行五度或平行八度。"
                return response, 0.0, {"has_error": False}
            
            # 构建报告
            report = []
            if has_p5: 
                report.append("检测到平行五度 (Parallel 5ths)。")
            if has_p8: 
                report.append("检测到平行八度 (Parallel 8ves/Unisons)。")
            
            if details:
                report.append("详细错误位置：")
                for d in details:
                    report.append(f"- {d['type']} between {d['voices']}")
            
            response = "\n".join(report)
            
            # 更新调用计数
            self._instance_dict[instance_id]["call_count"] += 1
            
            return response, 0.0, {"has_error": True, "details": details}
            
        except Exception as e:
            logger.error(f"ParallelIntervalDetectorTool 执行错误: {str(e)}")
            return f"检测工具运行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        return 0.0
