"""提示模板模块。

本模块定义了用于 Reflexion Agent 的提示模板，
包括通用的演员提示模板和修订指令。
"""

import datetime

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder


def create_actor_prompt_template() -> ChatPromptTemplate:
    """创建通用的演员提示模板。
    
    这个模板用于指导 LLM 作为专家研究员工作，包括：
    - 系统提示（专家研究员角色）
    - 消息历史占位符
    - 格式要求
    
    Returns:
        ChatPromptTemplate: 配置好的提示模板
    """
    template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are expert researcher.
Current time: {time}

1. {first_instruction}
2. Reflect and critique your answer. Be severe to maximize improvement.
3. Recommend search queries to research information and improve your answer.""",
            ),
            # 消息历史占位符，用于插入对话历史
            MessagesPlaceholder(variable_name="messages"),
            # 格式要求提示
            ("system", "Answer the user's question above using the required format."),
        ]
    ).partial(
        # 动态注入当前时间
        time=lambda: datetime.datetime.now().isoformat(),
    )
    
    return template


# 修订指令：指导 LLM 如何基于新信息和批评修订答案
REVISE_INSTRUCTIONS = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
        - You MUST include numerical citations in your revised answer to ensure it can be verified.
        - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In form of:
            - [1] https://example.com
            - [2] https://example.com
    - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words.
"""

