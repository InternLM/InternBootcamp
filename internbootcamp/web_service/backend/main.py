"""
FastAPI 主应用
"""
import os
import asyncio
import uuid
import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from pathlib import Path

from internbootcamp.web_service.backend.models.schemas import (
    DataGenerationRequest, EvaluationRequest, TaskInfo, TaskListResponse,
    IncrementalResultResponse, SampleResult, EvaluationSummary,
    TaskType, TaskStatus, EvaluationConfig, EvaluationConfigListResponse
)
from internbootcamp.web_service.backend.services.data_generation import DataGenerationService
from internbootcamp.web_service.backend.services.evaluation import EvaluationService
from internbootcamp.web_service.backend.utils.task_manager import task_manager
from internbootcamp.web_service.backend.utils.file_manager import FileManager
from internbootcamp.web_service.backend.utils.result_parser import ResultParser

app = FastAPI(
    title="InternBootcamp 评测平台",
    description="数据生成与模型评测可视化平台",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化文件管理器
file_manager = FileManager(base_dir="outputs")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "InternBootcamp 评测平台 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


# ==================== 数据生成相关接口 ====================

@app.post("/api/data-generation/create", response_model=TaskInfo)
async def create_data_generation_task(request: DataGenerationRequest):
    """创建数据生成任务"""
    # 生成输出目录
    output_dir = request.output_dir or "outputs/data_generation"
    
    # 先生成task_id用于创建任务
    task_id = str(uuid.uuid4())
    
    # 使用task_id创建日志和结果路径
    log_path = file_manager.get_log_path(task_id)
    
    # 创建任务（使用预生成的task_id）
    task_manager.tasks[task_id] = TaskInfo(
        task_id=task_id,
        task_type=TaskType.DATA_GENERATION,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        result_path=output_dir,
        log_path=log_path,
    )
    
    # 启动后台任务
    async def run_generation():
        try:
            await DataGenerationService.generate_data(
                instruction_config=request.instruction_config,
                output_dir=output_dir,
                split_samples=request.split_samples,
                shuffle=request.shuffle,
                gen_parquet=request.gen_parquet,
                no_tool=request.no_tool,
                no_interaction=request.no_interaction,
                log_path=log_path,
            )
        except Exception as e:
            print(f"数据生成任务失败: {e}")
            raise
    
    await task_manager.start_task(task_id, run_generation())
    
    return task_manager.get_task(task_id)


# ==================== 模型评测相关接口 ====================

@app.post("/api/evaluation/create", response_model=TaskInfo)
async def create_evaluation_task(request: EvaluationRequest):
    """创建评测任务"""
    # 生成任务ID和文件路径
    output_dir = "outputs/evaluation"
    
    # 先生成task_id用于创建任务
    task_id = str(uuid.uuid4())
    
    # 使用task_id创建日志和结果路径
    result_path = file_manager.get_result_path(task_id)
    log_path = file_manager.get_log_path(task_id)
    
    # 创建任务（使用预生成的task_id）
    task_manager.tasks[task_id] = TaskInfo(
        task_id=task_id,
        task_type=TaskType.EVALUATION,
        status=TaskStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        result_path=result_path,
        log_path=log_path,
    )
    
    # 获取任务信息
    task_info = task_manager.get_task(task_id)
    
    # 计算总样本数
    total_samples = 0
    if request.dataset_path:
        # 从数据集文件计算总数
        from internbootcamp.src.base_evaluator import load_dataset
        try:
            dataset = load_dataset(request.dataset_path)
            total_samples = len(dataset)
        except Exception as e:
            print(f"无法计算数据集总数: {e}")
            total_samples = 0
    elif request.sample_config:
        # 单个样本配置
        total_samples = 1
    
    # 初始化进度
    await task_manager.update_progress(task_id, 0, total_samples)
    
    # 启动后台任务
    async def run_evaluation():
        try:
            actual_result_path = None
            task_start_time = datetime.now()
            
            # 尝试在预期目录下查找结果文件（仅查找任务创建后生成的文件，避免冲突）
            def find_result_file_in_expected_dir():
                """在预期目录下查找结果文件（仅查找任务创建后生成的文件）"""
                if actual_result_path and os.path.exists(actual_result_path):
                    return actual_result_path
                # 根据 output_dir 和 api_model 查找结果文件
                model_dir = Path(output_dir) / request.api_model.replace('/', '-').strip('-')
                if model_dir.exists():
                    # 只查找任务创建后生成的文件，避免与其他任务冲突
                    result_files = [
                        f for f in model_dir.glob("eval_results_*.jsonl")
                        if os.path.getmtime(f) >= task_start_time.timestamp()
                    ]
                    if result_files:
                        # 按修改时间排序，取最新的（但必须是任务创建后的）
                        result_files.sort(key=os.path.getmtime, reverse=True)
                        return str(result_files[0])
                return None
            
            # 定期更新进度
            async def update_progress():
                nonlocal actual_result_path
                while True:
                    await asyncio.sleep(2)
                    # 优先使用已设置的结果文件路径
                    result_path = actual_result_path
                    # 如果还没有，尝试在预期目录下查找（仅查找任务创建后的文件）
                    if not result_path:
                        result_path = find_result_file_in_expected_dir()
                    
                    if result_path and os.path.exists(result_path):
                        try:
                            completed = file_manager.count_lines(result_path)
                            await task_manager.update_progress(task_id, completed, total_samples)
                            # 如果找到了文件但 actual_result_path 还没设置，更新它
                            if not actual_result_path:
                                actual_result_path = result_path
                                task_info.result_path = result_path
                        except Exception as e:
                            # 忽略文件读取错误，继续更新
                            print(f"更新进度时出错: {e}")
            
            # 启动进度更新任务
            progress_task = asyncio.create_task(update_progress())
            
            try:
                result_path = await EvaluationService.run_evaluation(
                    output_dir=output_dir,
                    api_key=request.api_key,
                    api_url=request.api_url,
                    api_model=request.api_model,
                    reward_calculator_class=request.reward_calculator_class,
                    dataset_path=request.dataset_path,
                    sample_config=request.sample_config,
                    api_extra_headers=request.api_extra_headers,
                    api_extra_params=request.api_extra_params,
                    verify_correction_kwargs=request.verify_correction_kwargs,
                    tool_config=request.tool_config,
                    interaction_config=request.interaction_config,
                    max_assistant_turns=request.max_assistant_turns,
                    max_user_turns=request.max_user_turns,
                    max_concurrent=request.max_concurrent,
                    tokenizer_path=request.tokenizer_path,
                    task_id=task_id,
                )
                
                # 更新任务结果路径
                if result_path:
                    actual_result_path = result_path
                    task_info.result_path = result_path
                    # 立即更新一次进度
                    try:
                        completed = file_manager.count_lines(result_path)
                        await task_manager.update_progress(task_id, completed, total_samples)
                    except Exception as e:
                        print(f"最终更新进度时出错: {e}")
            finally:
                # 等待一小段时间确保最终进度更新
                await asyncio.sleep(1)
                progress_task.cancel()
                # 最后一次尝试更新进度
                final_result_path = actual_result_path or find_result_file_in_expected_dir()
                if final_result_path and os.path.exists(final_result_path):
                    try:
                        completed = file_manager.count_lines(final_result_path)
                        await task_manager.update_progress(task_id, completed, total_samples)
                        # 确保任务结果路径被设置
                        if not actual_result_path:
                            actual_result_path = final_result_path
                            task_info.result_path = final_result_path
                    except Exception as e:
                        print(f"最后更新进度时出错: {e}")
                
        except Exception as e:
            print(f"评测任务失败: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    await task_manager.start_task(task_id, run_evaluation())
    
    return task_manager.get_task(task_id)


@app.get("/api/evaluation/{task_id}/results", response_model=IncrementalResultResponse)
async def get_evaluation_results(
    task_id: str,
    offset: int = Query(0, description="起始偏移量"),
    limit: int = Query(50, description="返回数量限制")
):
    """获取评测结果（增量）"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.result_path or not os.path.exists(task.result_path):
        return IncrementalResultResponse(samples=[], offset=offset, has_more=False)
    
    # 读取JSONL文件
    raw_results = file_manager.read_jsonl(task.result_path, offset=offset, limit=limit)
    
    # 解析结果
    samples = []
    for raw in raw_results:
        parsed = ResultParser.parse_sample_result(raw)
        samples.append(SampleResult(**parsed))
    
    # 检查是否还有更多数据
    total_lines = file_manager.count_lines(task.result_path)
    has_more = (offset + len(samples)) < total_lines
    
    return IncrementalResultResponse(
        samples=samples,
        offset=offset + len(samples),
        has_more=has_more
    )


@app.get("/api/evaluation/{task_id}/summary", response_model=EvaluationSummary)
async def get_evaluation_summary(task_id: str):
    """获取评测汇总统计"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.result_path or not os.path.exists(task.result_path):
        raise HTTPException(status_code=404, detail="Results not found")
    
    # 读取所有结果
    raw_results = file_manager.read_jsonl(task.result_path)
    
    # 解析结果
    parsed_results = [ResultParser.parse_sample_result(raw) for raw in raw_results]
    
    # 计算统计
    summary = ResultParser.calculate_summary(parsed_results)
    data_source_stats = ResultParser.calculate_data_source_stats(parsed_results)
    generator_stats = ResultParser.calculate_generator_stats(parsed_results)
    errors = ResultParser.extract_errors(parsed_results)
    
    return EvaluationSummary(
        summary=summary,
        data_sources=list(data_source_stats.values()),
        generators=generator_stats,
        errors=errors
    )


@app.get("/api/evaluation/{task_id}/download")
async def download_evaluation_results(task_id: str, file_type: str = Query("jsonl", regex="^(jsonl|csv)$")):
    """下载评测结果文件"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if file_type == "jsonl":
        file_path = task.result_path
    else:  # csv
        file_path = task.result_path.replace(".jsonl", ".csv")
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=os.path.basename(file_path),
        media_type="application/octet-stream"
    )


@app.post("/api/evaluation/analyze-file")
async def analyze_evaluation_file(
    file_path: str = Query(..., description="JSONL文件路径"),
    max_samples: int = Query(4096, description="最大分析样本数（用于统计）")
):
    """分析指定的评测结果文件（不需要关联任务）- 仅返回统计信息"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_path.endswith('.jsonl'):
        raise HTTPException(status_code=400, detail="Only JSONL files are supported")
    
    try:
        # 检查文件大小
        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
        
        # 读取结果（限制数量以提高性能）
        raw_results = file_manager.read_jsonl(file_path, limit=max_samples)
        
        if not raw_results:
            raise HTTPException(status_code=400, detail="File is empty or invalid")
        
        total_lines = file_manager.count_lines(file_path)
        is_truncated = total_lines > max_samples
        
        # 解析结果
        parsed_results = []
        for raw in raw_results:
            try:
                parsed = ResultParser.parse_sample_result(raw)
                parsed_results.append(parsed)
            except Exception as e:
                # 跳过解析失败的样本
                print(f"Failed to parse sample: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        if not parsed_results:
            raise HTTPException(status_code=400, detail="No valid samples found")
        
        # 计算统计
        summary = ResultParser.calculate_summary(parsed_results)
        data_source_stats = ResultParser.calculate_data_source_stats(parsed_results)
        generator_stats = ResultParser.calculate_generator_stats(parsed_results)
        errors = ResultParser.extract_errors(parsed_results)
        
        return {
            "file_path": file_path,
            "file_size_mb": round(file_size, 2),
            "total_samples": total_lines,
            "analyzed_samples": len(parsed_results),
            "is_truncated": is_truncated,
            "summary": summary,
            "data_sources": list(data_source_stats.values()),
            "generators": generator_stats,
            "errors": errors,
            # 不再返回samples列表
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to analyze file: {str(e)}")


@app.get("/api/evaluation/analyze-file/samples")
async def get_file_samples(
    file_path: str = Query(..., description="JSONL文件路径"),
    offset: int = Query(0, description="起始偏移量"),
    limit: int = Query(20, description="返回数量限制"),
    sort_by: Optional[str] = Query(None, description="排序字段: score, success, tokens"),
    sort_order: str = Query("desc", description="排序顺序: asc, desc")
):
    """获取指定文件的样本列表（分页，支持排序）"""
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_path.endswith('.jsonl'):
        raise HTTPException(status_code=400, detail="Only JSONL files are supported")
    
    try:
        # 如果需要排序，需要读取所有样本
        if sort_by:
            # 读取所有结果
            raw_results = file_manager.read_jsonl(file_path)
            
            # 解析所有结果
            all_samples = []
            for raw in raw_results:
                try:
                    parsed = ResultParser.parse_sample_result(raw)
                    all_samples.append(parsed)
                except Exception as e:
                    print(f"Failed to parse sample: {e}")
                    continue
            
            # 排序
            reverse = (sort_order == "desc")
            if sort_by == "score":
                all_samples.sort(key=lambda x: x.get("score", 0), reverse=reverse)
            elif sort_by == "success":
                all_samples.sort(key=lambda x: x.get("success", False), reverse=reverse)
            elif sort_by == "tokens":
                all_samples.sort(key=lambda x: x.get("total_tokens", 0), reverse=reverse)
            
            # 分页
            total_lines = len(all_samples)
            samples = all_samples[offset:offset+limit]
        else:
            # 不排序，直接读取指定范围
            raw_results = file_manager.read_jsonl(file_path, offset=offset, limit=limit)
            
            # 解析结果
            samples = []
            for raw in raw_results:
                try:
                    parsed = ResultParser.parse_sample_result(raw)
                    samples.append(parsed)
                except Exception as e:
                    print(f"Failed to parse sample: {e}")
                    continue
            
            total_lines = file_manager.count_lines(file_path)
        
        # 检查是否还有更多数据
        has_more = (offset + len(samples)) < total_lines
        
        return {
            "samples": samples,
            "offset": offset + len(samples),
            "has_more": has_more,
            "total": total_lines,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to read samples: {str(e)}")


# ==================== 任务管理相关接口 ====================

@app.get("/api/tasks", response_model=TaskListResponse)
async def list_tasks(task_type: Optional[TaskType] = None):
    """获取任务列表"""
    tasks = task_manager.list_tasks(task_type=task_type)
    return TaskListResponse(tasks=tasks, total=len(tasks))


@app.get("/api/tasks/{task_id}", response_model=TaskInfo)
async def get_task(task_id: str):
    """获取任务详情"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.post("/api/tasks/{task_id}/cancel")
async def cancel_task(task_id: str):
    """取消任务"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await task_manager.cancel_task(task_id)
    return {"message": "Task cancelled"}


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """删除任务"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    await task_manager.delete_task(task_id)
    return {"message": "Task deleted"}


@app.get("/api/tasks/{task_id}/logs")
async def get_task_logs(task_id: str, tail: Optional[int] = Query(None, description="返回最后N行")):
    """获取任务日志"""
    task = task_manager.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.log_path or not os.path.exists(task.log_path):
        return {"logs": ""}
    
    logs = file_manager.read_log(task.log_path, tail_lines=tail)
    return {"logs": logs}


# ==================== 评测配置管理相关接口 ====================

# 配置文件存储路径
CONFIG_STORAGE_DIR = Path("outputs/evaluation_configs")
CONFIG_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


@app.post("/api/evaluation/configs", response_model=EvaluationConfig)
async def save_evaluation_config(
    name: str = Query(..., description="配置名称"),
    config: EvaluationRequest = ...,
):
    """保存评测配置"""
    config_id = str(uuid.uuid4())
    now = datetime.now()
    
    eval_config = EvaluationConfig(
        config_id=config_id,
        name=name,
        created_at=now,
        updated_at=now,
        dataset_path=config.dataset_path,
        sample_config=config.sample_config,
        api_key=config.api_key,
        api_url=config.api_url,
        api_model=config.api_model,
        api_extra_headers=config.api_extra_headers,
        api_extra_params=config.api_extra_params,
        reward_calculator_class=config.reward_calculator_class,
        tool_config=config.tool_config,
        interaction_config=config.interaction_config,
        max_assistant_turns=config.max_assistant_turns,
        max_user_turns=config.max_user_turns,
        max_concurrent=config.max_concurrent,
        tokenizer_path=config.tokenizer_path,
        verify_correction_kwargs=config.verify_correction_kwargs,
    )
    
    # 保存到文件（持久化存储）
    config_file = CONFIG_STORAGE_DIR / f"{config_id}.json"
    try:
        # 将配置转换为字典，并处理datetime序列化
        config_dict = eval_config.dict()
        # 确保datetime使用ISO格式字符串
        if isinstance(config_dict.get("created_at"), datetime):
            config_dict["created_at"] = config_dict["created_at"].isoformat()
        if isinstance(config_dict.get("updated_at"), datetime):
            config_dict["updated_at"] = config_dict["updated_at"].isoformat()
        
        # 使用临时文件确保原子写入
        temp_file = config_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(config_dict, f, indent=2, ensure_ascii=False)
        # 原子性重命名
        temp_file.replace(config_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
    
    return eval_config


@app.get("/api/evaluation/configs", response_model=EvaluationConfigListResponse)
async def list_evaluation_configs():
    """获取所有评测配置"""
    configs = []
    
    if CONFIG_STORAGE_DIR.exists():
        for config_file in CONFIG_STORAGE_DIR.glob("*.json"):
            # 跳过临时文件
            if config_file.suffix == ".tmp":
                continue
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    config_data = json.load(f)
                    # 解析datetime字符串（支持ISO格式）
                    if "created_at" in config_data and isinstance(config_data["created_at"], str):
                        try:
                            config_data["created_at"] = datetime.fromisoformat(config_data["created_at"].replace("Z", "+00:00"))
                        except ValueError:
                            # 兼容旧格式
                            config_data["created_at"] = datetime.fromisoformat(config_data["created_at"])
                    if "updated_at" in config_data and isinstance(config_data["updated_at"], str):
                        try:
                            config_data["updated_at"] = datetime.fromisoformat(config_data["updated_at"].replace("Z", "+00:00"))
                        except ValueError:
                            # 兼容旧格式
                            config_data["updated_at"] = datetime.fromisoformat(config_data["updated_at"])
                    configs.append(EvaluationConfig(**config_data))
            except Exception as e:
                print(f"加载配置失败 {config_file}: {e}")
                import traceback
                traceback.print_exc()
                continue
    
    # 按更新时间倒序排序
    configs.sort(key=lambda x: x.updated_at, reverse=True)
    
    return EvaluationConfigListResponse(configs=configs, total=len(configs))


@app.get("/api/evaluation/configs/{config_id}", response_model=EvaluationConfig)
async def get_evaluation_config(config_id: str):
    """获取指定评测配置"""
    config_file = CONFIG_STORAGE_DIR / f"{config_id}.json"
    
    if not config_file.exists():
        raise HTTPException(status_code=404, detail="Config not found")
    
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config_data = json.load(f)
            # 解析datetime字符串（支持ISO格式）
            if "created_at" in config_data and isinstance(config_data["created_at"], str):
                try:
                    config_data["created_at"] = datetime.fromisoformat(config_data["created_at"].replace("Z", "+00:00"))
                except ValueError:
                    config_data["created_at"] = datetime.fromisoformat(config_data["created_at"])
            if "updated_at" in config_data and isinstance(config_data["updated_at"], str):
                try:
                    config_data["updated_at"] = datetime.fromisoformat(config_data["updated_at"].replace("Z", "+00:00"))
                except ValueError:
                    config_data["updated_at"] = datetime.fromisoformat(config_data["updated_at"])
            return EvaluationConfig(**config_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load config: {str(e)}")


@app.put("/api/evaluation/configs/{config_id}", response_model=EvaluationConfig)
async def update_evaluation_config(
    config_id: str,
    name: Optional[str] = Query(None, description="配置名称"),
    config: Optional[EvaluationRequest] = None,
):
    """更新评测配置"""
    config_file = CONFIG_STORAGE_DIR / f"{config_id}.json"
    
    if not config_file.exists():
        raise HTTPException(status_code=404, detail="Config not found")
    
    # 加载现有配置
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            # 解析datetime字符串
            if "created_at" in existing_data and isinstance(existing_data["created_at"], str):
                try:
                    existing_data["created_at"] = datetime.fromisoformat(existing_data["created_at"].replace("Z", "+00:00"))
                except ValueError:
                    existing_data["created_at"] = datetime.fromisoformat(existing_data["created_at"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载配置失败: {str(e)}")
    
    # 更新字段
    if name:
        existing_data["name"] = name
    if config:
        existing_data.update({
            "dataset_path": config.dataset_path,
            "sample_config": config.sample_config,
            "api_key": config.api_key,
            "api_url": config.api_url,
            "api_model": config.api_model,
            "api_extra_headers": config.api_extra_headers,
            "api_extra_params": config.api_extra_params,
            "reward_calculator_class": config.reward_calculator_class,
            "tool_config": config.tool_config,
            "interaction_config": config.interaction_config,
            "max_assistant_turns": config.max_assistant_turns,
            "max_user_turns": config.max_user_turns,
            "max_concurrent": config.max_concurrent,
            "tokenizer_path": config.tokenizer_path,
            "verify_correction_kwargs": config.verify_correction_kwargs,
        })
    
    # 更新更新时间
    existing_data["updated_at"] = datetime.now().isoformat()
    
    # 保存到文件（持久化存储，使用原子写入）
    try:
        # 确保datetime使用ISO格式字符串
        if isinstance(existing_data.get("created_at"), datetime):
            existing_data["created_at"] = existing_data["created_at"].isoformat()
        if isinstance(existing_data.get("updated_at"), datetime):
            existing_data["updated_at"] = existing_data["updated_at"].isoformat()
        
        # 使用临时文件确保原子写入
        temp_file = config_file.with_suffix(".tmp")
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        # 原子性重命名
        temp_file.replace(config_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")
    
    # 解析datetime字符串用于返回
    if "created_at" in existing_data and isinstance(existing_data["created_at"], str):
        try:
            existing_data["created_at"] = datetime.fromisoformat(existing_data["created_at"].replace("Z", "+00:00"))
        except ValueError:
            existing_data["created_at"] = datetime.fromisoformat(existing_data["created_at"])
    if "updated_at" in existing_data and isinstance(existing_data["updated_at"], str):
        try:
            existing_data["updated_at"] = datetime.fromisoformat(existing_data["updated_at"].replace("Z", "+00:00"))
        except ValueError:
            existing_data["updated_at"] = datetime.fromisoformat(existing_data["updated_at"])
    
    return EvaluationConfig(**existing_data)


@app.delete("/api/evaluation/configs/{config_id}")
async def delete_evaluation_config(config_id: str):
    """删除评测配置"""
    config_file = CONFIG_STORAGE_DIR / f"{config_id}.json"
    
    if not config_file.exists():
        raise HTTPException(status_code=404, detail="Config not found")
    
    config_file.unlink()
    return {"message": "Config deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

