# Copyright 2025 Bytedance Ltd. and/or its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import torch

from verl import DataProto
from verl.workers.reward_manager import register

import inspect
import warnings

@register("bootcamp")
class BootcampRewardManager:

    def __init__(self, tokenizer, num_examine, compute_score=None, reward_fn_key="data_source", **reward_kwargs) -> None:
        self.tokenizer = tokenizer
        self.num_examine = num_examine
        self.compute_score = compute_score
        self.reward_fn_key = reward_fn_key
        self.reward_kwargs = reward_kwargs or {}

        self._bootcamp_calc_cache: dict[str, callable] = {}

        # parallelism for per-item scoring
        self._num_workers: int = int(self.reward_kwargs.get("parallel_workers", 128))

    def _preload_bootcamp_calculators(self, data_sources: list[str]):
        unique_bootcamps: set[str] = set()
        for ds in data_sources:
            if isinstance(ds, str) and ds.startswith("bootcamp/"):
                bootcamp_name = ds.split("bootcamp/")[1]
                unique_bootcamps.add(bootcamp_name)
        if not unique_bootcamps:
            return
        try:
            import importlib
            module = importlib.import_module("internbootcamp")
        except Exception as e:
            # If import fails, skip caching; default_compute_score will handle errors later
            warnings.warn(f"Failed to import internbootcamp module: {e}")
            return

        for bootcamp_name in unique_bootcamps:
            if bootcamp_name in self._bootcamp_calc_cache:
                continue
            cls_name = bootcamp_name[0].upper() + bootcamp_name[1:] + "RewardCalculator"
            try:
                calc_cls = getattr(module, cls_name)
            except AttributeError:
                warnings.warn(f"Failed to find {cls_name} in internbootcamp module, please check if the bootcamp name in data_source is correct")
                continue

            def _make_runner(calc):
                def _runner(solution_str, ground_truth, extra_info=None):  
                    # 检查verify_score方法是否支持kwargs或extra_info参数
                    verify_score_sig = inspect.signature(calc.verify_score)
                    params = verify_score_sig.parameters
                    if_supports_kwargs = any(param.kind == param.VAR_KEYWORD for param in params.values())
                    if_supports_extra_info = 'extra_info' in params
                    # assert if_supports_kwargs or if_supports_extra_info, \
                        # f"verify_score方法必须支持**kwargs参数或extra_info参数，但在{calc.__name__}中都不支持"
                    
                    # call_kwargs = {
                    #     "format_score": self.reward_kwargs.get("format_score", 0),
                    #     "short_penalty": self.reward_kwargs.get("short_penalty", False),
                    #     "short_threshold": self.reward_kwargs.get("short_threshold", 512),
                    #     "think_threshold": self.reward_kwargs.get("think_threshold", 0),
                    #     "ans_threshold": self.reward_kwargs.get("ans_threshold", 256),
                    #     "format_penalty": self.reward_kwargs.get("format_penalty", False),
                    # }
                    
                    # if if_supports_extra_info:
                    #     call_kwargs["extra_info"] = extra_info
                    
                    return calc.verify_score(
                        solution_str,
                        ground_truth,
                        **self.reward_kwargs
                    )
                return _runner

            self._bootcamp_calc_cache[bootcamp_name] = _make_runner(calc_cls)

    def _compute_score_internal(self, data_source: str, solution_str: str, ground_truth, extra_info):
        # 优先路由到bootcamp计算
        if isinstance(data_source, str) and data_source.startswith("bootcamp/"):
            bootcamp_name = data_source.split("bootcamp/")[1]
            runner = self._bootcamp_calc_cache.get(bootcamp_name)
            if runner is not None:
                return runner(solution_str, ground_truth, extra_info)

        if self.compute_score is not None:
            return self.compute_score(
                data_source=data_source,
                solution_str=solution_str,
                ground_truth=ground_truth,
                extra_info=extra_info,
            )
        else:
            warnings.warn(f"No compute_score function provided, please check if the reward_model.compute_score is correct")
            raise Exception("No compute_score function provided")

    def __call__(self, data: DataProto, return_dict: bool = False):
        if "rm_scores" in data.batch.keys():
            if return_dict:
                return {"reward_tensor": data.batch["rm_scores"]}
            else:
                return data.batch["rm_scores"]

        # preload bootcamp calculators for this batch
        try:
            data_sources = data.non_tensor_batch[self.reward_fn_key]
            unique_sources = [str(x) for x in list(data_sources)]
            self._preload_bootcamp_calculators(unique_sources)
        except Exception:
            pass

        reward_tensor = torch.zeros_like(data.batch["responses"], dtype=torch.float32)
        reward_extra_info = defaultdict(list)

        def process_item(i: int):
            data_item = data[i]

            prompt_ids = data_item.batch["prompts"]
            prompt_length = prompt_ids.shape[-1]
            valid_prompt_length = data_item.batch["attention_mask"][:prompt_length].sum()
            valid_prompt_ids = prompt_ids[-valid_prompt_length:]

            response_ids = data_item.batch["responses"]
            valid_response_length = data_item.batch["attention_mask"][prompt_length:].sum()
            valid_response_ids = response_ids[:valid_response_length]

            prompt_str = self.tokenizer.decode(valid_prompt_ids, skip_special_tokens=True)
            response_str = self.tokenizer.decode(valid_response_ids, skip_special_tokens=True)

            ground_truth = data_item.non_tensor_batch["reward_model"].get("ground_truth", None)
            data_source = data_item.non_tensor_batch[self.reward_fn_key]

            extra_info = {}
            messages = data_item.non_tensor_batch.get("messages", {}) or {}
            meta_info = data_item.non_tensor_batch.get("meta_info", {}) or {}
            extra_info["messages"] = messages
            extra_info["meta_info"] = meta_info

            result = self._compute_score_internal(
                data_source=data_source,
                solution_str=response_str,
                ground_truth=ground_truth,
                extra_info=extra_info,
            )

            if isinstance(result, dict):
                reward = float(result.get("score", 0.0))
                item_extra = result
            else:
                reward = float(result)
                item_extra = {"score": reward}

            return {
                "idx": i,
                "reward": reward,
                "valid_response_length": int(valid_response_length),
                "data_source": data_source,
                "prompt_str": prompt_str,
                "response_str": response_str,
                "ground_truth": ground_truth,
                "extra": item_extra,
            }

        indices = list(range(len(data)))
        if self._num_workers > 1 and len(indices) > 1:
            with ThreadPoolExecutor(max_workers=self._num_workers) as ex:
                results = list(ex.map(process_item, indices))
        else:
            results = [process_item(i) for i in indices]

        already_print_data_sources: dict[str, int] = {}
        for res in results:
            i = res["idx"]
            reward_tensor[i, res["valid_response_length"] - 1] = res["reward"]
            for k, v in res["extra"].items():
                reward_extra_info[k].append(v)

        for res in results:
            data_source = res["data_source"]
            already_print_data_sources.setdefault(data_source, 0)
            if already_print_data_sources[data_source] < self.num_examine:
                already_print_data_sources[data_source] += 1
                print("[prompt]", res["prompt_str"])
                print("[response]", res["response_str"])
                print("[ground_truth]", res["ground_truth"])
                for k, v in res["extra"].items():
                    print(f"[{k}]", v)

        if return_dict:
            return {"reward_tensor": reward_tensor, "reward_extra_info": reward_extra_info}
        else:
            return reward_tensor 