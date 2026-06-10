# InternBootcamp 后端 API 文档

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **版本**: 1.0.0

---

## 基础接口

### 根路径
```
GET /
```
返回 API 基本信息。

**响应示例**:
```json
{
  "message": "InternBootcamp 评测平台 API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 健康检查
```
GET /health
```
检查服务健康状态。

**响应示例**:
```json
{
  "status": "healthy"
}
```

---

## 数据生成接口

### 创建数据生成任务
```
POST /api/data-generation/create
```

**请求体**:
```json
{
  "instruction_config": "path/to/config.yaml",
  "output_dir": "outputs/data_generation",  // 可选
  "split_samples": "train:100,test:10",      // 可选，默认 "train:100,test:10"
  "shuffle": true,                            // 可选，默认 true
  "gen_parquet": false,                       // 可选，默认 false
  "no_tool": false,                           // 可选，默认 false
  "no_interaction": false                     // 可选，默认 false
}
```

**响应**: `TaskInfo` 对象

---

## 模型评测接口

### 创建评测任务
```
POST /api/evaluation/create
```

**请求体**:
```json
{
  "dataset_path": "path/to/dataset.jsonl",
  "api_key": "your-api-key",
  "api_url": "https://api.openai.com/v1/chat/completions",  // 可选
  "api_model": "gpt-3.5-turbo",                            // 可选，默认 "gpt-3.5-turbo"
  "api_extra_headers": "key1:value1,key2:value2",          // 可选
  "api_extra_params": "{\"temperature\": 0.7}",            // 可选，JSON字符串
  "reward_calculator_class": "path.to.RewardCalculator",
  "tool_config": "path/to/tool_config.yaml",               // 可选
  "interaction_config": "path/to/interaction_config.yaml", // 可选
  "max_assistant_turns": 5,                                 // 可选，默认 5
  "max_user_turns": 20,                                     // 可选，默认 20
  "max_concurrent": 1,                                      // 可选，默认 1
  "tokenizer_path": "path/to/tokenizer",                    // 可选
  "verify_correction_kwargs": "{\"key\": \"value\"}"       // 可选，JSON字符串
}
```

**响应**: `TaskInfo` 对象

### 获取评测结果（增量）
```
GET /api/evaluation/{task_id}/results?offset=0&limit=50
```

**查询参数**:
- `offset` (int): 起始偏移量，默认 0
- `limit` (int): 返回数量限制，默认 50

**响应**: `IncrementalResultResponse`
```json
{
  "samples": [...],
  "offset": 50,
  "has_more": true
}
```

### 获取评测汇总统计
```
GET /api/evaluation/{task_id}/summary
```

**响应**: `EvaluationSummary` 对象，包含：
- `summary`: 总体统计信息
- `data_sources`: 按数据源统计
- `generators`: 按生成器统计
- `errors`: 错误信息列表

### 下载评测结果文件
```
GET /api/evaluation/{task_id}/download?file_type=jsonl
```

**查询参数**:
- `file_type` (string): 文件类型，可选 `jsonl` 或 `csv`，默认 `jsonl`

**响应**: 文件下载

### 分析评测结果文件
```
POST /api/evaluation/analyze-file?file_path=path/to/results.jsonl&max_samples=4096
```

**查询参数**:
- `file_path` (string, 必需): JSONL 文件路径
- `max_samples` (int): 最大分析样本数，默认 4096

**响应**: 文件统计信息（不包含样本列表）

### 获取文件样本列表（分页、排序）
```
GET /api/evaluation/analyze-file/samples?file_path=path/to/results.jsonl&offset=0&limit=20&sort_by=score&sort_order=desc
```

**查询参数**:
- `file_path` (string, 必需): JSONL 文件路径
- `offset` (int): 起始偏移量，默认 0
- `limit` (int): 返回数量限制，默认 20
- `sort_by` (string, 可选): 排序字段，可选 `score`、`success`、`tokens`
- `sort_order` (string): 排序顺序，可选 `asc` 或 `desc`，默认 `desc`

**响应**:
```json
{
  "samples": [...],
  "offset": 20,
  "has_more": true,
  "total": 4096,
  "sort_by": "score",
  "sort_order": "desc"
}
```

---

## 任务管理接口

### 获取任务列表
```
GET /api/tasks?task_type=evaluation
```

**查询参数**:
- `task_type` (string, 可选): 任务类型，可选 `data_generation` 或 `evaluation`

**响应**: `TaskListResponse`
```json
{
  "tasks": [...],
  "total": 10
}
```

### 获取任务详情
```
GET /api/tasks/{task_id}
```

**响应**: `TaskInfo` 对象

### 取消任务
```
POST /api/tasks/{task_id}/cancel
```

**响应**:
```json
{
  "message": "Task cancelled"
}
```

### 删除任务
```
DELETE /api/tasks/{task_id}
```

**响应**:
```json
{
  "message": "Task deleted"
}
```

### 获取任务日志
```
GET /api/tasks/{task_id}/logs?tail=100
```

**查询参数**:
- `tail` (int, 可选): 返回最后 N 行日志

**响应**:
```json
{
  "logs": "日志内容..."
}
```

---

## 数据模型

### TaskInfo
```json
{
  "task_id": "uuid",
  "task_type": "data_generation" | "evaluation",
  "status": "pending" | "running" | "completed" | "failed" | "cancelled",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "result_path": "path/to/result.jsonl",
  "log_path": "path/to/log.txt",
  "progress": 50.0,
  "total_samples": 100,
  "completed_samples": 50,
  "error_message": null
}
```

### SampleResult
```json
{
  "sample_id": "sample_001",
  "data_source": "source_name",
  "generator_name": "generator_name",
  "score": 0.85,
  "success": true,
  "prompt_tokens": 100,
  "completion_tokens": 200,
  "total_tokens": 300,
  "assistant_turns": 2,
  "tool_calls": 1,
  "messages": [...],
  "extracted_output": {...},
  "ground_truth": {...},
  "error": null
}
```

---

## 状态码

- `200`: 成功
- `400`: 请求参数错误
- `404`: 资源不存在
- `500`: 服务器内部错误

