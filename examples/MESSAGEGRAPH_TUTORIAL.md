# MessageGraph 详细教程

## 什么是 MessageGraph？

MessageGraph 是 LangGraph 框架提供的一种专门用于处理基于消息的工作流的图结构。它非常适合构建聊天机器人、对话系统等需要管理消息历史的应用程序。

## 核心概念

### 1. 节点（Node）
节点是图的基本执行单元，每个节点对应一个函数。节点函数：
- **输入**：接收当前状态（消息列表）
- **输出**：返回一个字典，包含要添加到状态中的新消息

### 2. 边（Edge）
边定义了节点之间的连接关系：
- **普通边**：无条件连接，总是执行
- **条件边**：根据状态动态决定执行路径

### 3. 状态（State）
在 MessageGraph 中，状态就是消息列表 `List[Message]`。每条消息可以是：
- `HumanMessage`: 用户消息
- `AIMessage`: AI 回复消息
- `SystemMessage`: 系统消息
- `ToolMessage`: 工具调用结果消息

## 执行过程详解

### 示例：简单线性工作流

```python
START -> greet -> respond -> farewell -> END
```

#### 步骤 1: 初始化状态
```python
# 用户调用图，传入初始消息
initial_state = [HumanMessage(content="你好")]
```

#### 步骤 2: 从 START 开始
```
状态: [HumanMessage("你好")]
当前位置: START
根据边: START -> greet
下一个节点: "greet"
```

#### 步骤 3: 执行 greet 节点
```python
def greet_node(state):
    # state = [HumanMessage("你好")]
    # 添加一条 AI 消息
    return {"messages": [AIMessage(content="你好！我是 AI 助手。")]}

# 执行后，状态更新为:
# state = [
#     HumanMessage("你好"),
#     AIMessage("你好！我是 AI 助手。")  # 新添加的消息
# ]
```

#### 步骤 4: 根据边移动到下一个节点
```
当前位置: "greet"
根据边: greet -> respond
下一个节点: "respond"
```

#### 步骤 5: 执行 respond 节点
```python
def respond_node(state):
    # state = [
    #     HumanMessage("你好"),
    #     AIMessage("你好！我是 AI 助手。")
    # ]
    # 使用 LLM 生成回复
    response = llm.invoke(state)
    return {"messages": [response]}

# 执行后，状态更新为:
# state = [
#     HumanMessage("你好"),
#     AIMessage("你好！我是 AI 助手。"),
#     AIMessage("很高兴认识你！")  # 新添加的回复
# ]
```

#### 步骤 6: 继续执行直到 END
```
respond -> farewell -> END
最终状态: [
    HumanMessage("你好"),
    AIMessage("你好！我是 AI 助手。"),
    AIMessage("很高兴认识你！"),
    AIMessage("再见！很高兴为您服务。")
]
```

### 执行流程图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. graph.invoke([HumanMessage("你好")])                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 从 START 开始                                            │
│    状态: [HumanMessage("你好")]                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 执行 greet 节点                                          │
│    输入: [HumanMessage("你好")]                             │
│    输出: {"messages": [AIMessage("你好！我是 AI 助手。")]}  │
│    状态更新: [HumanMessage("你好"), AIMessage("你好！...")]│
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 执行 respond 节点                                        │
│    输入: [HumanMessage("你好"), AIMessage("你好！...")]     │
│    输出: {"messages": [AIMessage("很高兴认识你！")]}      │
│    状态更新: [... , AIMessage("很高兴认识你！")]           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. 执行 farewell 节点                                       │
│    输出: {"messages": [AIMessage("再见！...")]}             │
│    状态更新: [... , AIMessage("再见！...")]                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. 到达 END，返回最终状态                                   │
│    最终状态包含所有消息                                      │
└─────────────────────────────────────────────────────────────┘
```

## 条件边的使用

条件边允许根据状态动态决定执行路径：

```python
def route_condition(state):
    """根据消息内容决定路径"""
    last_message = state[-1]
    if "happy" in last_message.content.lower():
        return "happy_path"  # 转到积极路径
    else:
        return "sad_path"    # 转到消极路径

# 添加条件边
builder.add_conditional_edges("check_message", route_condition)
```

### 条件边执行流程

```
执行 check_message 节点
    ↓
状态: [HumanMessage("I'm happy today!")]
    ↓
执行 route_condition(state)
    ↓
检查: "happy" in "I'm happy today!".lower()
    ↓
返回: "happy_path"
    ↓
下一个节点: "happy_path"
```

## 节点函数编写规范

### 1. 函数签名
```python
def node_function(state: List[Message]) -> dict:
    """
    Args:
        state: 当前状态（消息列表）
    
    Returns:
        dict: 包含 "messages" 键的字典
    """
    pass
```

### 2. 返回值格式
```python
# ✅ 正确：返回包含 messages 的字典
return {"messages": [AIMessage(content="回复内容")]}

# ❌ 错误：直接返回消息列表
return [AIMessage(content="回复内容")]

# ❌ 错误：返回单个消息
return AIMessage(content="回复内容")
```

### 3. 状态访问
```python
def node_function(state):
    # 访问所有消息
    all_messages = state
    
    # 访问最后一条消息
    last_message = state[-1]
    
    # 访问第一条消息
    first_message = state[0]
    
    # 过滤特定类型的消息
    user_messages = [msg for msg in state if isinstance(msg, HumanMessage)]
```

## 常见模式

### 1. 链式处理
```python
START -> node1 -> node2 -> node3 -> END
```
所有节点按顺序执行，每个节点都能看到之前所有节点的输出。

### 2. 条件分支
```python
         ┌─> path_a -> END
node1 ──┤
         └─> path_b -> END
```
根据条件选择不同的执行路径。

### 3. 循环
```python
node1 -> node2 -> (条件判断) -> node1 (继续) 或 END (结束)
```
通过条件边实现循环，直到满足退出条件。

## 最佳实践

1. **保持节点功能单一**：每个节点只做一件事
2. **合理使用消息历史**：节点可以访问所有历史消息，利用这个特性
3. **明确状态更新**：确保返回的字典包含正确的 "messages" 键
4. **处理边界情况**：检查状态是否为空，消息是否存在等
5. **使用类型提示**：帮助 IDE 提供更好的代码补全和错误检查

## 运行示例

查看 `messagegraph_example.py` 获取完整的可运行示例代码。

```bash
python examples/messagegraph_example.py
```

