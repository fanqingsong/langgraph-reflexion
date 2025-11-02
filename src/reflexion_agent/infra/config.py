"""Azure OpenAI 配置模块。

本模块提供 Azure OpenAI 的配置和管理功能，包括：
- 环境变量加载
- Azure OpenAI 设置
- 配置检查
- 部署名称获取
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def load_env_file(env_path: Optional[str] = None) -> None:
    """从 .env 文件加载环境变量。
    
    如果未指定路径，自动在项目根目录查找 .env 文件。
    
    Args:
        env_path: .env 文件的路径。如果为 None，则在项目根目录查找。
    """
    if env_path is None:
        # 在项目根目录查找 .env 文件
        # __file__ 是当前文件路径，parent.parent.parent.parent 是项目根目录
        # infra/ -> reflexion_agent/ -> src/ -> 项目根目录
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / ".env"
    else:
        env_path = Path(env_path)
    
    # 如果 .env 文件存在，加载它
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)


def setup_azure_openai(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    api_version: Optional[str] = None,
    load_env: bool = True,
) -> None:
    """设置 Azure OpenAI 环境变量。
    
    LangChain 的 ChatOpenAI 支持 Azure OpenAI，需要设置以下环境变量：
    - AZURE_OPENAI_API_KEY: API 密钥
    - AZURE_OPENAI_ENDPOINT: 端点 URL
    - AZURE_OPENAI_API_VERSION: API 版本（可选，默认为 "2024-02-15-preview"）
    
    Args:
        api_key: Azure OpenAI API 密钥。如果未提供，从环境变量 AZURE_OPENAI_API_KEY 读取。
        endpoint: Azure OpenAI 端点 URL。如果未提供，从环境变量 AZURE_OPENAI_ENDPOINT 读取。
        api_version: Azure OpenAI API 版本。如果未提供，默认为 "2024-02-15-preview"。
        load_env: 是否首先加载 .env 文件。默认为 True。
        
    Raises:
        ValueError: 如果缺少必需的 API 密钥或端点配置。
    """
    # 如果需要，先加载 .env 文件
    if load_env:
        load_env_file()
    
    # 设置 API 密钥
    if api_key:
        # 如果提供了 api_key 参数，直接设置
        os.environ["AZURE_OPENAI_API_KEY"] = api_key
    elif "AZURE_OPENAI_API_KEY" not in os.environ:
        # 如果既没有提供参数，环境变量中也没有，抛出错误
        raise ValueError(
            "Azure OpenAI API key not found. Please set AZURE_OPENAI_API_KEY environment variable or pass api_key parameter."
        )
    
    # 设置端点
    if endpoint:
        os.environ["AZURE_OPENAI_ENDPOINT"] = endpoint
    elif "AZURE_OPENAI_ENDPOINT" not in os.environ:
        raise ValueError(
            "Azure OpenAI endpoint not found. Please set AZURE_OPENAI_ENDPOINT environment variable or pass endpoint parameter."
        )
    
    # 设置 API 版本（带默认值）
    # LangChain 期望 OPENAI_API_VERSION 用于 Azure OpenAI
    if api_version:
        # 如果提供了版本，同时设置两个环境变量
        os.environ["AZURE_OPENAI_API_VERSION"] = api_version
        os.environ["OPENAI_API_VERSION"] = api_version
    elif "AZURE_OPENAI_API_VERSION" in os.environ:
        # 如果 AZURE_OPENAI_API_VERSION 已设置，也设置 OPENAI_API_VERSION
        os.environ["OPENAI_API_VERSION"] = os.environ["AZURE_OPENAI_API_VERSION"]
    elif "OPENAI_API_VERSION" not in os.environ:
        # 如果都没有设置，使用默认版本
        default_version = "2024-02-15-preview"
        os.environ["AZURE_OPENAI_API_VERSION"] = default_version
        os.environ["OPENAI_API_VERSION"] = default_version


def is_azure_openai_configured() -> bool:
    """检查是否已配置 Azure OpenAI。
    
    检查必需的环境变量（API 密钥和端点）是否已设置。
    
    Returns:
        bool: 如果 Azure OpenAI 环境变量已设置返回 True，否则返回 False。
    """
    # 先尝试加载 .env 文件
    load_env_file()
    # 检查必需的环境变量是否存在
    return (
        "AZURE_OPENAI_API_KEY" in os.environ
        and "AZURE_OPENAI_ENDPOINT" in os.environ
    )


def get_deployment_name() -> str:
    """从环境变量获取 Azure OpenAI 部署名称。
    
    Returns:
        str: 部署名称，如果未设置则默认为 "gpt-4"。
    """
    # 加载环境变量
    load_env_file()
    # 从环境变量获取部署名称，如果没有则使用默认值 "gpt-4"
    return os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

