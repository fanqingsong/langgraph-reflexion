"""Reflexion Agent with LangGraph - 自我反思 Agent 实现。

本包提供了一个使用 LangGraph 和 LangChain 实现的 Reflexion Agent，
通过自我反思和迭代改进来生成高质量的回答。

主要导出：
- create_reflexion_graph: 创建 Reflexion Agent 的工作流图
- setup_azure_openai: 配置 Azure OpenAI
- first_responder: 初始响应生成链（向后兼容）
- revisor: 答案修订链（向后兼容）
- get_llm: 获取 LLM 实例
"""

from langchain_core.output_parsers import PydanticToolsParser

from reflexion_agent.graph import create_reflexion_graph
from reflexion_agent.infra import (
    AnswerQuestion,
    REVISE_INSTRUCTIONS,
    ReviseAnswer,
    create_actor_prompt_template,
    get_llm,
    get_llm_instance,
    setup_azure_openai,
)

# 向后兼容：创建 first_responder 和 revisor
# 这些链的实现逻辑已经在 nodes 模块中，这里为了向后兼容重新导出

def _create_first_responder():
    """创建初始响应生成链（向后兼容）。"""
    llm = get_llm_instance()
    actor_prompt_template = create_actor_prompt_template()
    first_responder = actor_prompt_template.partial(
        first_instruction="Provide a detailed ~250 word answer."
    ) | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
    return first_responder

_first_responder_instance = None
def _get_first_responder():
    global _first_responder_instance
    if _first_responder_instance is None:
        _first_responder_instance = _create_first_responder()
    return _first_responder_instance

class _FirstResponder:
    """可调用的 first_responder 对象（向后兼容）。"""
    def invoke(self, *args, **kwargs):
        return _get_first_responder().invoke(*args, **kwargs)

first_responder = _FirstResponder()

# Pydantic 工具解析器（向后兼容）
validator = PydanticToolsParser(tools=[AnswerQuestion])

def _create_revisor():
    """创建答案修订链（向后兼容）。"""
    llm = get_llm_instance()
    actor_prompt_template = create_actor_prompt_template()
    revisor = actor_prompt_template.partial(
        first_instruction=REVISE_INSTRUCTIONS
    ) | llm.bind_tools(tools=[ReviseAnswer], tool_choice="ReviseAnswer")
    return revisor

_revisor_instance = None
def _get_revisor():
    global _revisor_instance
    if _revisor_instance is None:
        _revisor_instance = _create_revisor()
    return _revisor_instance

class _Revisor:
    """可调用的 revisor 对象（向后兼容）。"""
    def invoke(self, *args, **kwargs):
        return _get_revisor().invoke(*args, **kwargs)

revisor = _Revisor()

__all__ = [
    "create_reflexion_graph",
    "setup_azure_openai",
    "first_responder",
    "revisor",
    "get_llm",
    "get_llm_instance",
    "validator",
]
