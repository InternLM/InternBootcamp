"""
模型评测服务
"""
import asyncio
import json
from pathlib import Path
from typing import Optional, Dict, Any
from internbootcamp.src.base_evaluator import BaseEvaluator, load_dataset
from internbootcamp.utils.load_class_from_str import load_class_from_string


class EvaluationService:
    """模型评测服务"""
    
    @staticmethod
    def parse_extra_params(params_str: Optional[str]) -> Dict[str, Any]:
        """解析额外参数（支持JSON格式）"""
        if not params_str:
            return {}
        
        try:
            # 尝试解析JSON
            return json.loads(params_str)
        except json.JSONDecodeError:
            # 回退到旧格式解析 key:value,key2:value2
            params = {}
            for pair in params_str.split(','):
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    # 尝试转换数值类型
                    try:
                        if '.' in value:
                            params[key.strip()] = float(value.strip())
                        else:
                            params[key.strip()] = int(value.strip())
                    except ValueError:
                        params[key.strip()] = value.strip()
            return params
    
    @staticmethod
    def parse_extra_headers(headers_str: Optional[str]) -> Dict[str, str]:
        """解析额外请求头"""
        if not headers_str:
            return {}
        
        headers = {}
        for pair in headers_str.split(','):
            if ':' in pair:
                key, value = pair.split(':', 1)
                headers[key.strip()] = value.strip()
        return headers
    
    @staticmethod
    async def run_evaluation(
        output_dir: str,
        api_key: str,
        api_url: Optional[str],
        api_model: str,
        reward_calculator_class: str,
        dataset_path: Optional[str] = None,
        sample_config: Optional[Dict[str, Any]] = None,
        api_extra_headers: Optional[str] = None,
        api_extra_params: Optional[str] = None,
        verify_correction_kwargs: Optional[str] = None,
        tool_config: Optional[str] = None,
        interaction_config: Optional[str] = None,
        max_assistant_turns: Optional[int] = 5,
        max_user_turns: Optional[int] = 20,
        max_concurrent: int = 1,
        tokenizer_path: Optional[str] = None,
        task_id: Optional[str] = None,
        progress_callback = None,
    ) -> str:
        """
        执行评测任务
        
        Args:
            output_dir: 输出目录
            api_key: API密钥
            api_url: API地址
            api_model: 模型名称
            reward_calculator_class: 奖励计算器类路径
            dataset_path: 数据集路径（与sample_config二选一）
            sample_config: 单个样本配置（与dataset_path二选一）
            api_extra_headers: 额外请求头
            api_extra_params: 额外模型参数
            verify_correction_kwargs: 验证参数
            tool_config: 工具配置
            interaction_config: 交互配置
            max_assistant_turns: 最大assistant轮次
            max_user_turns: 最大user轮次
            max_concurrent: 最大并发数
            tokenizer_path: tokenizer路径
            task_id: 任务ID
            progress_callback: 进度回调函数
            
        Returns:
            str: 结果文件路径
        """
        # 验证参数
        if not dataset_path and not sample_config:
            raise ValueError("必须提供 dataset_path 或 sample_config 之一")
        if dataset_path and sample_config:
            raise ValueError("不能同时提供 dataset_path 和 sample_config")
        
        # 解析参数
        extra_headers = EvaluationService.parse_extra_headers(api_extra_headers)
        extra_params = EvaluationService.parse_extra_params(api_extra_params)
        verify_kwargs = EvaluationService.parse_extra_params(verify_correction_kwargs)
        
        # 加载奖励计算器
        reward_calculator = load_class_from_string(reward_calculator_class)
        
        # 创建评测器
        evaluator = BaseEvaluator(
            api_key=api_key,
            api_url=api_url,
            api_model=api_model,
            api_extra_headers=extra_headers,
            api_extra_params=extra_params,
            reward_calculator=reward_calculator,
            verify_correction_kwargs=verify_kwargs,
            max_assistant_turns=max_assistant_turns,
            max_user_turns=max_user_turns,
            tokenizer_path=tokenizer_path,
        )
        
        # 加载数据集
        if dataset_path:
            dataset = load_dataset(dataset_path)
        else:
            # 使用单个sample配置
            dataset = [sample_config]
        
        # 如果有进度回调，需要包装evaluate_batch方法
        if progress_callback:
            original_evaluate_batch = evaluator._evaluate_batch
            
            async def wrapped_evaluate_batch(*args, **kwargs):
                # 在这里我们可以监控进度
                # 但由于BaseEvaluator不直接提供进度回调，我们需要定期更新
                # 通过轮询结果文件来获取进度
                return await original_evaluate_batch(*args, **kwargs)
            
            evaluator._evaluate_batch = wrapped_evaluate_batch
        
        # 执行评测
        results = await evaluator.run_evaluation(
            dataset=dataset,
            output_dir=output_dir,
            yaml_tool_path=tool_config,
            yaml_interaction_path=interaction_config,
            max_concurrent=max_concurrent,
        )
        
        # 返回结果文件路径（从evaluator获取）
        # BaseEvaluator会在output_dir/{model}/eval_results_{timestamp}.jsonl生成结果
        import os
        from internbootcamp.utils.format_time_now import format_time_now
        
        # 查找最新生成的结果文件
        model_dir = Path(output_dir) / api_model.replace('/', '-').strip('-')
        if model_dir.exists():
            result_files = sorted(model_dir.glob("eval_results_*.jsonl"), key=os.path.getmtime, reverse=True)
            if result_files:
                return str(result_files[0])
        
        return ""

