# 模块结构说明

## 重构说明

原来的 `chains.py` 已经拆分为多个独立模块，提供更好的代码组织和可维护性。

## 模块结构

### 核心模块

1. **llm.py** - LLM 初始化和管理
   - `get_llm()`: 创建新的 LLM 实例
   - `get_llm_instance()`: 获取全局 LLM 实例（单例模式）
   - 自动检测并配置 Azure OpenAI 或标准 OpenAI

2. **prompts.py** - 提示模板定义
   - `create_actor_prompt_template()`: 创建通用的演员提示模板
   - `REVISE_INSTRUCTIONS`: 修订指令常量

3. **first_responder.py** - 初始响应生成链
   - `create_first_responder()`: 创建初始响应生成链的函数
   - `first_responder`: 导出的链实例
   - `validator`: Pydantic 工具解析器

4. **revisor.py** - 答案修订链
   - `create_revisor()`: 创建答案修订链的函数
   - `revisor`: 导出的链实例

5. **nodes.py** - 节点实现模块（新增）
   - `draft_node()`: 初始答案生成节点函数
   - `execute_tools_node()`: 工具执行节点函数
   - `revise_node()`: 答案修订节点函数
   - `create_event_loop()`: 创建事件循环条件函数

6. **chains.py** - 向后兼容模块
   - 重新导出 `first_responder` 和 `revisor`，保持向后兼容
   - 建议新代码直接从对应模块导入

## 导入方式

### 推荐方式（新代码）

```python
# 导入特定链
from reflexion_agent.first_responder import first_responder
from reflexion_agent.revisor import revisor

# 导入 LLM
from reflexion_agent.infra import get_llm, get_llm_instance

# 导入提示模板
from reflexion_agent.infra import create_actor_prompt_template, REVISE_INSTRUCTIONS
```

### 向后兼容方式（旧代码仍可用）

```python
# 旧代码仍然可以工作
from reflexion_agent.chains import first_responder, revisor, llm
```

### 从包级别导入

```python
# 从包级别导入主要组件
from reflexion_agent import (
    create_reflexion_graph,
    first_responder,
    revisor,
    get_llm,
    get_llm_instance,
)

# 导入节点函数（如果需要单独使用）
from reflexion_agent.nodes import (
    draft_node,
    execute_tools_node,
    revise_node,
    create_event_loop,
)
```

## 依赖关系

```
graph.py
  ├── nodes.py
  │   ├── chains.py (向后兼容)
  │   │   ├── first_responder.py
  │   │   │   ├── llm.py
  │   │   │   ├── prompts.py
  │   │   │   └── schema.py
  │   │   └── revisor.py
  │   │       ├── llm.py
  │   │       ├── prompts.py
  │   │       └── schema.py
  │   └── tools.py
  └── nodes.py (节点实现)
      ├── draft_node (使用 first_responder)
      ├── execute_tools_node (使用 tool_node)
      ├── revise_node (使用 revisor)
      └── create_event_loop (条件函数)
```

## 优势

1. **更好的关注点分离**：每个模块职责单一
2. **更容易测试**：可以独立测试每个模块
3. **更好的可维护性**：修改一个模块不影响其他模块
4. **更好的可重用性**：可以在其他地方单独使用某个链
5. **向后兼容**：旧代码仍然可以正常工作

## 迁移指南

如果你有旧代码使用了 `chains.py`，可以逐步迁移：

```python
# 旧代码
from reflexion_agent.chains import first_responder, revisor

# 新代码（推荐）
from reflexion_agent.first_responder import first_responder
from reflexion_agent.revisor import revisor
```

两种方式都可以工作，但推荐使用新的导入方式，因为 `chains.py` 将来可能会被移除。

