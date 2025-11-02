"""Reflexion Agent 的基础使用示例。

本示例演示如何使用 Reflexion Agent 来回答问题，
通过自我反思和迭代改进生成高质量的回答。
"""

from dotenv import load_dotenv

# 加载环境变量（包括 Azure OpenAI 和 Tavily API 配置）
load_dotenv()

from langchain_core.messages import HumanMessage

from reflexion_agent.graph import create_reflexion_graph

# 为 langgraph.json 创建图实例
# 这是 LangGraph 开发服务器需要的全局变量
graph = create_reflexion_graph()

if __name__ == "__main__":
    # 示例查询：关于 AI-Powered SOC 和自主 SOC 的问题
    query = "Write about AI-Powered SOC / autonomous soc problem domain, list startups that do that and raised capital."

    print("Running reflexion agent...")
    print(f"Query: {query}\n")

    # 调用图处理查询
    # StateGraph 需要传入状态字典，包含 messages 键
    # 图会自动执行：生成初始答案 -> 搜索相关信息 -> 修订答案 -> 循环改进
    result = graph.invoke({"messages": [HumanMessage(content=query)]})

    # 提取并格式化打印答案
    # StateGraph 返回状态字典，包含 messages 键
    messages = result.get("messages", [])
    if messages and len(messages) > 0:
        # 获取最后一条消息（应该包含最终答案）
        last_message = messages[-1]
        
        # 检查是否包含工具调用（工具调用中包含了结构化答案）
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            # 从工具调用参数中提取答案
            answer = last_message.tool_calls[0]["args"]["answer"]
            
            # 格式化打印最终答案
            print("=" * 80)
            print("FINAL ANSWER:")
            print("=" * 80)
            print(answer)
            print("=" * 80)

            # 如果有引用，也打印出来
            if "references" in last_message.tool_calls[0]["args"]:
                refs = last_message.tool_calls[0]["args"]["references"]
                if refs:
                    print("\nReferences:")
                    # 为每个引用添加编号
                    for i, ref in enumerate(refs, 1):
                        print(f"  [{i}] {ref}")
