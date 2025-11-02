"""Reflexion Agent 的 Pydantic 数据模型定义。

本模块定义了用于 Reflexion Agent 的 Pydantic 模型（Schema），这些模型用于结构化 LLM 的输出，
确保生成的数据符合预期格式。
"""

from typing import List

from pydantic import BaseModel, Field


class Reflection(BaseModel):
    """对答案质量的反思模型。
    
    用于评估生成的答案，识别缺失的信息和多余的内容。
    """

    # 缺失内容的批评意见
    missing: str = Field(description="Critique of what is missing.")
    # 多余内容的批评意见
    superfluous: str = Field(description="Critique of what is superfluous")


class AnswerQuestion(BaseModel):
    """回答问题的基础模型。
    
    用于初始答案生成，包含答案、自我反思和改进建议的搜索查询。
    """

    # 约250字的详细答案
    answer: str = Field(description="~250 word detailed answer to the question.")
    # 对初始答案的反思
    reflection: Reflection = Field(description="Your reflection on the initial answer.")
    # 用于研究改进的搜索查询列表（1-3个查询）
    search_queries: List[str] = Field(
        description="1-3 search queries for researching improvements to address the critique of your current answer."
    )


class ReviseAnswer(AnswerQuestion):
    """修订答案的模型。
    
    继承自 AnswerQuestion，增加了引用列表，确保修订后的答案有依据。
    强制引用可以确保回答更加可靠和可验证。
    """

    # 引用列表，用于支持修订后的答案
    references: List[str] = Field(
        description="Citations motivating your updated answer."
    )

