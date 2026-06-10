"""
数据模型定义
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskType(str, Enum):
    """任务类型枚举"""
    DATA_GENERATION = "data_generation"
    EVALUATION = "evaluation"


class DataGenerationRequest(BaseModel):
    """数据生成请求"""
    instruction_config: str = Field(..., description="指令配置文件路径")
    output_dir: Optional[str] = Field(None, description="输出目录")
    split_samples: Optional[str] = Field("train:100,test:10", description="数据集划分，格式: train:100,test:10")
    shuffle: bool = Field(True, description="是否打乱数据")
    gen_parquet: bool = Field(False, description="是否生成parquet格式")
    no_tool: bool = Field(False, description="不使用工具配置")
    no_interaction: bool = Field(False, description="不使用交互配置")


class EvaluationRequest(BaseModel):
    """模型评测请求"""
    dataset_path: Optional[str] = Field(None, description="数据集路径（与sample_config二选一）")
    sample_config: Optional[Dict[str, Any]] = Field(None, description="单个样本配置（与dataset_path二选一），包含messages、ground_truth等字段")
    api_key: str = Field(..., description="API密钥")
    api_url: Optional[str] = Field(None, description="API地址")
    api_model: str = Field("gpt-3.5-turbo", description="模型名称")
    api_extra_headers: Optional[str] = Field(None, description="额外请求头，格式: key1:value1,key2:value2")
    api_extra_params: Optional[str] = Field(None, description="额外模型参数，JSON字符串")
    reward_calculator_class: str = Field(..., description="奖励计算器类路径")
    tool_config: Optional[str] = Field(None, description="工具配置文件路径")
    interaction_config: Optional[str] = Field(None, description="交互配置文件路径")
    max_assistant_turns: Optional[int] = Field(5, description="最大assistant轮次")
    max_user_turns: Optional[int] = Field(20, description="最大user轮次")
    max_concurrent: int = Field(1, description="最大并发数")
    tokenizer_path: Optional[str] = Field(None, description="tokenizer路径")
    verify_correction_kwargs: Optional[str] = Field(None, description="验证参数，JSON字符串")


class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    task_type: TaskType
    status: TaskStatus
    created_at: datetime
    updated_at: datetime
    result_path: Optional[str] = None
    log_path: Optional[str] = None
    progress: float = 0.0  # 0-100
    total_samples: int = 0
    completed_samples: int = 0
    error_message: Optional[str] = None


class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskInfo]
    total: int


class SampleResult(BaseModel):
    """单个样本结果"""
    sample_id: Optional[str] = None
    data_source: Optional[str] = None
    generator_name: Optional[str] = None
    score: Optional[float] = None
    success: bool
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    assistant_turns: Optional[int] = None
    tool_calls: Optional[int] = None
    messages: Optional[List[Dict[str, Any]]] = None
    extracted_output: Any = None
    ground_truth: Any = None
    error: Optional[str] = None


class IncrementalResultResponse(BaseModel):
    """增量结果响应"""
    samples: List[SampleResult]
    offset: int
    has_more: bool


class SummaryStats(BaseModel):
    """汇总统计"""
    total_samples: int
    success_count: int
    error_count: int
    success_rate: float
    avg_score: float
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_tokens: int = 0
    avg_prompt_tokens: float = 0.0
    avg_completion_tokens: float = 0.0
    avg_tokens: float = 0.0


class DataSourceStats(BaseModel):
    """数据源统计"""
    data_source: str
    total_count: int
    success_count: int
    error_count: int
    success_rate: float
    avg_score: float
    max_score: float
    min_score: float
    avg_assistant_turns: float
    avg_tool_calls: float
    avg_interaction_turns: float
    avg_prompt_tokens: float
    avg_completion_tokens: float
    avg_tokens: float


class GeneratorStats(BaseModel):
    """生成器统计"""
    generator_name: str
    total_count: int
    success_count: int
    error_count: int
    success_rate: float
    avg_score: float
    max_score: float
    min_score: float
    avg_assistant_turns: float
    avg_tool_calls: float
    avg_interaction_turns: float
    avg_prompt_tokens: float
    avg_completion_tokens: float
    avg_tokens: float


class ErrorInfo(BaseModel):
    """错误信息"""
    data_source: str
    generator_name: Optional[str]
    error: str
    sample_id: str


class EvaluationSummary(BaseModel):
    """评测汇总"""
    summary: SummaryStats
    data_sources: List[DataSourceStats]
    generators: Dict[str, List[GeneratorStats]]
    errors: List[ErrorInfo]


class EvaluationConfig(BaseModel):
    """评测配置（用于保存历史配置）"""
    config_id: str = Field(..., description="配置ID")
    name: str = Field(..., description="配置名称")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    # 评测配置字段
    dataset_path: Optional[str] = None
    sample_config: Optional[Dict[str, Any]] = None
    api_key: str
    api_url: Optional[str] = None
    api_model: str = "gpt-3.5-turbo"
    api_extra_headers: Optional[str] = None
    api_extra_params: Optional[str] = None
    reward_calculator_class: str
    tool_config: Optional[str] = None
    interaction_config: Optional[str] = None
    max_assistant_turns: Optional[int] = 5
    max_user_turns: Optional[int] = 20
    max_concurrent: int = 1
    tokenizer_path: Optional[str] = None
    verify_correction_kwargs: Optional[str] = None


class EvaluationConfigListResponse(BaseModel):
    """评测配置列表响应"""
    configs: List[EvaluationConfig]
    total: int

