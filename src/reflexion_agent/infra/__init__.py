"""Infrastructure 模块 - 统一导出基础设施组件。

本模块提供 Reflexion Agent 所需的基础设施组件，包括：
- config: Azure OpenAI 配置
- llm: LLM 初始化和管理
- prompts: 提示模板
- schema: Pydantic 数据模型
"""

from reflexion_agent.infra.config import (
    get_deployment_name,
    is_azure_openai_configured,
    setup_azure_openai,
)
from reflexion_agent.infra.llm import get_llm, get_llm_instance
from reflexion_agent.infra.prompts import REVISE_INSTRUCTIONS, create_actor_prompt_template
from reflexion_agent.infra.schema import AnswerQuestion, Reflection, ReviseAnswer

__all__ = [
    # config
    "setup_azure_openai",
    "get_deployment_name",
    "is_azure_openai_configured",
    # llm
    "get_llm",
    "get_llm_instance",
    # prompts
    "create_actor_prompt_template",
    "REVISE_INSTRUCTIONS",
    # schema
    "Reflection",
    "AnswerQuestion",
    "ReviseAnswer",
]

