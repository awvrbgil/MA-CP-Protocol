# MA-CP: Multi-Agent Collaboration Protocol 🧠
> **Stop trusting a single AI. Let them debate, verify, and reach consensus.**
> **拒绝单一模型的幻觉。通过多智能体辩论与共识机制，获取更客观、更精准的决策。**


## ⚡️ What is this? (这是什么？)

MA-CP 是一个**多智能体协作框架**，它不仅仅是让两个 AI 聊天，而是引入了**“议会制”**流程。
它解决了单体 LLM 的三大痛点：
1.  **幻觉 (Hallucination)**：通过对手（Challenger）的质疑来纠正错误。
2.  **偏见 (Bias)**：引入不同视角的角色（如激进派 vs 保守派）进行对冲。
3.  **缺乏深度 (Shallow Reasoning)**：通过多轮辩论强制模型进行 System 2 级别的深思。

## 🛠 Features (核心功能)

*   **⚔️ Debate & Consensus (辩论共识模式)**: 核心功能。两个 AI 针对一个问题进行多轮辩论，由 Referee AI 实时计算共识度（Consensus Score）。只有共识度 >80% 或达到回合上限才输出最终结论。
*   **🏟️ Local Arena (本地竞技场)**: 想知道 `Llama-3` 和 `DeepSeek-Coder` 谁写代码更好？让它们同台竞技，直观对比。
*   **🔌 Hybrid Support (混合架构)**: 支持本地 **Ollama** 模型与云端 API (OpenAI/Claude/DeepSeek) 混用。让 GPT-4 当裁判，本地小模型当辩手。
*   **🎭 Role-Playing System (角色系统)**: 内置 11+ 预设角色（魔鬼代言人、逻辑学家、事实核查员等）。
*   **💾 Structured Logs (结构化存档)**: 所有的思考过程均可导出为日志，便于复盘和数据集构建。

## 🎯 Use Cases (应用场景)

*   **代码审查**: 让 Agent A 写代码，Agent B 找 Bug，Agent C 总结修复方案。
*   **客观研报**: 让 Agent A 代表看多方，Agent B 代表看空方，生成平衡的市场分析。
*   **数据清洗**: 两个小模型互相验证数据的准确性。


## 🗺️ 愿景与未来

MA-CP 始于一个简单的“多AI辩论”脚本，长期愿景(/vision.md)
**这不仅仅是一个工具，更是一次关于“AI如何思考”的实验。**

---

> ## 🚀 快速开始 (Quick Start )
1.  **安装基础环境**：确保已安装 [Python 3.10+](https://www.python.org/downloads/) 和 [Ollama](https://ollama.com/)，并至少下载两个模型（如 `llama3.1:8b`）。
2.  **克隆项目**：
    ```bash
    git clone https://github.com/awvrbgil/MA-CP-Protocol.git
    cd MA-CP-Protocol
    ```
3.  **安装Python依赖**：
    ```bash
    pip install -r requirements.txt
    ```
4.  **配置与运行**：复制 `config.example.yaml` 为 `config.yaml`，根据你的模型修改配置，然后运行：
    ```bash
    python src/macp/scheduler.py
    ```

    ## 支持与赞助

MA CP 协议是一个充满热情的开源项目。如果这个协议和构想对你有所启发，或者你希望支持它的持续发展，欢迎通过赞助来表示你的支持。所有的赞助将直接用于项目的开发和服务器开销。

👉 **[点此查看详细的赞助方式与感谢](/docs/imgs/sponsor/sponsorship.md)**

---

## 🤝 加入我们

这是一个由独立开发者发起的实验性项目。我们坚信，好的想法只与行动有关。

我们邀请所有对 **“AI群体智慧”** 感兴趣的开发者、研究者和思考者，共同参与设计和构建这一协议的未来。

**路的前方是深渊还是大道，走过去才知道。而我们已经迈出了第一步。**




