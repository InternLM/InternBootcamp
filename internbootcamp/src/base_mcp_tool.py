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

import asyncio
import json
import logging
import os
from typing import Any, Optional
from uuid import uuid4

import aiohttp
import httpx
import requests
from fastmcp.exceptions import ClientError
from tenacity import retry, stop_after_attempt, wait_exponential
from verl.tools.schemas import OpenAIFunctionToolSchema, ToolResponse
from verl.tools.utils.mcp_clients.McpClientManager import ClientManager
from verl.utils.rollout_trace import rollout_trace_op

from .base_tool import BaseTool

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BaseMCPTool(BaseTool):
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        self._instance_dict = {}
        self.timeout = config.get("timeout_per_query")
        self.mcp_server_url = config.get("mcp_server_url")

        logger.info(f"Initialized BaseMCPTool with config: {config}")

    def _load_config(self, file: str) -> dict[str, Any]:
        try:
            with open(file) as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f'the "{file}" file was not found')
        except Exception:
            logger.error(f'there was an error reading the "{file}" file')

        return {}

    def get_openai_tool_schema(self) -> OpenAIFunctionToolSchema:
        """Return the OpenAI tool schema."""
        return self.tool_schema

    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> tuple[str, ToolResponse]:
        """Create a tool instance.

        Args:
            instance_id: The instance id of the tool.
            identity: Identity information to pass to the API.

        Returns:
            The instance id of the tool.
        """
        # identity类型限制
        if not isinstance(identity, dict):
            try:
                identity = json.loads(identity)
            except:
                print(f"[DEBUG BaseMCPTool] Error in create: identity is not a dict. identity: {identity}")
                return None
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] =identity
        
        # Call API to create instance on remote server
        try:
            # IMPORTANT:
            # - 这里必须使用超时；否则网络不通/服务挂掉时会长时间挂起，放大评测失败率
            # - aiohttp.ClientSession(timeout=None) 会忽略超时配置
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.mcp_server_url + "/create",
                    json={"instance_id": instance_id, "identity": identity},
                ) as response:
                    if response.status != 200:
                        text = await response.text()
                        raise ValueError(f"Bad status: {response.status}, response: {text}")
        except Exception as e:
            print(f"Failed to call API create: {e}")
            import traceback
            traceback.print_exc()
            raise e
        
        return instance_id, ToolResponse()

    @retry(stop=stop_after_attempt(16), 
           wait=wait_exponential(multiplier=1, max=60), 
           reraise=True,
           before_sleep=lambda retry_state: print(f"Tool call retrying, failed attempt {retry_state.attempt_number}: \n{retry_state.outcome.exception()}"))
    async def _call_tool(self, instance_id, parameters) -> tuple[str, dict]:
        err_msg = ""
        params_with_instance = dict(parameters) if parameters is not None else {}
        params_with_instance["instance_id"] = instance_id
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(self.mcp_server_url + "/execute", json=params_with_instance) as response:
                    # 确保响应是 JSON
                    if response.status != 200:
                        text = await response.text()
                        raise ValueError(f"Bad status: {response.status}, response: {text}")
                    result = await response.json()
                    if len(result) != 3:
                        raise ValueError(f"failed to call tool: {result}")
                    return result
        except asyncio.TimeoutError as e:
            err_msg = f"Request time out: {e}"
        except aiohttp.ContentTypeError as e:
            err_msg = f"Invalid content-type: {e}"
        except json.JSONDecodeError as e:
            err_msg = f"JSON decode failed: {e}"
        except ClientError as e:
            err_msg = f"Tool call failed: {e}"
        except aiohttp.ClientError as e:
            err_msg = f"Connection failed: {e}"
        except ValueError as e:  # JSON 解析错误或其他验证错误
            err_msg = f"Invalid response: {e}"
        except Exception as e:
            import traceback
            
            err_msg = f"An unexpected error occurred:\n{traceback.format_exc()}\n{str(e)}"

        # If we reach here, there was an error
        return str(err_msg), 0.0, {}

        # text = call_tool_result.text
        # print(f"call_tool_result:{text}")
        # assert False
        # logger.debug(f"Tool result for instance {instance_id} with tool {self.name}: {call_tool_result.content}")
        # result, metadata = self._parse_tool_result(call_tool_result.content)
        # metadata["api_request_error"] += err_msg
        # return result, metadata

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> tuple[str, float, dict]:
        if self.name == "" or self.name is None or parameters is None:
            error_msg = "Error: 'parameters' is missing or empty."
            logger.error(f"[MCPTool] {error_msg} Received tool name: {self.name}, parameters: {parameters}")
            return json.dumps({"result": error_msg}), 0.0, {}

        try:
            return await self._call_tool(instance_id, parameters)
        except Exception as e:
            error_result = json.dumps({"result": f"Tool execution failed: {e}"})
            logger.error(f"[BaseMCPTool] Execution failed: {e}")
            return error_result, 0.0, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> str:
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.mcp_server_url + "/calc_reward", 
                    json={"instance_id": instance_id}
                ) as response:
                    text = await response.text()
                    return float(text)
        except Exception as e:
            return 0.0

    async def release(self, instance_id: str, **kwargs) -> None:
        if instance_id in self._instance_dict:
            del self._instance_dict[instance_id]
        try:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.mcp_server_url + "/release", 
                    json={"instance_id": instance_id}
                ) as response:
                    pass  # Response handled
        except Exception as e:
            print(f"Failed to call API release: {e}")
        return True

    def _parse_tool_result(self, content: list) -> tuple[str, dict]:
        tools_content = [part.text for part in filter(lambda x: x.type == "text", content)]
        return " ".join(tools_content), {}
