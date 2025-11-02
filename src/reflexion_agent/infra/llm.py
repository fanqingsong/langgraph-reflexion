"""LLM 初始化模块。

本模块负责初始化和管理 LLM 实例，支持：
- Azure OpenAI
- 标准 OpenAI

根据环境变量自动选择合适的 LLM 配置。
"""

import os

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from langchain.chat_models import init_chat_model

from reflexion_agent.infra.config import (
    get_deployment_name,
    is_azure_openai_configured,
    setup_azure_openai,
)


def get_llm():
    """获取配置好的 LLM 实例。
    
    根据环境变量配置选择合适的 LLM：
    - 如果配置了 Azure OpenAI，使用 Azure OpenAI
    - 否则使用标准 OpenAI
    
    Returns:
        ChatModel: 配置好的 LLM 实例（通过 init_chat_model 创建）
    """
    # 根据环境变量配置选择合适的 LLM
    # 如果配置了 Azure OpenAI，使用 Azure OpenAI；否则使用标准 OpenAI
    if is_azure_openai_configured():
        # 初始化 Azure OpenAI 配置（设置环境变量）
        setup_azure_openai(load_env=True)
        # 获取部署名称（默认为 "gpt-4"）
        deployment_name = get_deployment_name()
        
        # 使用 init_chat_model 创建 Azure OpenAI 实例
        # 这种方式会自动从环境变量读取配置，无需手动构建 base_url
        # 环境变量包括：
        # - AZURE_OPENAI_API_KEY
        # - AZURE_OPENAI_ENDPOINT
        # - OPENAI_API_VERSION
        llm = init_chat_model(
            model=deployment_name,  # Azure 部署名称
            model_provider="azure_openai"  # 指定使用 Azure OpenAI 提供者
        )
    else:
        # 使用标准 OpenAI（需要 OPENAI_API_KEY 环境变量）
        llm = init_chat_model(model="gpt-4")
    
    return llm


# 全局 LLM 实例（延迟初始化）
_llm_instance = None


def get_llm_instance():
    """获取全局 LLM 实例（单例模式）。
    
    首次调用时初始化 LLM，后续调用返回同一个实例。
    这样可以避免重复初始化，提高性能。
    
    Returns:
        ChatModel: 全局 LLM 实例（通过 init_chat_model 创建）
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_llm()
    return _llm_instance

