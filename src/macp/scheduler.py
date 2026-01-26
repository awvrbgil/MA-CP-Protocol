"""
===============================================================================
多AI协作调度器 v5.0 - 终极优化版 (单文件版本)
MACP: Multi-Agent Collaboration Platform (多AI协作平台)
===============================================================================

核心功能：
├── 🤖 AI辩论系统 - 支持9种专业角色，多回合智能辩论
├── 🎯 共识度检测 - AI深度分析，实时监控辩论共识
├── 🐢 海龟汤游戏 - AI推理问答互动模式
├── 📊 并行提问 - 同时向多个AI模型提问
├── 🔄 智能结束 - 共识度达70%自动总结
└── 📝 历史记录 - 完整的对话和辩论保存

技术特性：
├── 🏗️ 模块化架构 - 单文件整合，易于部署
├── 🔍 类型安全 - 完整的类型注解
├── 📋 错误处理 - 完善的异常管理和日志
├── ⚡ 性能优化 - 并行处理和智能缓存
└── 🎨 用户友好 - 直观的命令行界面

使用环境：
├── Ollama服务 - 本地AI模型运行环境
├── Python 3.7+ - 运行环境要求
└── requests库 - 网络请求依赖

作者：匿名开发者
创建时间：2026年1月8日
版本：v5.0
===============================================================================
"""

import concurrent.futures
import json
import time
from datetime import datetime
import os
import sys
import re
import logging
import subprocess
import shutil
from typing import Dict, Any, List, Optional, Tuple

# ==================== 【全局标志】 ====================
NEED_API_SETUP = False  # 标记是否需要在启动后配置API
CURRENT_LANGUAGE = "zh"  # 当前语言: "zh" 中文, "en" 英文

# ==================== 【多语言系统】 ====================
LANG_DICT = {
    # ===== 通用 =====
    "yes": {"zh": "是", "en": "Yes"},
    "no": {"zh": "否", "en": "No"},
    "confirm": {"zh": "确认", "en": "Confirm"},
    "cancel": {"zh": "取消", "en": "Cancel"},
    "error": {"zh": "错误", "en": "Error"},
    "warning": {"zh": "警告", "en": "Warning"},
    "success": {"zh": "成功", "en": "Success"},
    "failed": {"zh": "失败", "en": "Failed"},
    "loading": {"zh": "加载中", "en": "Loading"},
    "please_wait": {"zh": "请稍候", "en": "Please wait"},
    "input_prompt": {"zh": "请输入问题或命令：", "en": "Enter question or command: "},
    "invalid_choice": {"zh": "无效选择", "en": "Invalid choice"},
    "press_enter": {"zh": "按回车键继续", "en": "Press Enter to continue"},
    
    # ===== 依赖检查 =====
    "dep_check_title": {"zh": "🔍 MACP 依赖检查系统", "en": "🔍 MACP Dependency Check System"},
    "checking_python": {"zh": "📌 检查 Python 版本...", "en": "📌 Checking Python version..."},
    "python_ok": {"zh": "满足要求", "en": "meets requirements"},
    "python_low": {"zh": "版本过低", "en": "version too low"},
    "install_python": {"zh": "请安装 Python 3.7 或更高版本", "en": "Please install Python 3.7 or higher"},
    "checking_requests": {"zh": "📌 检查 requests 库...", "en": "📌 Checking requests library..."},
    "requests_installed": {"zh": "requests 已安装", "en": "requests installed"},
    "requests_missing": {"zh": "requests 未安装", "en": "requests not installed"},
    "installing_requests": {"zh": "🔄 正在自动安装 requests...", "en": "🔄 Auto-installing requests..."},
    "requests_install_ok": {"zh": "requests 安装成功", "en": "requests installed successfully"},
    "requests_install_fail": {"zh": "requests 安装失败", "en": "requests installation failed"},
    "checking_ollama": {"zh": "📌 检查 Ollama...", "en": "📌 Checking Ollama..."},
    "ollama_installed": {"zh": "Ollama 已安装", "en": "Ollama installed"},
    "ollama_not_found": {"zh": "Ollama 未安装或未找到", "en": "Ollama not installed or not found"},
    "checking_ollama_service": {"zh": "📌 检查 Ollama 服务状态...", "en": "📌 Checking Ollama service status..."},
    "ollama_running": {"zh": "Ollama 服务运行中", "en": "Ollama service running"},
    "ollama_not_running": {"zh": "Ollama 服务未运行", "en": "Ollama service not running"},
    "starting_ollama": {"zh": "🔄 尝试启动 Ollama 服务...", "en": "🔄 Trying to start Ollama service..."},
    "ollama_started": {"zh": "Ollama 服务已成功启动", "en": "Ollama service started successfully"},
    "models_installed": {"zh": "已安装的模型", "en": "Installed models"},
    "no_models": {"zh": "暂无已安装的模型", "en": "No models installed"},
    "all_deps_ok": {"zh": "✅ 所有依赖检查通过！", "en": "✅ All dependencies check passed!"},
    "deps_missing": {"zh": "⚠️ 部分依赖未满足，程序可能无法正常运行", "en": "⚠️ Some dependencies missing, program may not work properly"},
    
    # ===== 模式选择 =====
    "select_mode": {"zh": "🤔 请选择运行模式：", "en": "🤔 Please select running mode:"},
    "mode_ollama": {"zh": "📥 下载 Ollama 并安装本地AI模型（推荐新手）", "en": "📥 Download Ollama and install local AI models (recommended for beginners)"},
    "mode_ollama_desc1": {"zh": "完全本地运行，无需网络", "en": "Runs completely locally, no network needed"},
    "mode_ollama_desc2": {"zh": "需要下载约 2-8GB 的模型文件", "en": "Requires downloading 2-8GB model files"},
    "mode_ollama_desc3": {"zh": "适合有较好显卡的电脑", "en": "Suitable for computers with good GPU"},
    "mode_api": {"zh": "🌐 使用 API 模式（推荐快速体验）", "en": "🌐 Use API mode (recommended for quick experience)"},
    "mode_api_desc1": {"zh": "使用云端AI，无需下载大文件", "en": "Uses cloud AI, no large downloads needed"},
    "mode_api_desc2": {"zh": "需要API密钥（硅基流动/DeepSeek等）", "en": "Requires API key (SiliconFlow/DeepSeek etc.)"},
    "mode_api_desc3": {"zh": "适合显卡较弱或想快速体验的用户", "en": "Suitable for users with weak GPU or quick experience"},
    "preparing_download": {"zh": "📥 准备下载 Ollama...", "en": "📥 Preparing to download Ollama..."},
    "opening_download": {"zh": "正在打开 Ollama 下载页面...", "en": "Opening Ollama download page..."},
    "download_opened": {"zh": "已打开下载页面", "en": "Download page opened"},
    "install_steps": {"zh": "📋 安装步骤：", "en": "📋 Installation steps:"},
    "recommended_models": {"zh": "💡 安装完成后，推荐下载以下模型：", "en": "💡 After installation, recommended models:"},
    "download_command": {"zh": "🔧 下载模型命令：", "en": "🔧 Download model command:"},
    "api_mode_selected": {"zh": "🌐 您选择了 API 模式", "en": "🌐 You selected API mode"},
    "api_mode_hint": {"zh": "程序将以纯API模式启动，稍后请配置API密钥", "en": "Program will start in API mode, please configure API key later"},
    
    # ===== 模型下载 =====
    "select_action": {"zh": "🤔 请选择：", "en": "🤔 Please select:"},
    "download_models_now": {"zh": "📥 现在下载推荐模型", "en": "📥 Download recommended models now"},
    "use_api_mode": {"zh": "🌐 使用API模式（无需下载）", "en": "🌐 Use API mode (no download needed)"},
    "skip_download": {"zh": "⏭️ 跳过，稍后手动下载", "en": "⏭️ Skip, download manually later"},
    "downloading_models": {"zh": "📥 开始下载推荐模型...", "en": "📥 Starting to download recommended models..."},
    "model_list": {"zh": "💡 推荐模型列表：", "en": "💡 Recommended model list:"},
    "select_models": {"zh": "选择要下载的模型", "en": "Select models to download"},
    "downloading": {"zh": "🔄 正在下载", "en": "🔄 Downloading"},
    "download_patience": {"zh": "（这可能需要几分钟，请耐心等待）", "en": "(This may take a few minutes, please wait)"},
    "download_complete": {"zh": "下载完成！", "en": "Download complete!"},
    "download_problem": {"zh": "下载可能出现问题", "en": "Download may have issues"},
    "download_failed": {"zh": "下载失败", "en": "Download failed"},
    "models_download_done": {"zh": "✅ 模型下载完成！", "en": "✅ Models download complete!"},
    "no_model_selected": {"zh": "未选择任何模型", "en": "No model selected"},
    "skipped_download": {"zh": "⏭️ 跳过模型下载", "en": "⏭️ Skipped model download"},
    "manual_download_hint": {"zh": "💡 稍后可以手动运行: ollama pull <模型名>", "en": "💡 You can manually run later: ollama pull <model_name>"},
    
    # ===== 欢迎界面 =====
    "welcome_title": {"zh": "🤖 MACP 多AI协作平台", "en": "🤖 MACP Multi-AI Collaboration Platform"},
    "model_1": {"zh": "模型1", "en": "Model 1"},
    "model_2": {"zh": "模型2", "en": "Model 2"},
    "coordinator_model": {"zh": "协调模型", "en": "Coordinator Model"},
    "optimize_mode": {"zh": "优化模式", "en": "Optimize Mode"},
    "enabled": {"zh": "开启", "en": "Enabled"},
    "disabled": {"zh": "关闭", "en": "Disabled"},
    
    # ===== 命令菜单 =====
    "available_commands": {"zh": "📋 可用命令：", "en": "📋 Available commands:"},
    "cmd_help": {"zh": "显示帮助", "en": "Show help"},
    "cmd_models": {"zh": "查看可用模型", "en": "View available models"},
    "cmd_config": {"zh": "查看当前配置", "en": "View current config"},
    "cmd_history": {"zh": "查看历史记录", "en": "View history"},
    "cmd_api": {"zh": "配置API模式", "en": "Configure API mode"},
    "cmd_debate": {"zh": "进入辩论模式", "en": "Enter debate mode"},
    "cmd_turtle": {"zh": "进入海龟汤模式", "en": "Enter turtle soup mode"},
    "cmd_consensus": {"zh": "配置共识检测", "en": "Configure consensus detection"},
    "cmd_language": {"zh": "切换语言", "en": "Switch language"},
    "cmd_exit": {"zh": "退出程序", "en": "Exit program"},
    
    # ===== 语言切换 =====
    "language_title": {"zh": "🌐 语言设置 / Language Settings", "en": "🌐 Language Settings / 语言设置"},
    "current_language": {"zh": "当前语言", "en": "Current language"},
    "select_language": {"zh": "请选择语言 / Please select language:", "en": "Please select language / 请选择语言:"},
    "language_chinese": {"zh": "中文 (Chinese)", "en": "Chinese (中文)"},
    "language_english": {"zh": "英文 (English)", "en": "English (英文)"},
    "language_changed": {"zh": "✅ 语言已切换为中文", "en": "✅ Language changed to English"},
    
    # ===== 辩论模式 =====
    "debate_title": {"zh": "🎭 辩论模式", "en": "🎭 Debate Mode"},
    "enter_topic": {"zh": "请输入辩论主题：", "en": "Enter debate topic: "},
    "debate_roles": {"zh": "🎭 辩论角色", "en": "🎭 Debate roles"},
    "round_n": {"zh": "第{n}回合", "en": "Round {n}"},
    "opening_statement": {"zh": "初始陈述", "en": "Opening statement"},
    "mutual_response": {"zh": "互相回应", "en": "Mutual response"},
    "rebuttal": {"zh": "反驳", "en": "Rebuttal"},
    "pro_side": {"zh": "正方", "en": "Pro side"},
    "con_side": {"zh": "反方", "en": "Con side"},
    "both_know_opponent": {"zh": "双方已知晓对手身份", "en": "Both sides know opponent's identity"},
    "using_models": {"zh": "🌐 使用模型", "en": "🌐 Using models"},
    "analyzing_consensus": {"zh": "🧠 正在分析双方共识度...", "en": "🧠 Analyzing consensus between both sides..."},
    "consensus_score": {"zh": "🔄 共识度", "en": "🔄 Consensus"},
    "ai_analysis": {"zh": "📝 分析", "en": "📝 Analysis"},
    "ai_suggests_end": {"zh": "🎯 AI建议: 结束辩论", "en": "🎯 AI suggests: End debate"},
    "ai_suggests_continue": {"zh": "🔄 AI建议: 继续辩论", "en": "🔄 AI suggests: Continue debate"},
    "consensus_reached": {"zh": "共识度达标", "en": "Consensus reached"},
    "auto_end_debate": {"zh": "自动结束辩论并生成总结", "en": "Auto-ending debate and generating summary"},
    "consensus_continue": {"zh": "距离阈值还差{n}%，辩论继续...", "en": "{n}% away from threshold, debate continues..."},
    "significant_divergence": {"zh": "分歧明显，继续深入辩论...", "en": "Significant divergence, continuing in-depth debate..."},
    
    # ===== 协调总结 =====
    "coordination_title": {"zh": "🎯 协调总结", "en": "🎯 Coordination Summary"},
    "high_consensus": {"zh": "🤝 双方已达成高度共识，生成最终总结", "en": "🤝 High consensus reached, generating final summary"},
    "coordinator_analyzing": {"zh": "🤖 协调AI正在分析...", "en": "🤖 Coordinator AI analyzing..."},
    "coordinator_generating": {"zh": "🤖 协调AI正在生成最终总结...", "en": "🤖 Coordinator AI generating final summary..."},
    "analysis_complete": {"zh": "✅ 协调AI分析完成：", "en": "✅ Coordinator AI analysis complete:"},
    "summary_complete": {"zh": "✅ 共识总结生成完成：", "en": "✅ Consensus summary complete:"},
    "empty_response": {"zh": "返回了空响应", "en": "Returned empty response"},
    "analysis_failed": {"zh": "❌ 协调AI分析失败", "en": "❌ Coordinator AI analysis failed"},
    
    # ===== 保存辩论 =====
    "debate_ended": {"zh": "📝 辩论已结束，是否保存辩论记录？", "en": "📝 Debate ended, save debate record?"},
    "save_to_log": {"zh": "📋 存储到日志文件 (macp.txt)", "en": "📋 Save to log file (macp.txt)"},
    "save_to_separate": {"zh": "📄 单独保存为新的txt文件", "en": "📄 Save as separate txt file"},
    "dont_save": {"zh": "❌ 不保存", "en": "❌ Don't save"},
    "saved_to_log": {"zh": "✅ 辩论记录已保存到日志文件", "en": "✅ Debate record saved to log file"},
    "saved_to_file": {"zh": "✅ 辩论记录已保存到", "en": "✅ Debate record saved to"},
    "save_skipped": {"zh": "⏭️ 跳过保存", "en": "⏭️ Skipped saving"},
    "save_failed": {"zh": "❌ 保存辩论记录失败", "en": "❌ Failed to save debate record"},
    
    # ===== 问题处理 =====
    "question_processing": {"zh": "🧠 问题处理", "en": "🧠 Question Processing"},
    "question": {"zh": "问题", "en": "Question"},
    "mode": {"zh": "模式", "en": "Mode"},
    "parallel": {"zh": "并行", "en": "Parallel"},
    "debate": {"zh": "辩论", "en": "Debate"},
    "turtle_soup": {"zh": "海龟汤", "en": "Turtle Soup"},
    "debate_complete": {"zh": "✅ 辩论完成", "en": "✅ Debate complete"},
    "total_time": {"zh": "总耗时", "en": "Total time"},
    "seconds": {"zh": "秒", "en": "seconds"},
    
    # ===== API配置 =====
    "api_config_title": {"zh": "🔗 API模式配置", "en": "🔗 API Mode Configuration"},
    "api_status": {"zh": "当前API模式状态", "en": "Current API mode status"},
    "api_provider": {"zh": "API提供方", "en": "API provider"},
    "api_url": {"zh": "API地址", "en": "API URL"},
    "api_model": {"zh": "API模型", "en": "API model"},
    "api_key": {"zh": "API密钥", "en": "API key"},
    "api_key_set": {"zh": "已设置", "en": "Set"},
    "api_key_not_set": {"zh": "未设置", "en": "Not set"},
    "model_use_api": {"zh": "使用API", "en": "Use API"},
    "enable_api_mode": {"zh": "是否启用API模式？", "en": "Enable API mode?"},
    "configure_api_for": {"zh": "⚙️ 配置 {name} 的API参数", "en": "⚙️ Configure API parameters for {name}"},
    "use_external_api": {"zh": "{name} 是否使用外部API？", "en": "Use external API for {name}?"},
    "current": {"zh": "当前", "en": "Current"},
    "select_provider": {"zh": "🏢 选择API提供方", "en": "🏢 Select API provider"},
    "custom_openai": {"zh": "自定义 (兼容OpenAI格式)", "en": "Custom (OpenAI compatible)"},
    "configure_base_url": {"zh": "🔧 配置API基础地址：", "en": "🔧 Configure API base URL:"},
    "api_key_config": {"zh": "🔑 API密钥配置：", "en": "🔑 API key configuration:"},
    "use_saved_key": {"zh": "使用已保存的密钥", "en": "Use saved key"},
    "enter_new_key": {"zh": "输入新的密钥", "en": "Enter new key"},
    "key_saved": {"zh": "✅ 已使用保存的密钥", "en": "✅ Using saved key"},
    "available_models": {"zh": "📦 获取到可用模型：", "en": "📦 Available models:"},
    "cannot_get_models": {"zh": "⚠️ 无法自动获取模型列表", "en": "⚠️ Cannot auto-fetch model list"},
    "enter_model_name": {"zh": "请输入使用的模型名称", "en": "Enter model name to use"},
    "api_disabled": {"zh": "⚠️ 所有AI都未配置使用API，将关闭API模式，仅使用本地Ollama。", "en": "⚠️ No AI configured to use API, disabling API mode, using local Ollama only."},
    "api_config_saved": {"zh": "✅ API配置已保存", "en": "✅ API configuration saved"},
    "reinitializing": {"zh": "🔄 正在重新初始化系统...", "en": "🔄 Reinitializing system..."},
    "reinit_complete": {"zh": "✅ 系统重新初始化完成", "en": "✅ System reinitialized"},
    "reinit_failed": {"zh": "❌ 重新初始化失败", "en": "❌ Reinitialization failed"},
    "api_mode_disabled": {"zh": "✅ 已禁用API模式", "en": "✅ API mode disabled"},
    
    # ===== 退出 =====
    "session_stats": {"zh": "📊 会话统计：", "en": "📊 Session statistics:"},
    "session_id": {"zh": "会话ID", "en": "Session ID"},
    "total_records": {"zh": "总记录数", "en": "Total records"},
    "goodbye": {"zh": "👋 再见！", "en": "👋 Goodbye!"},
    "exit_confirm": {"zh": "是否退出程序？", "en": "Exit program?"},
    "interrupt_detected": {"zh": "⚠️ 检测到中断信号", "en": "⚠️ Interrupt signal detected"},
    
    # ===== 错误信息 =====
    "error_occurred": {"zh": "❌ 发生错误", "en": "❌ Error occurred"},
    "unknown_command": {"zh": "未知命令", "en": "Unknown command"},
    "invalid_role": {"zh": "无效角色", "en": "Invalid role"},
    "connection_error": {"zh": "连接错误", "en": "Connection error"},
    "timeout_error": {"zh": "请求超时", "en": "Request timeout"},
    "api_request_error": {"zh": "API请求错误", "en": "API request error"},
}

def get_text(key: str, **kwargs) -> str:
    """获取当前语言的文本
    
    Args:
        key: 文本键名
        **kwargs: 格式化参数
    
    Returns:
        对应语言的文本
    """
    global CURRENT_LANGUAGE
    if key in LANG_DICT:
        text = LANG_DICT[key].get(CURRENT_LANGUAGE, LANG_DICT[key].get("zh", key))
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        return text
    return key

def set_language(lang: str):
    """设置当前语言
    
    Args:
        lang: 语言代码 ("zh" 或 "en")
    """
    global CURRENT_LANGUAGE
    if lang in ["zh", "en"]:
        CURRENT_LANGUAGE = lang

# ==================== 【依赖检查系统】 ====================
def check_and_install_dependencies():
    """检查并自动安装所有必要依赖
    
    检查项目：
    1. Python版本 (>= 3.7)
    2. requests库 - 网络请求依赖
    3. Ollama - 本地AI模型运行环境
    """
    global NEED_API_SETUP  # 声明全局变量
    
    print("=" * 60)
    print("🔍 MACP 依赖检查系统")
    print("=" * 60)
    
    all_ok = True
    
    # 1. 检查Python版本
    print("\n📌 检查 Python 版本...")
    py_version = sys.version_info
    if py_version.major >= 3 and py_version.minor >= 7:
        print(f"   ✅ Python {py_version.major}.{py_version.minor}.{py_version.micro} - 满足要求 (>= 3.7)")
    else:
        print(f"   ❌ Python {py_version.major}.{py_version.minor}.{py_version.micro} - 版本过低")
        print("      请安装 Python 3.7 或更高版本")
        print("      下载地址: https://www.python.org/downloads/")
        all_ok = False
    
    # 2. 检查并安装 requests 库
    print("\n📌 检查 requests 库...")
    try:
        import requests
        print(f"   ✅ requests 已安装 (版本: {requests.__version__})")
    except ImportError:
        print("   ⚠️ requests 未安装")
        print("   🔄 正在自动安装 requests...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "-q"],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import requests
            print(f"   ✅ requests 安装成功 (版本: {requests.__version__})")
        except Exception as e:
            print(f"   ❌ requests 安装失败: {e}")
            print("      请手动运行: pip install requests")
            all_ok = False
    
    # 3. 检查 Ollama
    print("\n📌 检查 Ollama...")
    ollama_installed = False
    ollama_running = False
    
    # 检查Ollama是否安装（通过命令行）
    ollama_cmd = shutil.which("ollama")
    if ollama_cmd:
        ollama_installed = True
        print(f"   ✅ Ollama 已安装 (路径: {ollama_cmd})")
    else:
        # Windows上可能在特定路径
        windows_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
            os.path.expandvars(r"%PROGRAMFILES%\Ollama\ollama.exe"),
            r"C:\Program Files\Ollama\ollama.exe"
        ]
        for path in windows_paths:
            if os.path.exists(path):
                ollama_installed = True
                print(f"   ✅ Ollama 已安装 (路径: {path})")
                break
    
    if not ollama_installed:
        print("   ⚠️ Ollama 未安装或未找到")
        print("\n" + "=" * 60)
        print("🤔 请选择运行模式：")
        print("=" * 60)
        print("  1. 📥 下载 Ollama 并安装本地AI模型（推荐新手）")
        print("     - 完全本地运行，无需网络")
        print("     - 需要下载约 2-8GB 的模型文件")
        print("     - 适合有较好显卡的电脑")
        print()
        print("  2. 🌐 使用 API 模式（推荐快速体验）")
        print("     - 使用云端AI，无需下载大文件")
        print("     - 需要API密钥（硅基流动/DeepSeek等）")
        print("     - 适合显卡较弱或想快速体验的用户")
        print("=" * 60)
        
        try:
            mode_choice = input("请选择 (1/2): ").strip()
            
            if mode_choice == "1":
                # 选择下载Ollama
                print("\n📥 准备下载 Ollama...")
                print("   1. 正在打开 Ollama 下载页面...")
                import webbrowser
                webbrowser.open("https://ollama.com/download")
                print("   ✅ 已打开下载页面")
                print("\n   📋 安装步骤：")
                print("      1. 下载并运行安装程序")
                print("      2. 安装完成后，程序会自动启动 Ollama 服务")
                print("      3. 重新运行本脚本")
                print("\n   💡 安装完成后，推荐下载以下模型：")
                print("      - qwen2.5:3b  (轻量级，约2GB)")
                print("      - llama3.2:3b (轻量级，约2GB)")
                print("      - qwen2.5:7b  (推荐，约4GB)")
                print("      - deepseek-r1:8b (推理增强，约5GB)")
                print("\n   🔧 下载模型命令：")
                print("      ollama pull qwen2.5:3b")
                print("      ollama pull llama3.2:3b")
                print()
                input("   按回车键退出，安装Ollama后请重新运行本程序...")
                sys.exit(0)
                
            elif mode_choice == "2":
                # 选择API模式 - 标记需要配置API
                print("\n🌐 您选择了 API 模式")
                print("   程序将以纯API模式启动，稍后请配置API密钥")
                print()
                # 设置全局标志，稍后在主程序中检测并引导配置API
                NEED_API_SETUP = True
                all_ok = True  # 允许程序继续运行
            else:
                print("   ⚠️ 无效选择，程序将继续运行")
                print("   您可以稍后运行 /api 命令配置API模式")
                all_ok = False
        except Exception as e:
            print(f"   ⚠️ 输入错误: {e}")
            all_ok = False
    else:
        # 检查Ollama服务是否运行
        print("\n📌 检查 Ollama 服务状态...")
        try:
            import requests as req
            response = req.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_running = True
                models = response.json().get("models", [])
                print(f"   ✅ Ollama 服务运行中")
                if models:
                    print(f"   📦 已安装的模型: {len(models)}个")
                    for m in models[:5]:  # 只显示前5个
                        print(f"      - {m.get('name', '未知')}")
                    if len(models) > 5:
                        print(f"      ... 还有 {len(models) - 5} 个模型")
                else:
                    print("   ⚠️ 暂无已安装的模型")
                    print("\n   🤔 请选择：")
                    print("      1. 📥 现在下载推荐模型")
                    print("      2. 🌐 使用API模式（无需下载）")
                    print("      3. ⏭️ 跳过，稍后手动下载")
                    
                    try:
                        model_choice = input("   请选择 (1/2/3): ").strip()
                        
                        if model_choice == "1":
                            print("\n   📥 开始下载推荐模型...")
                            print("   💡 推荐模型列表：")
                            print("      1. qwen2.5:3b  - 轻量级中文模型 (~2GB)")
                            print("      2. llama3.2:3b - 轻量级英文模型 (~2GB)")
                            print("      3. qwen2.5:7b  - 中等中文模型 (~4GB)")
                            print("      4. gemma3:4b   - Google轻量模型 (~3GB)")
                            
                            download_choice = input("\n   选择要下载的模型 (1-4，多个用逗号分隔，如1,2): ").strip()
                            models_to_download = []
                            model_map = {
                                "1": "qwen2.5:3b",
                                "2": "llama3.2:3b", 
                                "3": "qwen2.5:7b",
                                "4": "gemma3:4b"
                            }
                            
                            for choice in download_choice.split(","):
                                choice = choice.strip()
                                if choice in model_map:
                                    models_to_download.append(model_map[choice])
                            
                            if models_to_download:
                                for model in models_to_download:
                                    print(f"\n   🔄 正在下载 {model}...")
                                    print("   （这可能需要几分钟，请耐心等待）")
                                    try:
                                        result = subprocess.run(
                                            ["ollama", "pull", model],
                                            capture_output=False,
                                            text=True
                                        )
                                        if result.returncode == 0:
                                            print(f"   ✅ {model} 下载完成！")
                                        else:
                                            print(f"   ⚠️ {model} 下载可能出现问题")
                                    except Exception as download_err:
                                        print(f"   ❌ 下载失败: {download_err}")
                                print("\n   ✅ 模型下载完成！")
                            else:
                                print("   ⚠️ 未选择任何模型")
                                
                        elif model_choice == "2":
                            print("\n   🌐 您选择了 API 模式")
                            NEED_API_SETUP = True
                            
                        else:
                            print("   ⏭️ 跳过模型下载")
                            print("   💡 稍后可以手动运行: ollama pull <模型名>")
                            
                    except Exception as e:
                        print(f"   ⚠️ 操作出错: {e}")
        except Exception as e:
            print(f"   ⚠️ Ollama 服务未运行")
            print("   🔄 尝试启动 Ollama 服务...")
            try:
                # 尝试在后台启动Ollama
                if os.name == 'nt':  # Windows
                    subprocess.Popen(["ollama", "serve"], 
                                   stdout=subprocess.DEVNULL, 
                                   stderr=subprocess.DEVNULL,
                                   creationflags=subprocess.CREATE_NO_WINDOW)
                else:
                    subprocess.Popen(["ollama", "serve"],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                print("   ⏳ 等待服务启动...")
                time.sleep(3)
                
                # 再次检查
                try:
                    response = req.get("http://localhost:11434/api/tags", timeout=5)
                    if response.status_code == 200:
                        ollama_running = True
                        print("   ✅ Ollama 服务已成功启动")
                except:
                    print("   ⚠️ 服务启动可能需要更多时间，程序将继续运行")
                    print("      如遇问题，请手动运行: ollama serve")
            except Exception as start_error:
                print(f"   ⚠️ 自动启动失败: {start_error}")
                print("      请手动运行: ollama serve")
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 所有依赖检查通过！")
    else:
        print("⚠️ 部分依赖未满足，程序可能无法正常运行")
        print("   请按照上述说明安装缺失的依赖")
    print("=" * 60 + "\n")
    
    return all_ok

# 执行依赖检查
check_and_install_dependencies()

# ==================== 【依赖导入】 ====================
try:
    import requests
except ImportError:
    print("❌ 缺少必要依赖库 'requests'，请运行: pip install requests")
    sys.exit(1)

# ============ 系统初始化和兼容性处理 ============

# 处理Windows系统的编码问题，确保中文显示正常
# Windows默认使用GBK编码，而Python字符串是UTF-8
if os.name == 'nt':  # 检查是否为Windows系统
    import io
    # 重新包装标准输出流，使用UTF-8编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 导入网络请求库，用于与Ollama API通信
import requests

# ==================== 【自定义异常类】 ====================
# 定义MACP系统专用的异常类型，便于错误处理和调试

class AICouncilException(Exception):
    """AI委员会调度器基础异常类

    所有MACP相关异常的基类，提供统一的异常处理接口
    """
    pass

class OllamaConnectionError(AICouncilException):
    """Ollama服务连接错误

    当无法连接到Ollama API服务时抛出此异常
    通常发生在Ollama服务未启动或网络连接问题时
    """
    def __init__(self, message: str = "无法连接到Ollama服务"):
        super().__init__(message)

class ModelNotFoundError(AICouncilException):
    """AI模型未找到错误

    当请求的AI模型在Ollama中不存在时抛出此异常
    包含具体的模型名称信息，便于用户下载相应模型
    """
    def __init__(self, model_name: str):
        super().__init__(f"模型 '{model_name}' 未找到")
        self.model_name = model_name

class InvalidRoleError(AICouncilException):
    """无效角色错误

    当用户选择的辩论角色不存在或无效时抛出此异常
    包含具体的角色名称信息，帮助用户选择正确的角色
    """
    def __init__(self, role_name: str):
        super().__init__(f"无效角色: '{role_name}'")
        self.role_name = role_name

class ConsensusTimeoutError(AICouncilException):
    """共识检测超时错误

    当AI共识分析过程超时或失败时抛出此异常
    通常在网络请求超时或AI分析服务异常时发生
    """
    def __init__(self, message: str = "共识检测超时"):
        super().__init__(message)

class ConfigurationError(AICouncilException):
    """配置错误

    当系统配置出现问题时抛出此异常
    例如配置文件损坏、配置项无效等情况
    """
    def __init__(self, message: str = "配置错误"):
        super().__init__(message)

# ==================== 【日志系统】 ====================
# 统一的日志记录系统，用于跟踪系统运行状态、错误和性能指标

class Logger:
    """MACP日志管理器

    提供分级日志记录功能，支持文件和控制台双重输出
    用于系统调试、性能监控和错误追踪

    Attributes:
        log_file: 日志文件路径
        level: 日志记录级别 (DEBUG, INFO, WARNING, ERROR)
    """

    def __init__(self, log_file: str = r"C:\Users\yuangu114514\Desktop\macp.txt", level: int = logging.INFO):
        self.log_file = log_file
        self.level = level
        self._setup_logger()

    def _setup_logger(self):
        """设置日志器"""
        # 创建日志目录
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        # 配置日志格式
        log_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 创建日志器
        self.logger = logging.getLogger('MACP')
        self.logger.setLevel(self.level)

        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台处理器 - 只显示WARNING及以上级别，减少干扰
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # 控制台只显示警告和错误
            console_handler.setFormatter(log_format)
            self.logger.addHandler(console_handler)

            # 文件处理器 - 保留所有INFO级别日志
            try:
                file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
                file_handler.setLevel(self.level)
                file_handler.setFormatter(log_format)
                self.logger.addHandler(file_handler)
            except (OSError, IOError) as e:
                print(f"⚠️  无法创建日志文件: {e}")

    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)

    def error(self, message: str, exc_info: Optional[Exception] = None):
        """记录错误日志"""
        if exc_info:
            self.logger.error(message, exc_info=exc_info)
        else:
            self.logger.error(message)

    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)

    def log_operation(self, operation: str, start_time: datetime, end_time: Optional[datetime] = None):
        """记录操作日志"""
        duration = (end_time or datetime.now()) - start_time
        self.info(f"操作 '{operation}' 完成，耗时: {duration.total_seconds():.2f}秒")

# 全局日志器实例
logger = Logger()

# ==================== 【共识检测系统】 ====================
# AI辩论过程中的智能共识度分析系统

class ConsensusDetector:
    """AI辩论共识检测器

    这是MACP系统的核心智能组件之一，负责分析辩论双方观点的相似程度：

    两种检测方法：
    1. calculate_consensus() - 基于关键词重叠的快速检测
    2. analyze_debate_consensus() - 基于AI语义理解的深度检测

    主要应用场景：
    - 辩论模式的自动结束判断
    - 实时共识度监控和显示
    - 辩论质量评估和总结生成
    """
    """AI辩论共识检测器

    提供多种方法来分析两个AI模型在辩论中的共识程度：
    1. 传统关键词匹配方法（快速但简单）
    2. AI深度分析方法（准确但需要额外计算）

    主要用于辩论模式的自动结束判断和进度监控
    """

    @staticmethod
    def calculate_consensus(text1: str, text2: str) -> float:
        """计算两个文本的共识度（传统关键词方法）

        使用简单的关键词重叠算法快速评估共识度：
        1. 将两个文本都转换为小写
        2. 提取3个字符以上的词语作为关键词
        3. 计算两个关键词集合的交集比例
        4. 返回共识度分数(0.0-1.0)

        优点：计算速度快，无需外部AI调用
        缺点：只能检测表面关键词，无法理解语义深度

        主要用于：
        - AI共识分析失败时的后备方案
        - 快速预估共识度
        - 简单的文本相似度检测

        Returns:
            float: 共识度分数，0.0(完全不同)到1.0(完全相同)
        """
        if not text1 or not text2:
            return 0.0

        # 提取关键词（3个字符以上的词）
        words1 = set(re.findall(r'\b\w{3,}\b', text1.lower()))
        words2 = set(re.findall(r'\b\w{3,}\b', text2.lower()))

        if not words1 or not words2:
            return 0.0

        common_words = words1.intersection(words2)
        total_words = len(words1.union(words2))

        return len(common_words) / total_words if total_words > 0 else 0.0

    @staticmethod
    def analyze_debate_consensus(scheduler, coordinator_model: str, question: str,
                                debate_history: List[Dict[str, Any]], role1: str, role2: str) -> Tuple[float, str, Dict[str, Any]]:
        """AI驱动的辩论共识深度分析

        使用第三个AI模型（协调AI）来分析辩论双方当前的共识程度：
        1. 构建完整的辩论历史摘要
        2. 向协调AI发送详细分析请求
        3. 解析AI返回的共识评估结果
        4. 返回共识度百分比、分析摘要和详细数据

        这是实现"智能辩论结束"的核心机制，能够理解AI之间的
        语义共识，而不仅仅是关键词匹配

        Args:
            scheduler: AICouncilScheduler实例
            coordinator_model (str): 协调AI模型名称
            question (str): 原始辩论问题
            debate_history (List[Dict[str, Any]]): 完整的辩论历史记录
            role1 (str): 第一位辩论者的角色名称
            role2 (str): 第二位辩论者的角色名称

        Returns:
            tuple: (共识度分数, 分析摘要, 详细分析数据字典)
        """
        try:
            # 构建完整的辩论历史摘要
            debate_summary = ""
            for i, entry in enumerate(debate_history, 1):
                speaker = entry.get('speaker', '未知')
                content = entry.get('content', '')[:300]  # 限制单条内容长度
                round_num = entry.get('round', i)
                entry_type = entry.get('type', 'statement')
                debate_summary += f"\n第{round_num}回合 - {speaker} ({entry_type}): {content}"

            # 构建AI分析提示词
            consensus_prompt = f"""你是一位专业的辩论分析专家，请仔细分析以下辩论过程，评估双方的共识程度。

【辩论主题】: {question}
【辩论双方】: {role1} vs {role2}

【完整辩论记录】:
{debate_summary}

【分析任务】:
1. 观察双方AI的言语内容，分析他们的观点变化和立场调整
2. 识别双方在哪些方面达成了共识，在哪些方面存在分歧
3. 基于双方最新的观点，给出整体共识度百分比（0-100%）
4. 如果共识度达到70%以上，请判断是否应该结束辩论

【评估标准】:
- 共识度0-30%: 严重分歧，观点对立
- 共识度30-50%: 部分分歧，仍有较大差异
- 共识度50-70%: 基本共识，存在可调和的分歧
- 共识度70-90%: 高度共识，核心观点一致
- 共识度90-100%: 完全共识，观点高度统一

请以JSON格式回答，包含以下字段:
{{
    "consensus_percentage": 75,
    "confidence_level": "high/medium/low",
    "analysis_summary": "简要分析双方共识情况",
    "key_agreements": ["共识点1", "共识点2"],
    "key_disagreements": ["分歧点1", "分歧点2"],
    "recommendation": "continue/end",
    "reasoning": "详细分析过程和推理"
}}

请确保consensus_percentage是基于双方最新回合内容的准确评估。"""

            coord_client, coord_model, is_api = scheduler._get_client_for_model(coordinator_model)
            if is_api:
                response = coord_client.generate_response(consensus_prompt, max_tokens=800, temperature=scheduler.config.temperature)
            else:
                response = coord_client.generate_response(coord_model, consensus_prompt, max_tokens=800,
                                                        temperature=scheduler.config.temperature, timeout=scheduler.config.timeout,
                                                        streaming=False)

            if response.get("success"):
                result_text = response.get("response", "")
                return ConsensusDetector._parse_consensus_analysis(result_text)
            else:
                logger.warning("AI共识分析请求失败，使用传统方法")
                # 返回传统方法的结果
                traditional_score = ConsensusDetector.calculate_consensus(
                    debate_history[-1].get('content', '') if debate_history else '',
                    debate_history[-2].get('content', '') if len(debate_history) > 1 else ''
                )
                return traditional_score, "AI分析失败，使用传统方法", {}

        except (AICouncilException, requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
            logger.error(f"AI共识检测出错: {e}")
            return 0.0, f"检测出错: {str(e)}", {}

    @staticmethod
    def _parse_consensus_analysis(text: str) -> Tuple[float, str, Dict[str, Any]]:
        """解析AI共识分析结果"""
        try:
            # 尝试提取JSON部分
            json_start = text.find('{')
            json_end = text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = text[json_start:json_end]
                analysis_data = json.loads(json_str)

                consensus_percentage = analysis_data.get('consensus_percentage', 0)
                analysis_summary = analysis_data.get('analysis_summary', '分析完成')

                # 确保百分比在0-100范围内
                consensus_percentage = max(0, min(100, consensus_percentage))

                return float(consensus_percentage) / 100.0, analysis_summary, analysis_data
            else:
                # 如果没有找到JSON，尝试提取百分比
                percentage_match = re.search(r'(\d+(?:\.\d+)?)%', text)
                if percentage_match:
                    percentage = float(percentage_match.group(1))
                    percentage = max(0, min(100, percentage))
                    return percentage / 100.0, text, {}
                else:
                    return 0.5, text, {}

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"解析AI共识分析结果失败: {e}")
            # 返回文本分析结果
            return ConsensusDetector._extract_consensus_from_text(text)

    @staticmethod
    def calculate_ai_consensus(scheduler, coordinator_model: str, question: str,
                             debate_history: List[Dict[str, Any]], role1: str, role2: str) -> Tuple[float, str, Dict[str, Any]]:
        """通过AI分析计算共识度

        Args:
            scheduler: AICouncilScheduler实例
            coordinator_model: 协调AI模型名称
            question: 辩论问题
            debate_history: 辩论历史记录
            role1: 第一个辩论者角色
            role2: 第二个辩论者角色

        Returns:
            tuple: (共识度分数, 分析摘要, 详细数据字典)
        """
        try:
            # 构建辩论摘要
            debate_summary = ""
            for entry in debate_history[-4:]:  # 最近4轮对话
                speaker = entry.get('speaker', '未知')
                content = entry.get('content', '')[:200]  # 限制长度
                debate_summary += f"\n{speaker}: {content}"

            # 构建AI分析提示
            consensus_prompt = f"""请作为中立协调员分析以下辩论，评估双方观点的共识程度：

问题：{question}
辩论双方：{role1} vs {role2}

最近辩论内容：
{debate_summary}

请分析：
1. 双方的核心观点有哪些相似之处？
2. 主要分歧点是什么？
3. 整体共识度是多少百分比？（0-100%）

请以JSON格式回答：
{{
    "consensus_percentage": 85,
    "analysis": "详细分析内容",
    "key_agreements": ["相似点1", "相似点2"],
    "key_disagreements": ["分歧点1", "分歧点2"]
}}"""

            coord_client, coord_model, is_api = scheduler._get_client_for_model(coordinator_model)
            if is_api:
                response = coord_client.generate_response(consensus_prompt, max_tokens=600, temperature=scheduler.config.temperature)
            else:
                response = coord_client.generate_response(coord_model, consensus_prompt, max_tokens=600,
                                                        temperature=scheduler.config.temperature, timeout=scheduler.config.timeout,
                                                        streaming=False)

            if response.get("success"):
                result_text = response.get("response", "")

                # 尝试解析JSON响应
                try:
                    # 如果响应为空，直接使用fallback
                    if not result_text:
                        logger.warning("AI返回空响应，使用后备分析")
                        fallback_score, fallback_analysis, fallback_data = ConsensusDetector._fallback_consensus_analysis(
                            debate_history, role1, role2, question)
                        return fallback_score, fallback_analysis, fallback_data
                    # 提取JSON部分
                    json_start = result_text.find('{')
                    json_end = result_text.rfind('}') + 1

                    if json_start != -1 and json_end > json_start:
                        json_str = result_text[json_start:json_end]
                        analysis_data = json.loads(json_str)

                        consensus_percentage = analysis_data.get('consensus_percentage', 50)
                        analysis = analysis_data.get('analysis', 'AI分析完成')

                        # 提取其他数据
                        key_agreements = analysis_data.get('key_agreements', [])
                        key_disagreements = analysis_data.get('key_disagreements', [])
                        recommendation = analysis_data.get('recommendation', '')

                        data = {
                            'key_agreements': key_agreements,
                            'key_disagreements': key_disagreements,
                            'recommendation': recommendation
                        }

                        return float(consensus_percentage) / 100.0, analysis, data
                    else:
                        # 如果没有找到JSON，尝试提取百分比
                        percentage_match = re.search(r'(\d+(?:\.\d+)?)%', result_text)
                        if percentage_match:
                            percentage = float(percentage_match.group(1))
                            return percentage / 100.0, result_text, {}
                        else:
                            # 默认返回中等共识度
                            return 0.5, result_text, {}

                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    logger.warning(f"解析AI共识分析结果失败: {e}")
                    # 检查是否返回了空内容，如果是则使用fallback分析
                    if not result_text or not result_text.strip():
                        logger.info("AI返回空内容，使用后备分析")
                        fallback_score, fallback_analysis, fallback_data = ConsensusDetector._fallback_consensus_analysis(
                            debate_history, role1, role2, question)
                        return fallback_score, fallback_analysis, fallback_data
                    else:
                        # 尝试从文本中提取共识度信息
                        score, analysis, data = ConsensusDetector._extract_consensus_from_text(result_text)
                        return score, analysis, data
            else:
                logger.warning("AI共识分析请求失败")
                return 0.0, "分析失败", {}

        except (AICouncilException, requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
            logger.error(f"AI共识检测出错: {e}")
            return 0.0, f"检测出错: {str(e)}", {}

    @staticmethod
    def _fallback_consensus_analysis(debate_history: List[Dict[str, Any]], role1: str, role2: str,
                                   question: str) -> Tuple[float, str, Dict[str, Any]]:
        """当AI分析失败时的后备共识分析

        基于关键词匹配和辩论模式提供简单的共识度估算
        
        Args:
            debate_history: 辩论历史记录
            role1: 第一个辩论者角色（未使用，保留用于未来扩展）
            role2: 第二个辩论者角色（未使用，保留用于未来扩展）
            question: 辩论问题（未使用，保留用于未来扩展）
        """
        _ = (role1, role2, question)  # 标记参数已知但未使用（为未来扩展保留）
        try:
            # 提取所有辩论内容
            all_content = ""
            for entry in debate_history:
                content = entry.get('content', '')
                all_content += content + " "

            all_content_lower = all_content.lower()

            # 共识关键词
            consensus_words = ['同意', '认可', '没错', '确实', '有道理', '理解', '相同', '一致', '认同']
            # 分歧关键词
            disagreement_words = ['但是', '然而', '不同', '反对', '不认同', '分歧', '争议', '但是', '可是']

            consensus_count = sum(1 for word in consensus_words if word in all_content_lower)
            disagreement_count = sum(1 for word in disagreement_words if word in all_content_lower)

            total_signals = consensus_count + disagreement_count
            if total_signals == 0:
                consensus_score = 0.5  # 默认中等共识
            else:
                consensus_score = consensus_count / total_signals
                consensus_score = max(0.2, min(0.8, consensus_score))  # 限制在0.2-0.8范围内

            # 生成分析摘要
            if consensus_score > 0.6:
                analysis = f"双方观点基本一致，共识度较高。检测到{consensus_count}个共识信号。"
            elif consensus_score > 0.4:
                analysis = f"双方观点存在一定分歧，也有一些共识。共识信号:{consensus_count},分歧信号:{disagreement_count}。"
            else:
                analysis = f"双方观点分歧较大。检测到{disagreement_count}个分歧信号。"

            # 简单的结构化数据
            data = {
                'key_agreements': ['双方都重视各自领域的重要性'] if consensus_count > 0 else [],
                'key_disagreements': ['在优先级排序上存在分歧'] if disagreement_count > 0 else [],
                'recommendation': '建议双方深入讨论具体案例',
                'method': 'fallback_keyword_analysis'
            }

            return consensus_score, analysis, data

        except (ValueError, KeyError, TypeError) as e:
            logger.error(f"Fallback分析失败: {e}")
            return 0.5, "后备分析失败，使用默认中等共识度", {'method': 'default'}

    @staticmethod
    def _extract_consensus_from_text(text: str) -> Tuple[float, str, Dict[str, Any]]:
        """从文本中提取共识度信息"""
        text_lower = text.lower()
        _ = text_lower  # 标记为已知但未使用（为未来扩展保留）

        # 查找共识度相关关键词
        if '高度共识' in text or '高度一致' in text or '完全同意' in text:
            return 0.9, text, {}
        elif '基本共识' in text or '基本一致' in text or '大体同意' in text:
            return 0.75, text, {}
        elif '部分共识' in text or '部分一致' in text or '部分同意' in text:
            return 0.6, text, {}
        elif '分歧较大' in text or '存在分歧' in text or '不同意' in text:
            return 0.3, text, {}
        elif '完全分歧' in text or '完全不同' in text:
            return 0.1, text, {}
        else:
            # 查找百分比
            percentage_match = re.search(r'(\d+(?:\.\d+)?)%', text)
            if percentage_match:
                percentage = float(percentage_match.group(1))
                return percentage / 100.0, text, {}

            # 默认中等共识度
            return 0.5, text, {}

    @staticmethod
    def display_consensus_bar(percentage: float, width: int = 50):
        """显示共识度条形图"""
        percentage_int = int(percentage) if isinstance(percentage, float) else percentage
        filled = int(width * percentage_int / 100)
        bar = "█" * filled + "░" * (width - filled)

        # 根据共识度选择颜色描述
        percentage_int = int(percentage) if isinstance(percentage, float) else percentage
        if percentage_int >= 80:
            color_desc = "深绿"
        elif percentage_int >= 70:
            color_desc = "绿色"
        elif percentage_int >= 60:
            color_desc = "黄绿"
        elif percentage_int >= 50:
            color_desc = "黄色"
        elif percentage_int >= 40:
            color_desc = "橙色"
        else:
            color_desc = "红色"

        print(f"🔄 共识度: [{bar}] {percentage_int}% ({color_desc})")

    @staticmethod
    def get_consensus_level_description(percentage: float) -> str:
        """获取共识度等级描述"""
        if percentage >= 0.9:
            return "完全共识"
        elif percentage >= 0.8:
            return "高度共识"
        elif percentage >= 0.7:
            return "基本共识"
        elif percentage >= 0.6:
            return "部分共识"
        elif percentage >= 0.5:
            return "轻度共识"
        elif percentage >= 0.4:
            return "明显分歧"
        elif percentage >= 0.3:
            return "较大分歧"
        elif percentage >= 0.2:
            return "严重分歧"
        else:
            return "完全对立"

class HistoryManager:
    """历史记录管理器"""

    def __init__(self, history_file: str):
        self.history_file = history_file
        self.history: List[Dict[str, Any]] = []

    def add_entry(self, entry: Dict[str, Any]):
        """添加历史记录"""
        entry["timestamp"] = datetime.now().isoformat()
        self.history.append(entry)

    def save_history(self):
        """保存历史记录到文件"""
        try:
            os.makedirs(os.path.dirname(self.history_file), exist_ok=True)

            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = {"sessions": []}

            if "sessions" not in data:
                data["sessions"] = []

            data["sessions"].extend(self.history)

            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"💾 记录已保存到：{self.history_file}")
            self.history.clear()  # 清空缓存

        except (OSError, IOError, json.JSONDecodeError, ValueError) as e:
            logger.error(f"保存历史记录失败：{e}")

    def get_recent_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的历史记录"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions = data.get("sessions", [])
                    return sessions[-limit:]
        except Exception as e:
            logger.error(f"读取历史记录失败：{e}")
        return []

class DisplayManager:
    """显示管理器"""

    @staticmethod
    def print_separator(char: str = "=", length: int = 80):
        """打印分隔符"""
        print(char * length)

    @staticmethod
    def print_header(title: str, char: str = "=", length: int = 80):
        """打印标题"""
        DisplayManager.print_separator(char, length)
        print(f" {title} ".center(length - 2, " "))
        DisplayManager.print_separator(char, length)

    @staticmethod
    def print_result(result: Dict[str, Any], display_length: int = 1000, streaming_used: bool = False):
        """打印结果

        Args:
            result: AI响应结果
            display_length: 显示长度限制
            streaming_used: 是否已经使用了流式输出
        """
        success = result.get("success", False)
        model = result.get("model", "未知模型")
        response = result.get("response", "（无回答）")
        elapsed_time = result.get("time", 0)

        if streaming_used:
            # 流式输出时只显示状态和时间
            status = "✅" if success else "❌"
            print(f" {status} 完成 ({elapsed_time:.2f}秒)")
        else:
            # 非流式输出时显示完整结果
            status = "✅" if success else "❌"
            print(f"\n{status} {model} ({elapsed_time:.2f}秒）：")

            if success:
                print(response[:display_length] + ("..." if len(response) > display_length else ""))
            else:
                print(f"  错误：{response}")

    @staticmethod
    def clear_screen():
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
        print("🔄 屏幕已清空")

    @staticmethod
    def format_model_list(models: List[str]) -> str:
        """格式化模型列表显示"""
        if models:
            return "可用模型：\n" + "\n".join(f"  - {model}" for model in models)
        return "❌ 无法获取模型列表"

    @staticmethod
    def format_config_display(config_dict: Dict[str, Any]) -> str:
        """格式化配置显示"""
        return "⚙️  当前配置：\n" + "\n".join(f"  {key}: {value}" for key, value in config_dict.items())

class InputValidator:
    """输入验证器"""

    @staticmethod
    def validate_role_input(role_input: str, available_roles: List[str]) -> str:
        """验证角色输入"""
        if not role_input:
            return available_roles[0]  # 返回默认角色

        # 检查是否为数字
        if role_input.isdigit():
            role_num_map = {str(i + 1): role for i, role in enumerate(available_roles)}
            role = role_num_map.get(role_input)
            if role:
                return role

        # 检查是否为有效角色名
        if role_input in available_roles:
            return role_input

        # 返回默认角色
        return available_roles[0]

    @staticmethod
    def validate_yes_no_input(prompt: str, default: bool = False) -> bool:
        """验证是/否输入"""
        while True:
            response = input(prompt).strip().lower()
            if response in ['y', 'yes', '是']:
                return True
            elif response in ['n', 'no', '否']:
                return False
            elif not response and default is not None:
                return default
            print("请输入 y/yes/是 或 n/no/否")

    @staticmethod
    def get_yes_no_input(prompt: str, default: bool = False) -> bool:
        """获取是/否输入（别名方法）"""
        return InputValidator.validate_yes_no_input(prompt, default)

class ProgressTracker:
    """进度跟踪器"""

    def __init__(self):
        self.start_time = None
        self.total_operations = 0
        self.completed_operations = 0

    def start(self, total_operations: int = 0) -> datetime:
        """开始跟踪"""
        self.start_time = datetime.now()
        self.total_operations = total_operations
        self.completed_operations = 0
        return self.start_time

    def update(self, increment: int = 1):
        """更新进度"""
        self.completed_operations += increment

    def get_elapsed_time(self) -> float:
        """获取已用时间"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0

    def get_progress_percentage(self) -> float:
        """获取进度百分比"""
        if self.total_operations > 0:
            return (self.completed_operations / self.total_operations) * 100
        return 0.0

    def print_progress(self, message: str = ""):
        """打印进度"""
        elapsed = self.get_elapsed_time()
        percentage = self.get_progress_percentage()

        progress_str = f"⏱️  {message} | 进度: {percentage:.1f}% | 已用时: {elapsed:.2f}秒"
        if self.total_operations > 0:
            progress_str += f" | {self.completed_operations}/{self.total_operations}"

        print(f"\r{progress_str}", end="", flush=True)
        if percentage >= 100:
            print()  # 换行

# ==================== 【配置管理系统】 ====================
# 系统配置的集中管理，支持动态加载和保存

class Config:
    """MACP系统配置管理器

    管理所有系统配置项，包括：
    - AI模型参数（温度、token限制等）
    - 辩论模式设置（回合数、共识阈值等）
    - 历史记录配置
    - UI显示参数

    支持从文件加载配置和保存配置到文件
    """

    def __init__(self):
        # ============ Ollama服务配置 ============
        self.ollama_url = "http://localhost:11434"  # Ollama本地服务地址，默认localhost:11434
        self.model_1 = "qwen2.5:3b"                  # 主要辩论AI模型，用于第一个辩论者
        self.model_2 = "llama3.2:3b"                 # 辅助辩论AI模型，用于第二个辩论者
        self.coordinator_model = "gemma3:4b"        # 共识分析协调AI，用于分析辩论共识度

        # ============ API模式配置 ============
        self.api_mode_enabled = False               # 是否启用API模式
        self.api_provider = "custom"               # API提供方标识：siliconflow/deepseek/volcengine/custom
        self.api_base_url = "https://api.openai.com/v1"              # API基础地址（不含具体endpoint）
        self.api_url = "https://api.openai.com/v1/chat/completions"  # API服务地址（chat completions endpoint）
        self.api_key = ""                          # API密钥
        self.api_model = "gpt-3.5-turbo"           # API使用的模型名称
        self.model_1_use_api = False                # 模型1是否使用API
        self.model_2_use_api = False                # 模型2是否使用API
        self.coordinator_use_api = False            # 协调AI是否使用API
        # 每个AI独立的API配置（若为空则回退到全局配置）
        self.model_1_api_provider = ""
        self.model_1_api_base_url = ""
        self.model_1_api_url = ""
        self.model_1_api_key = ""
        self.model_1_api_model = ""

        self.model_2_api_provider = ""
        self.model_2_api_base_url = ""
        self.model_2_api_url = ""
        self.model_2_api_key = ""
        self.model_2_api_model = ""

        self.coordinator_api_provider = ""
        self.coordinator_api_base_url = ""
        self.coordinator_api_url = ""
        self.coordinator_api_key = ""
        self.coordinator_api_model = ""

        # ============ 提供方全局密钥（用于密钥记忆功能） ============
        self.siliconflow_api_key = ""               # 硅基流动API密钥
        self.deepseek_api_key = ""                  # DeepSeek API密钥
        self.volcengine_api_key = ""                # 火山引擎API密钥
        self.openai_api_key = ""                    # OpenAI API密钥
        self.xai_api_key = ""                       # xAI (Grok) API密钥
        self.gemini_api_key = ""                    # Google Gemini API密钥
        self.claude_api_key = ""                    # Anthropic Claude API密钥
        self.openrouter_api_key = ""                # OpenRouter API密钥

        # ============ AI模型生成参数 ============
        self.timeout = 90          # API请求超时时间(秒)，防止网络请求卡住
        self.max_tokens = 1000     # 单次生成的最大token数，控制回答长度
        self.temperature = 0.7     # 生成文本的随机性，0.0最保守，1.0最创造性

        # ============ 历史记录配置 ============
        self.save_history = True                    # 是否保存对话历史到文件
        self.history_file = "macp_history.json"     # 历史记录保存的文件路径

        # ============ 辩论模式核心配置 ============
        self.debate_rounds = 3                      # 默认辩论回合数，影响辩论深度
        self.auto_coordinate = True                 # 是否启用自动协调模式
        self.default_role_1 = "系统架构师"         # 默认第一个AI的辩论角色
        self.default_role_2 = "叙事导演"           # 默认第二个AI的辩论角色
        self.enable_tags = True                     # 是否启用智能标签检测功能
        self.allow_tag_override = False             # 是否允许标签检测结果覆盖用户角色选择
        self.display_length = 1000                  # 单个回答的最大显示字符数
        self.enable_early_stop = True               # 是否启用智能提前结束（基于共识度）
        self.consensus_threshold = 0.9              # 共识阈值，达到此值自动结束辩论（较高阈值避免过早结束）
        self.consensus_check_start_round = 2        # 从第几回合开始进行共识度检测
        self.ai_consensus_analysis = True           # 启用AI深度共识分析（而非简单关键词匹配）
        self.auto_summarize_at_threshold = True     # 达到共识阈值时自动生成总结报告
        self.coordination_mode = "auto"             # 协调模式：auto(自动)/user(用户手动)

        # ============ 性能和模式配置 ============
        self.optimize_memory = False                # 是否启用内存优化模式（实验性）
        self.turtle_soup_max_rounds = 10            # 海龟汤推理游戏的最大回合数
        self.streaming_output = True                # 是否启用流式输出

        # ============ 语言和界面配置 ============
        self.language = "zh"                        # 界面语言: "zh" 中文, "en" 英文

        # ============ 多AI辩论配置 ============
        # 额外的AI模型列表，用于多AI辩论
        # 格式: [{"name": "AI名称", "type": "ollama/api", "model": "模型名", "api_config": {...}}]
        self.extra_ai_models: List[Dict[str, Any]] = []

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            key: getattr(self, key)
            for key in dir(self)
            if not key.startswith('_') and not callable(getattr(self, key))
        }

    def update_from_dict(self, config_dict: Dict[str, Any]):
        """从字典更新配置"""
        for key, value in config_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def load_from_file(self, filepath: str):
        """从文件加载配置"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    self.update_from_dict(config_data)
            except (OSError, IOError, json.JSONDecodeError, ValueError) as e:
                logger.warning(f"加载配置文件失败: {e}")

    def save_to_file(self, filepath: str):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except (OSError, IOError, json.JSONDecodeError, ValueError) as e:
            logger.warning(f"保存配置文件失败: {e}")

# 配置文件路径（桌面）
CONFIG_FILE_PATH = r"C:\Users\yuangu114514\Desktop\macp_config.json"

# 创建全局配置实例，整个系统共享同一份配置
config = Config()

# 自动加载配置文件（如果存在）
if os.path.exists(CONFIG_FILE_PATH):
    try:
        config.load_from_file(CONFIG_FILE_PATH)
        print(f"✅ 已加载配置文件: {CONFIG_FILE_PATH}")
        # 同步语言设置到全局变量
        if hasattr(config, 'language') and config.language in ["zh", "en"]:
            CURRENT_LANGUAGE = config.language
    except Exception as e:
        print(f"⚠️ 加载配置文件失败: {e}")

# ==================== 【角色和标签系统】 ====================
# 定义AI辩论角色的提示词库和立场偏好系统

# 角色提示词库：包含9种专业角色，每种角色都有独特的辩论风格和立场偏好
# 辩论手特殊处理：第一个为正方（支持方），第二个为反方（反对方）
ROLE_PROMPTS: Dict[str, Dict[str, Any]] = {
    "系统架构师": {
        "prompt": """你是一名严谨的系统架构师，专注于可扩展性、平衡性、可维护性和玩家体验。
辩论风格：数据驱动，喜欢用具体例子证明观点。
回答格式：结构化分析，带有具体理由。""",
        "position_bias": "neutral",  # 中立立场
        "debate_style": "analytical"
    },

    "叙事导演": {
        "prompt": """你是一名富有创造力的叙事导演，专注于情感影响、故事融合、角色一致性和玩家代入感。
辩论风格：感性，喜欢用比喻和叙事证明观点。
回答格式：生动的描述，强调情感和故事性。""",
        "position_bias": "creative",  # 创意导向
        "debate_style": "narrative"
    },

    "数值策划": {
        "prompt": """你是一名精确的数值策划，专注于数学平衡、成长曲线、经济系统和概率设计。
辩论风格：严谨，喜欢用数据和公式说话。
回答格式：精确的数值分析，带有计算公式。""",
        "position_bias": "quantitative",  # 量化导向
        "debate_style": "mathematical"
    },

    "魔鬼代言人": {
        "prompt": """你专门挑刺，无论什么观点都找问题：逻辑漏洞、潜在风险、反向案例、质疑假设。
辩论风格：批判性，略带挑衅。
回答格式：先肯定对方，然后提出尖锐问题。""",
        "position_bias": "critical",  # 批判立场
        "debate_style": "skeptical"
    },

    "玩家代表": {
        "prompt": """你代表普通玩家，关注趣味性、易上手、成就感、挫败感。
辩论风格：直白，从玩家体验出发。
回答格式：直白的体验描述，带有具体感受。""",
        "position_bias": "user_centric",  # 用户中心
        "debate_style": "empathetic"
    },

    "项目经理": {
        "prompt": """你关注项目可行性，专注于开发成本、时间周期、技术风险、团队适配。
辩论风格：务实，关注实际限制。
回答格式：详细的实施计划，带有风险评估。""",
        "position_bias": "practical",  # 务实立场
        "debate_style": "pragmatic"
    },

    "律师": {
        "prompt": """你是一名专业的律师，专注于法律合规性、合同条款、风险管理、知识产权、隐私保护。
辩论风格：严谨，注重条款和案例引用。
回答格式：结构化的法律分析，引用相关法律原则。""",
        "position_bias": "legal",  # 法律立场
        "debate_style": "formal"
    },

    "哲学家": {
        "prompt": """你是一名深邃的哲学家，专注于伦理道德、逻辑一致性、价值观冲突、人性考量、长期影响。
辩论风格：思辨性，喜欢追问根本假设。
回答格式：深刻的哲学分析，带有伦理反思。""",
        "position_bias": "ethical",  # 伦理立场
        "debate_style": "philosophical"
    },

    "辩论手": {
        "prompt": """你是一名专业的辩论手，专注于：
1. 逻辑严谨性 - 论点是否逻辑严密？
2. 证据充分性 - 论据是否充分可靠？
3. 反驳有效性 - 反驳是否切中要害？
4. 策略灵活性 - 能否根据对方观点调整策略？

你的辩论风格：犀利，善于抓住对方逻辑漏洞，快速组织反驳。
你的回答格式：清晰的论点-论据-反驳结构，带有具体例子。

【辩论策略】：
- 第一回合：建立完整的论证框架
- 后续回合：针对性反驳，寻找对方逻辑漏洞
- 最后总结：强化核心论点，提出无可辩驳的结论""",
        "position_bias": "oppositional",  # 对立立场（第一个正方，第二个反方）
        "debate_style": "rhetorical"
    },

    # ========== 新增角色 ==========

    "朋友": {
        "prompt": """你是一位温暖、善解人意的朋友，专注于：
1. 情感支持 - 倾听对方的烦恼和心事
2. 共情理解 - 设身处地理解对方的感受
3. 温和建议 - 提供不带压力的建议
4. 陪伴安慰 - 让对方感到被理解和支持

你的交流风格：温暖亲切，像老朋友一样交谈，不说教、不评判。
你的回答格式：先表达理解和共情，再分享看法，最后给予鼓励。

【交流原则】：
- 先听后说，充分理解对方的感受
- 用"我理解"、"我明白"来表达共情
- 分享自己的看法时用"我觉得"而非"你应该"
- 尊重对方的选择，不强迫接受建议""",
        "position_bias": "supportive",  # 支持性立场
        "debate_style": "empathetic"
    },

    "专家": {
        "prompt": """你是一位知识渊博的百科全书式专家，专注于：
1. 事实准确性 - 提供准确、可靠的信息
2. 知识广度 - 涵盖各个领域的基础知识
3. 逻辑清晰 - 条理分明地解释复杂概念
4. 纠正错误 - 发现问题中的错误假设并纠正

你的交流风格：专业严谨，通俗易懂，注重准确性。
你的回答格式：先回答核心问题，再补充相关知识，必要时纠正错误。

【回答原则】：
- 遇到错误假设必须先指出并纠正
- 不确定的内容要明确说"我不确定"
- 用简单的语言解释专业概念
- 提供可靠的知识来源（如果有）""",
        "position_bias": "factual",  # 事实导向
        "debate_style": "educational"
    },

    "数学家": {
        "prompt": """你是一位严谨的数学家，专注于：
1. 数学推理 - 严密的逻辑推导和证明
2. 数值计算 - 精确的计算和估算
3. 问题建模 - 将实际问题转化为数学模型
4. 概念解释 - 用直观方式解释数学概念

你的交流风格：逻辑严密，步骤清晰，注重推导过程。
你的回答格式：
1. 理解问题
2. 建立数学模型
3. 推导/计算过程
4. 得出结论
5. 验证答案

【回答原则】：
- 每一步推导都要有理有据
- 计算过程要展示出来
- 遇到错误假设要先纠正
- 用多种方法验证结果的正确性""",
        "position_bias": "logical",  # 逻辑导向
        "debate_style": "deductive"
    },

    "物理学家": {
        "prompt": """你是一位专业的物理学家，专注于：
1. 物理原理 - 解释自然现象背后的物理定律
2. 科学思维 - 用科学方法分析问题
3. 实验验证 - 强调实验和观测的重要性
4. 概念澄清 - 纠正常见的物理误解

你的交流风格：科学严谨，深入浅出，善用类比。
你的回答格式：
1. 现象描述
2. 物理原理解释
3. 公式/定律应用（如适用）
4. 实例说明
5. 常见误区纠正

【回答原则】：
- 区分科学事实和假说
- 遇到违反物理定律的问题要指出
- 用日常生活例子解释抽象概念
- 承认科学的边界和未知领域""",
        "position_bias": "scientific",  # 科学导向
        "debate_style": "empirical"
    },

    "心理咨询师": {
        "prompt": """你是一位专业的心理咨询师，专注于：
1. 情绪识别 - 识别和理解情绪状态
2. 心理分析 - 分析行为背后的心理动机
3. 自我成长 - 提供自我提升的建议
4. 心理健康 - 普及心理健康知识

你的交流风格：温和专业，不评判，引导思考。
你的回答格式：先共情理解，再提供专业分析，最后给出建议。

【咨询原则】：
- 保持中立，不评判对方的感受和选择
- 引导对方自我觉察，而非直接给答案
- 区分日常烦恼和需要专业帮助的情况
- 必要时建议寻求专业心理帮助""",
        "position_bias": "therapeutic",  # 治疗性立场
        "debate_style": "reflective"
    },

    "历史学家": {
        "prompt": """你是一位博学的历史学家，专注于：
1. 历史事实 - 准确描述历史事件和人物
2. 历史背景 - 分析事件的时代背景
3. 因果关系 - 探讨历史事件的因果链
4. 历史教训 - 从历史中汲取智慧

你的交流风格：客观中立，引经据典，注重史实。
你的回答格式：
1. 历史背景介绍
2. 事件/人物描述
3. 因果分析
4. 历史意义和影响
5. 现代启示

【回答原则】：
- 区分历史事实和历史解读
- 引用可靠的历史文献
- 避免用现代标准评判古人
- 承认历史研究的不确定性""",
        "position_bias": "historical",  # 历史导向
        "debate_style": "contextual"
    },

    "程序员": {
        "prompt": """你是一位经验丰富的程序员，专注于：
1. 代码实现 - 提供清晰、高效的代码
2. 问题调试 - 分析和解决编程问题
3. 技术选型 - 推荐合适的技术方案
4. 最佳实践 - 分享编程最佳实践

你的交流风格：实用主义，代码优先，解释清晰。
你的回答格式：
1. 理解需求
2. 提供代码解决方案
3. 解释代码逻辑
4. 提供优化建议

【回答原则】：
- 代码要有注释
- 考虑边界情况和错误处理
- 推荐主流、稳定的技术
- 解释为什么这样写""",
        "position_bias": "technical",  # 技术导向
        "debate_style": "practical"
    }
}

# 从角色提示词库生成角色列表和数字映射
# 这些常量用于UI显示和用户输入处理
ROLE_LIST: List[str] = list(ROLE_PROMPTS.keys())  # 所有可用角色的有序列表
ROLE_NUM_MAP: Dict[str, str] = {str(i + 1): role for i, role in enumerate(ROLE_LIST)}  # 数字到角色的映射

# ============ 智能标签系统 ============
# 根据问题内容自动检测相关领域，并推荐合适的辩论角色

# 标签到角色的映射：每个专业领域对应最适合的辩论角色组合
TAG_TO_ROLES: Dict[str, List[str]] = {
    "机制设计": ["系统架构师", "数值策划", "玩家代表"],     # 游戏机制、系统设计相关
    "叙事设计": ["叙事导演", "玩家代表", "魔鬼代言人"],     # 故事剧情、叙事结构相关
    "平衡性": ["数值策划", "系统架构师", "魔鬼代言人"],     # 数值平衡、游戏平衡相关
    "创新性": ["魔鬼代言人", "叙事导演", "系统架构师"],     # 创意创新、新颖想法相关
    "可行性": ["系统架构师", "数值策划", "魔鬼代言人"],     # 项目可行性、技术实现相关
    "情感体验": ["叙事导演", "玩家代表", "朋友", "心理咨询师"],  # 情感体验、用户感受相关
    "技术实现": ["系统架构师", "项目经理", "程序员"],       # 技术实现、工程开发相关
    "用户体验": ["玩家代表", "叙事导演", "系统架构师"],     # 用户界面、交互体验相关
    "法律合规": ["律师", "项目经理", "魔鬼代言人"],         # 法律合规、知识产权相关
    "伦理道德": ["哲学家", "律师", "魔鬼代言人"],           # 伦理道德、价值观相关
    "辩论技巧": ["辩论手", "律师", "魔鬼代言人"],           # 辩论技巧、论证逻辑相关
    # 新增标签
    "数学问题": ["数学家", "专家", "魔鬼代言人"],           # 数学计算、逻辑推理相关
    "物理问题": ["物理学家", "专家", "数学家"],             # 物理现象、科学原理相关
    "科学知识": ["专家", "物理学家", "数学家"],             # 通用科学知识问题
    "历史问题": ["历史学家", "哲学家", "专家"],             # 历史事件、人物相关
    "情感倾诉": ["朋友", "心理咨询师", "哲学家"],           # 情感问题、心事倾诉
    "心理健康": ["心理咨询师", "朋友", "哲学家"],           # 心理问题、情绪困扰
    "编程问题": ["程序员", "系统架构师", "专家"]            # 编程代码、技术问题
}

# 标签关键词映射：用于从用户问题中检测相关领域的关键词
TAG_KEYWORDS: Dict[str, List[str]] = {
    "机制设计": ["机制", "系统", "设计", "功能", "玩法", "规则"],
    "叙事设计": ["故事", "剧情", "叙事", "角色", "世界观", "情节"],
    "平衡性": ["平衡", "数值", "难度", "强度", "调整", "公平"],
    "创新性": ["创新", "新颖", "独特", "创意", "新意", "原创"],
    "可行性": ["实现", "开发", "成本", "时间", "技术", "资源"],
    "情感体验": ["情感", "感受", "体验", "代入", "沉浸", "感动"],
    "技术实现": ["技术", "实现", "代码", "引擎", "性能", "优化"],
    "用户体验": ["用户", "玩家", "体验", "操作", "界面", "流畅"],
    "法律合规": ["法律", "合规", "合同", "条款", "风险", "知识产权"],
    "伦理道德": ["伦理", "道德", "价值观", "人性", "尊严", "自由"],
    "辩论技巧": ["辩论", "争论", "讨论", "反驳", "论证", "逻辑"],
    # 新增标签关键词
    "数学问题": ["数学", "计算", "公式", "方程", "几何", "代数", "微积分", "统计", "概率", "证明", "求解"],
    "物理问题": ["物理", "力学", "电磁", "光学", "热力学", "量子", "相对论", "能量", "动量", "波动"],
    "科学知识": ["科学", "科普", "原理", "定律", "实验", "研究", "发现", "自然"],
    "历史问题": ["历史", "朝代", "古代", "近代", "战争", "帝国", "文明", "事件", "人物", "年代"],
    "情感倾诉": ["烦恼", "难过", "伤心", "困惑", "纠结", "郁闷", "心情", "倾诉", "聊聊", "心事", "感情"],
    "心理健康": ["焦虑", "抑郁", "压力", "失眠", "情绪", "心理", "精神", "恐惧", "紧张"],
    "编程问题": ["编程", "代码", "程序", "bug", "错误", "函数", "变量", "算法", "python", "java", "javascript"]
}

# ============ 问题类型分类系统 ============
# 用于判断问题是否需要高准确度（事实类）还是允许主观讨论（哲学/叙事类）

# 事实准确类问题的关键词（这类问题需要AI纠正错误，不能有幻觉）
FACTUAL_KEYWORDS: List[str] = [
    # 科学事实
    "是什么", "有没有", "有多少", "多大", "多长", "多重", "多远",
    "几个", "几种", "什么时候", "什么地方", "谁发明", "谁发现",
    "是真的吗", "正确吗", "对不对", "存在吗", "能不能",
    # 动物/生物
    "动物", "植物", "生物", "细胞", "器官", "身体", "羽毛", "翅膀", "爪子", "毛发",
    "哺乳动物", "鸟类", "鱼类", "昆虫", "爬行动物",
    # 科学领域
    "物理", "化学", "生物学", "数学", "地理", "天文", "医学",
    "科学", "实验", "公式", "定理", "定律", "原理",
    # 历史/地理
    "历史", "朝代", "年代", "事件", "人物", "国家", "城市", "首都",
    # 常识
    "颜色", "形状", "大小", "重量", "温度", "速度", "距离"
]

# 主观/哲学类问题的关键词（这类问题允许开放讨论）
PHILOSOPHICAL_KEYWORDS: List[str] = [
    # 哲学
    "人生", "意义", "目的", "本质", "存在", "自由意志", "命运",
    "善恶", "对错", "价值", "美", "真理", "幸福", "爱",
    # 思辨
    "应该", "是否应该", "值得", "更好", "最好", "如何看待",
    "怎么看", "你认为", "你觉得", "看法", "观点", "立场",
    # 假设性
    "如果", "假如", "假设", "可能", "或许", "也许",
    # 辩论性
    "支持", "反对", "利弊", "优缺点", "好坏", "争议"
]

def analyze_question_type(question: str) -> Dict[str, Any]:
    """分析问题类型，判断是否需要高准确度
    
    Returns:
        {
            "type": "factual" | "philosophical" | "mixed",
            "accuracy_required": True/False,
            "confidence": 0.0-1.0,
            "detected_factual_keywords": [...],
            "detected_philosophical_keywords": [...]
        }
    """
    question_lower = question.lower()
    
    # 检测事实类关键词
    factual_hits = [kw for kw in FACTUAL_KEYWORDS if kw in question_lower]
    # 检测哲学类关键词
    philosophical_hits = [kw for kw in PHILOSOPHICAL_KEYWORDS if kw in question_lower]
    
    factual_score = len(factual_hits)
    philosophical_score = len(philosophical_hits)
    
    # 判断问题类型
    if factual_score > philosophical_score * 2:
        question_type = "factual"
        accuracy_required = True
        confidence = min(1.0, factual_score / 3)
    elif philosophical_score > factual_score * 2:
        question_type = "philosophical"
        accuracy_required = False
        confidence = min(1.0, philosophical_score / 3)
    else:
        question_type = "mixed"
        accuracy_required = factual_score >= philosophical_score
        confidence = 0.5
    
    return {
        "type": question_type,
        "accuracy_required": accuracy_required,
        "confidence": confidence,
        "detected_factual_keywords": factual_hits,
        "detected_philosophical_keywords": philosophical_hits
    }

# 防幻觉提示词（中文）
ANTI_HALLUCINATION_PROMPT_ZH = """
【重要：防止幻觉指令】
1. 如果问题本身包含错误的假设或事实错误，你必须首先指出并纠正这个错误，而不是顺着错误继续回答。
2. 例如：如果用户问"猫的羽毛是什么颜色"，你必须指出"猫没有羽毛，猫有的是毛发"，然后再讨论相关话题。
3. 对于事实性问题，如果你不确定答案，请明确说"我不确定"或"我需要查证"，而不是编造答案。
4. 保持逻辑严谨，不要为了辩论而忽视基本事实。
5. 事实优先于立场：即使你的角色需要辩护某个观点，也不能歪曲基本事实。
"""

# 防幻觉提示词（英文）
ANTI_HALLUCINATION_PROMPT_EN = """
【IMPORTANT: Anti-Hallucination Instructions】
1. If the question itself contains false assumptions or factual errors, you MUST first point out and correct this error, rather than answering based on the false premise.
2. Example: If user asks "What color is a cat's feathers?", you MUST point out "Cats don't have feathers, cats have fur", then discuss the relevant topic.
3. For factual questions, if you're unsure about the answer, clearly state "I'm not sure" or "I need to verify", rather than making up an answer.
4. Maintain logical rigor, don't ignore basic facts for the sake of debate.
5. Facts over position: Even if your role requires defending a viewpoint, you cannot distort basic facts.
"""

# 哲学讨论提示词（中文）
PHILOSOPHICAL_PROMPT_ZH = """
【讨论模式：开放思辨】
这是一个开放性的哲学/思辨问题，没有绝对的对错答案。
1. 你可以自由表达你的观点和论证。
2. 重点在于论证的逻辑性和深度，而非寻找"正确答案"。
3. 但仍需保持基本的逻辑自洽，不要自相矛盾。
4. 尊重不同观点，用理性论证而非情绪化表达。
"""

# 哲学讨论提示词（英文）
PHILOSOPHICAL_PROMPT_EN = """
【Discussion Mode: Open Speculation】
This is an open philosophical/speculative question with no absolute right or wrong answer.
1. You can freely express your viewpoints and arguments.
2. Focus on the logic and depth of argumentation, rather than finding "the correct answer".
3. But still maintain basic logical consistency, don't contradict yourself.
4. Respect different viewpoints, use rational argumentation rather than emotional expression.
"""

class RoleSystem:
    """AI辩论角色系统管理器

    管理MACP系统中所有AI角色的配置和行为：
    - 角色提示词生成和管理
    - 立场偏好设置（尤其是辩论手的正反方机制）
    - 用户输入的角色名称纠错
    - 智能标签检测和角色推荐

    核心特性：
    - 辩论手自动立场分配：第一个为正方，第二个为反方
    - 拼写容错：自动纠正常见的角色名称输入错误
    - 动态提示词：根据辩论位置生成不同的立场提示
    """

    # 常见角色名称拼写错误映射表，用于输入容错处理
    COMMON_TYPOS = {
        "叙述导演": "叙事导演",
        "系统框架师": "系统架构师",
        "魔鬼代言人": "魔鬼代言人",  # 这几个其实没有错误，但保留以防扩展
        "玩家代表": "玩家代表",
        "数值策划": "数值策划",
        "项目经理": "项目经理",
        "律师": "律师",
        "哲学家": "哲学家",
        "法律顾问": "律师",
        "哲学思考者": "哲学家",
        "辩论者": "辩论手",
        "辩手": "辩论手",
        # 新增角色的别名
        "好友": "朋友",
        "闺蜜": "朋友",
        "知己": "朋友",
        "百科": "专家",
        "百科全书": "专家",
        "知识专家": "专家",
        "数学专家": "数学家",
        "物理专家": "物理学家",
        "物理老师": "物理学家",
        "心理医生": "心理咨询师",
        "心理专家": "心理咨询师",
        "咨询师": "心理咨询师",
        "史学家": "历史学家",
        "历史专家": "历史学家",
        "历史老师": "历史学家",
        "开发者": "程序员",
        "码农": "程序员",
        "工程师": "程序员",
        "软件工程师": "程序员"
    }

    def __init__(self):
        pass

    @staticmethod
    def get_role_prompt(role_name: str, is_first: bool = True) -> Optional[str]:
        """获取角色提示词，支持辩论立场调整"""
        corrected_role = RoleSystem.COMMON_TYPOS.get(role_name, role_name)
        role_data = ROLE_PROMPTS.get(corrected_role)

        if not role_data:
            return None

        # 如果是字符串格式（向后兼容），直接返回
        if isinstance(role_data, str):
            return role_data

        base_prompt = role_data["prompt"]
        # position_bias = role_data.get("position_bias", "neutral")  # 保留以备将来扩展使用

        # 特殊处理辩论手：第一个是正方，第二个是反方
        if corrected_role == "辩论手":
            if is_first:
                position_addition = """

【你的立场】：你作为正方（支持方），需要为命题建立积极的论点，证明其合理性和价值。你将使用经典辩论技巧来构建完整的论证框架。"""
            else:
                position_addition = """

【你的立场】：你作为反方（反对方），需要质疑命题的合理性，寻找逻辑漏洞和反例。你将使用批判性思维来反驳对方的观点。"""
            return base_prompt + position_addition

        # 其他角色保持原有逻辑，但可以根据需要添加立场偏好
        return base_prompt

    @staticmethod
    def get_all_roles() -> List[str]:
        """获取所有可用角色"""
        return ROLE_LIST.copy()

    @staticmethod
    def get_role_by_number(number: str) -> Optional[str]:
        """通过数字获取角色"""
        return ROLE_NUM_MAP.get(number)

    @staticmethod
    def detect_tags(question: str) -> List[str]:
        """从问题中检测标签"""
        tags_with_weights = {}
        question_lower = question.lower()

        for tag, keywords in TAG_KEYWORDS.items():
            weight = sum(2 for keyword in keywords if keyword in question_lower)
            if weight > 0:
                tags_with_weights[tag] = weight

        sorted_tags = sorted(tags_with_weights.items(), key=lambda x: x[1], reverse=True)
        return [tag for tag, _ in sorted_tags[:3]]

    @staticmethod
    def get_roles_for_tags(tags: List[str]) -> List[str]:
        """根据标签获取推荐角色"""
        recommended_roles = set()
        for tag in tags:
            if tag in TAG_TO_ROLES:
                recommended_roles.update(TAG_TO_ROLES[tag])
        return list(recommended_roles)

# 创建全局角色系统实例，管理所有AI角色的配置和行为
role_system = RoleSystem()

# ==================== 【Ollama API客户端】 ====================
# 与Ollama服务通信的核心接口

class OllamaClient:
    """Ollama本地AI服务客户端

    封装Ollama REST API的所有操作：
    - 服务连接检查
    - 模型列表获取
    - 文本生成功能
    - 错误处理和重试机制

    提供统一的接口给上层应用使用，屏蔽底层的HTTP通信细节
    """

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 10  # 默认超时时间

    def check_service(self) -> bool:
        """检查Ollama服务是否运行"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                logger.info("✅ Ollama服务运行正常")
                return True
            else:
                logger.warning(f"⚠️  Ollama服务异常，状态码: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            raise OllamaConnectionError(f"无法连接到Ollama服务: {self.base_url}")
        except Exception as e:
            logger.error(f"检查Ollama服务时发生错误: {e}")
            return False

    def list_models(self) -> List[str]:
        """获取可用模型列表"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model["name"] for model in data.get("models", [])]
            else:
                logger.warning(f"获取模型列表失败，状态码: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取模型列表时发生错误: {e}")
            return []

    def check_models(self, required_models: List[str]) -> Dict[str, bool]:
        """检查所需模型是否可用"""
        available_models = self.list_models()
        results = {}

        logger.info("📦 检查模型可用性:")
        for model in required_models:
            available = model in available_models
            results[model] = available
            status = "✅" if available else "❌"
            logger.info(f"   {status} {model}")

        return results

    def generate_response(self,
                         model: str,
                         prompt: str,
                         max_tokens: Optional[int] = None,
                         temperature: float = 0.7,
                         timeout: int = 90,
                         streaming: bool = False) -> Dict[str, Any]:
        """生成模型响应

        Args:
            model: 模型名称
            prompt: 提示文本
            max_tokens: 最大token数
            temperature: 温度参数
            timeout: 超时时间
            streaming: 是否启用流式输出

        Returns:
            响应字典
        """
        if streaming:
            return self._generate_streaming_response(model, prompt, max_tokens, temperature, timeout)
        else:
            return self._generate_non_streaming_response(model, prompt, max_tokens, temperature, timeout)

    def _generate_non_streaming_response(self,
                                        model: str,
                                        prompt: str,
                                        max_tokens: Optional[int] = None,
                                        temperature: float = 0.7,
                                        timeout: int = 90) -> Dict[str, Any]:
        """生成非流式模型响应"""
        start_time = time.time()

        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature
                }
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout
            )

            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "model": model,
                    "response": result.get("response", ""),
                    "time": elapsed_time,
                    "tokens": result.get("total_duration", 0),
                    "eval_count": result.get("eval_count", 0),
                    "eval_duration": result.get("eval_duration", 0)
                }
            else:
                return {
                    "success": False,
                    "model": model,
                    "response": f"请求失败，状态码: {response.status_code}",
                    "time": elapsed_time,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"非流式响应出错: {e}")
            return {
                "success": False,
                "model": model,
                "response": f"响应出错: {str(e)}",
                "time": elapsed_time,
                "error": str(e)
            }

    def _generate_streaming_response(self,
                                    model: str,
                                    prompt: str,
                                    max_tokens: Optional[int] = None,
                                    temperature: float = 0.7,
                                    timeout: int = 90,
                                    speaker_name: Optional[str] = None,
                                    response_type: str = "") -> Dict[str, Any]:
        """生成流式模型响应
        
        Args:
            model: 模型名称
            prompt: 提示词
            max_tokens: 最大token数
            temperature: 温度参数
            timeout: 超时时间
            speaker_name: 发言者名称（用于辩论模式显示）
            response_type: 响应类型（如"反驳xxx"）
        """
        start_time = time.time()
        full_response = ""
        total_tokens = 0
        eval_count = 0
        eval_duration = 0

        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": True,
                "options": {
                    "temperature": temperature
                }
            }

            if max_tokens:
                payload["options"]["num_predict"] = max_tokens

            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout,
                stream=True
            )

            if response.status_code != 200:
                elapsed_time = time.time() - start_time
                return {
                    "success": False,
                    "model": model,
                    "response": f"请求失败，状态码: {response.status_code}",
                    "time": elapsed_time,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text
                }

            # 处理流式响应 - 显示发言者名称
            if speaker_name:
                type_prefix = f" {response_type}：" if response_type else "："
                print(f"\n📢 {speaker_name}{type_prefix}", flush=True)
            else:
                print(f"🤖 {model}：", end="", flush=True)

            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str:
                        try:
                            chunk = json.loads(line_str)

                            # 提取响应内容
                            if "response" in chunk:
                                chunk_text = chunk["response"]
                                if chunk_text:
                                    print(chunk_text, end="", flush=True)
                                    full_response += chunk_text

                            # 收集统计信息
                            if "total_duration" in chunk:
                                total_tokens = chunk["total_duration"]
                            if "eval_count" in chunk:
                                eval_count = chunk["eval_count"]
                            if "eval_duration" in chunk:
                                eval_duration = chunk["eval_duration"]

                            # 检查是否完成
                            if chunk.get("done", False):
                                break

                        except json.JSONDecodeError:
                            continue

            print()  # 换行
            elapsed_time = time.time() - start_time

            return {
                "success": True,
                "model": model,
                "response": full_response,
                "time": elapsed_time,
                "tokens": total_tokens,
                "eval_count": eval_count,
                "eval_duration": eval_duration
            }

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"流式响应出错: {e}")
            return {
                "success": False,
                "model": model,
                "response": f"流式响应出错: {str(e)}",
                "time": elapsed_time,
                "error": str(e)
            }

        except requests.exceptions.Timeout:
            elapsed_time = time.time() - start_time
            return {
                "success": False,
                "model": model,
                "response": "（请求超时）",
                "time": elapsed_time,
                "error": "timeout"
            }

        except requests.exceptions.ConnectionError:
            elapsed_time = time.time() - start_time
            return {
                "success": False,
                "model": model,
                "response": "（连接错误）",
                "time": elapsed_time,
                "error": "connection_error"
            }

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"生成响应时发生错误: {e}", exc_info=e)
            return {
                "success": False,
                "model": model,
                "response": f"（请求错误: {str(e)}）",
                "time": elapsed_time,
                "error": str(e)
            }

    def get_running_models(self) -> List[Dict[str, Any]]:
        """获取正在运行的模型"""
        try:
            response = self.session.get(f"{self.base_url}/api/ps", timeout=10)
            if response.status_code == 200:
                return response.json().get("models", [])
            else:
                logger.warning(f"获取运行中模型失败，状态码: {response.status_code}")
                return []
        except Exception as e:
            logger.error(f"获取运行中模型时发生错误: {e}")
            return []

# ==================== 【API客户端】 ====================
# 支持外部API服务的客户端，用于混合使用Ollama和API模型

class APIClient:
    """外部API服务客户端

    支持OpenAI格式的API调用，提供统一的接口来调用外部AI服务。
    可以与Ollama模型混合使用，每个API模型都是独立的实例。
    """

    def __init__(self, api_url: str, api_key: str, model_name: str, timeout: int = 90):
        """初始化API客户端

        Args:
            api_url: API服务地址
            api_key: API密钥
            model_name: API使用的模型名称
            timeout: 请求超时时间
        """
        self.api_url = api_url
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.session = requests.Session()

        # 设置请求头
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        })

    @staticmethod
    def _infer_base_url(api_url: str) -> str:
        """从 chat completions URL 推断 base url（用于 /models 等接口）"""
        url = (api_url or "").rstrip("/")
        for suffix in ("/chat/completions",):
            if url.endswith(suffix):
                return url[: -len(suffix)]
        # 已经是 base 的情况
        if url.endswith("/v1") or url.endswith("/api/v3") or url.endswith("/api/v3/"):
            return url.rstrip("/")
        return url

    def list_models(self) -> List[str]:
        """获取该 API 提供方可用模型列表（若不支持则返回空列表）"""
        try:
            base_url = APIClient._infer_base_url(self.api_url)
            resp = self.session.get(f"{base_url}/models", timeout=15)
            if resp.status_code != 200:
                return []
            data = resp.json()
            # OpenAI 兼容：{"data":[{"id":"xxx"}, ...]}
            models = []
            for item in data.get("data", []):
                model_id = item.get("id")
                if model_id:
                    models.append(model_id)
            return models
        except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError):
            return []

    def check_connection(self) -> bool:
        """检查API连接是否可用"""
        try:
            # 发送一个简单的测试请求
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            response = self.session.post(self.api_url, json=payload, timeout=10)
            return response.status_code == 200
        except (requests.exceptions.RequestException, ValueError) as e:
            logger.error(f"API连接检查失败: {e}")
            return False

    def generate_response(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7,
                         streaming: bool = False, speaker_name: Optional[str] = None, 
                         response_type: str = "") -> Dict[str, Any]:
        """生成AI响应

        Args:
            prompt: 提示词
            max_tokens: 最大token数
            temperature: 温度参数
            streaming: 是否使用流式输出
            speaker_name: 发言者名称（用于流式输出显示）
            response_type: 响应类型（如"反驳xxx"）

        Returns:
            包含响应信息的字典
        """
        if streaming:
            return self._generate_streaming_response(prompt, max_tokens, temperature, 
                                                    speaker_name, response_type)
        
        start_time = time.time()

        try:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False
            }

            response = self.session.post(self.api_url, json=payload, timeout=self.timeout)

            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")

                elapsed_time = time.time() - start_time
                return {
                    "success": True,
                    "model": f"API-{self.model_name}",
                    "response": content,
                    "time": elapsed_time
                }
            else:
                elapsed_time = time.time() - start_time
                error_msg = f"API请求失败，状态码: {response.status_code}"
                try:
                    error_detail = response.json()
                    error_msg += f"，详情: {error_detail}"
                except:
                    pass

                return {
                    "success": False,
                    "model": f"API-{self.model_name}",
                    "response": f"（{error_msg}）",
                    "time": elapsed_time,
                    "error": error_msg
                }

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"API生成响应时发生错误: {e}")
            return {
                "success": False,
                "model": f"API-{self.model_name}",
                "response": f"（API请求错误: {str(e)}）",
                "time": elapsed_time,
                "error": str(e)
            }

    def _generate_streaming_response(self, prompt: str, max_tokens: int = 1000, 
                                    temperature: float = 0.7,
                                    speaker_name: Optional[str] = None,
                                    response_type: str = "") -> Dict[str, Any]:
        """生成流式AI响应（真正的逐字输出）
        
        Args:
            prompt: 提示词
            max_tokens: 最大token数
            temperature: 温度参数
            speaker_name: 发言者名称
            response_type: 响应类型
        """
        start_time = time.time()
        full_response = ""

        try:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": True
            }

            response = self.session.post(self.api_url, json=payload, timeout=self.timeout, stream=True)

            if response.status_code != 200:
                elapsed_time = time.time() - start_time
                error_msg = f"API请求失败，状态码: {response.status_code}"
                return {
                    "success": False,
                    "model": f"API-{self.model_name}",
                    "response": f"（{error_msg}）",
                    "time": elapsed_time,
                    "error": error_msg
                }

            # 显示发言者名称
            if speaker_name:
                type_prefix = f" {response_type}：" if response_type else "："
                print(f"\n📢 {speaker_name}{type_prefix}", flush=True)
            else:
                print(f"🤖 API-{self.model_name}：", end="", flush=True)

            # 处理流式响应 (SSE格式)
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith("data: "):
                        data_str = line_str[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                print(content, end="", flush=True)
                                full_response += content
                        except json.JSONDecodeError:
                            continue

            print()  # 换行
            elapsed_time = time.time() - start_time

            return {
                "success": True,
                "model": f"API-{self.model_name}",
                "response": full_response,
                "time": elapsed_time
            }

        except Exception as e:
            elapsed_time = time.time() - start_time
            logger.error(f"API流式响应出错: {e}")
            return {
                "success": False,
                "model": f"API-{self.model_name}",
                "response": f"（API流式请求错误: {str(e)}）",
                "time": elapsed_time,
                "error": str(e)
            }

# ==================== 【核心调度器】 ====================
# MACP系统的核心业务逻辑控制器

class AICouncilScheduler:
    """多AI协作调度器核心类

    统筹管理整个MACP系统的运行：
    - 初始化系统和检查依赖
    - 协调多个AI模型的协作
    - 管理辩论流程和共识检测
    - 处理历史记录和性能监控

    这是系统的"大脑"，负责所有业务逻辑的编排和执行
    """

    def __init__(self):
        self.config = config
        self.client = OllamaClient(self.config.ollama_url)
        # 按模型分别维护API客户端
        self.api_client = None  # 兼容旧字段，不再实际使用
        self.api_client_model1: Optional[APIClient] = None
        self.api_client_model2: Optional[APIClient] = None
        self.api_client_coordinator: Optional[APIClient] = None
        self.history_manager = HistoryManager(self.config.history_file)
        self.progress_tracker = ProgressTracker()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 初始化检查
        self._initialize()

    def _initialize(self):
        """初始化调度器"""
        try:
            logger.info("🚀 初始化MACP调度器...")

            # 检查Ollama服务（如果需要的话）
            if not self.config.api_mode_enabled or not (self.config.model_1_use_api and self.config.model_2_use_api and self.config.coordinator_use_api):
                if not self.client.check_service():
                    logger.warning("Ollama服务不可用，将仅使用API模式")
                else:
                    # 检查Ollama所需模型
                    required_models = []
                    if not self.config.model_1_use_api:
                        required_models.append(self.config.model_1)
                    if not self.config.model_2_use_api:
                        required_models.append(self.config.model_2)
                    if not self.config.coordinator_use_api:
                        required_models.append(self.config.coordinator_model)

                    if required_models:
                        model_status = self.client.check_models(required_models)
                        missing_models = [model for model, available in model_status.items() if not available]
                        if missing_models:
                            logger.warning(f"Ollama缺少模型: {', '.join(missing_models)}，将尝试使用API替代")

            # 初始化API客户端（如果启用了API模式）
            if self.config.api_mode_enabled:
                self._initialize_api_client()

            logger.info("✅ 初始化完成")

        except Exception as e:
            logger.error(f"初始化失败: {e}")
            raise

    def _initialize_api_client(self):
        """初始化API客户端（按模型分别初始化）"""

        def create_client(api_url: str, api_key: str, api_model: str) -> Optional[APIClient]:
            api_url = (api_url or "").strip()
            api_key = (api_key or "").strip()
            api_model = (api_model or "").strip()
            if not api_url or not api_key or not api_model:
                return None
            client = APIClient(
                api_url=api_url,
                api_key=api_key,
                model_name=api_model,
                timeout=self.config.timeout
            )
            # 仅做一次简单连通性检查，不强制失败
            if client.check_connection():
                logger.info(f"✅ API客户端已就绪: {api_model}")
            else:
                logger.warning(f"⚠️ API客户端连接检查失败: {api_model}")
            return client

        # 模型1
        if self.config.model_1_use_api:
            url = getattr(self.config, "model_1_api_url", "") or self.config.api_url
            key = getattr(self.config, "model_1_api_key", "") or self.config.api_key
            model = getattr(self.config, "model_1_api_model", "") or self.config.api_model
            self.api_client_model1 = create_client(url, key, model)
        else:
            self.api_client_model1 = None

        # 模型2
        if self.config.model_2_use_api:
            url = getattr(self.config, "model_2_api_url", "") or self.config.api_url
            key = getattr(self.config, "model_2_api_key", "") or self.config.api_key
            model = getattr(self.config, "model_2_api_model", "") or self.config.api_model
            self.api_client_model2 = create_client(url, key, model)
        else:
            self.api_client_model2 = None

        # 协调AI
        if self.config.coordinator_use_api:
            url = getattr(self.config, "coordinator_api_url", "") or self.config.api_url
            key = getattr(self.config, "coordinator_api_key", "") or self.config.api_key
            model = getattr(self.config, "coordinator_api_model", "") or self.config.api_model
            self.api_client_coordinator = create_client(url, key, model)
        else:
            self.api_client_coordinator = None

        if not any([self.api_client_model1, self.api_client_model2, self.api_client_coordinator]):
            logger.warning("API模式已启用，但未成功初始化任何API客户端，请检查配置")

    def _get_client_for_model(self, model_name: str) -> tuple:
        """根据模型名称返回对应的客户端和模型标识

        Returns:
            (client, model_identifier, is_api_client) 元组
        """
        if not self.config.api_mode_enabled:
            return self.client, model_name, False

        if model_name == self.config.model_1 and self.config.model_1_use_api and self.api_client_model1:
            api_model = getattr(self.config, "model_1_api_model", "") or self.config.api_model
            return self.api_client_model1, f"API-{api_model}", True
        elif model_name == self.config.model_2 and self.config.model_2_use_api and self.api_client_model2:
            api_model = getattr(self.config, "model_2_api_model", "") or self.config.api_model
            return self.api_client_model2, f"API-{api_model}", True
        elif model_name == self.config.coordinator_model and self.config.coordinator_use_api and self.api_client_coordinator:
            api_model = getattr(self.config, "coordinator_api_model", "") or self.config.api_model
            return self.api_client_coordinator, f"API-{api_model}", True
        else:
            return self.client, model_name, False

    # ==================== 【核心方法】 ====================
    def ask_both_models(self, question: str, mode: str = "parallel",
                       role1: Optional[str] = None, role2: Optional[str] = None) -> List[Dict[str, Any]]:
        """向两个模型提问（支持多种模式）"""
        DisplayManager.print_header("🧠 问题处理")
        print(f"问题: {question}")
        print(f"模式: {mode}")
        DisplayManager.print_separator()

        self.progress_tracker.start()

        try:
            if mode == "parallel":
                return self._parallel_ask(question)
            elif mode == "debate":
                return self._debate_ask(question, role1, role2)
            elif mode == "turtle_soup":
                return self._turtle_soup_ask(question, role1, role2)
            else:
                raise ValueError(f"未知模式: {mode}")
        except Exception as e:
            logger.error(f"处理问题时发生错误: {e}")
            return []

    def _parallel_ask(self, question: str) -> List[Dict[str, Any]]:
        """并行提问逻辑（支持API模式）"""
        logger.info("开始并行提问")

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_model = {}

            # 模型1
            if self.config.api_mode_enabled and self.config.model_1_use_api and self.api_client_model1:
                future_to_model[executor.submit(self.api_client_model1.generate_response,
                                              question, self.config.max_tokens, self.config.temperature)] = f"API-{getattr(self.config, 'model_1_api_model', '') or self.config.api_model}"
            else:
                future_to_model[executor.submit(self.client.generate_response,
                                              self.config.model_1, question,
                                              self.config.max_tokens, self.config.temperature,
                                              self.config.timeout)] = self.config.model_1

            # 模型2
            if self.config.api_mode_enabled and self.config.model_2_use_api and self.api_client_model2:
                future_to_model[executor.submit(self.api_client_model2.generate_response,
                                              question, self.config.max_tokens, self.config.temperature)] = f"API-{getattr(self.config, 'model_2_api_model', '') or self.config.api_model}"
            else:
                future_to_model[executor.submit(self.client.generate_response,
                                              self.config.model_2, question,
                                              self.config.max_tokens, self.config.temperature,
                                              self.config.timeout)] = self.config.model_2

            results = []
            for future in concurrent.futures.as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    result = future.result()
                    results.append(result)
                    self.progress_tracker.update()
                except Exception as e:
                    logger.error(f"模型 {model_name} 执行错误: {e}")
                    results.append({
                        "success": False,
                        "model": model_name,
                        "error": f"执行错误: {str(e)}",
                        "time": 0
                    })

        self._display_results(results)

        if self.config.save_history:
            self._save_history_entry(question, results, mode="parallel")

        return results

    # ==================== 【辩论模式】 ====================
    def _debate_ask(self, question: str, role1: Optional[str] = None, role2: Optional[str] = None) -> List[Dict[str, Any]]:
        """执行多回合AI辩论 - 增强版

        这是MACP系统的核心功能，实现两个AI模型之间的辩论：
        1. 初始化辩论角色（支持正反方立场）
        2. 进行多回合辩论对话，双方可以看到完整上下文
        3. 实时AI共识度分析和监控
        4. 达到阈值时自动结束并生成总结

        Args:
            question: 辩论主题问题
            role1: 第一个AI的角色（默认为正方）
            role2: 第二个AI的角色（默认为反方）

        Returns:
            包含两个AI响应的结果列表
        """
        # 确定角色
        role1 = role1 or self.config.default_role_1
        role2 = role2 or self.config.default_role_2

        # 先获取客户端，确定实际使用的模型名（本地或API）
        client1, model_id1, is_api1 = self._get_client_for_model(self.config.model_1)
        client2, model_id2, is_api2 = self._get_client_for_model(self.config.model_2)

        # 构造显示名：使用实际模型名（如果是API则显示API模型名）
        actual_model1 = model_id1 if is_api1 else self.config.model_1
        actual_model2 = model_id2 if is_api2 else self.config.model_2
        display_name1 = f"{actual_model1}-{role1}"
        display_name2 = f"{actual_model2}-{role2}"

        role_prompt1 = role_system.get_role_prompt(role1, is_first=True)   # 正方
        role_prompt2 = role_system.get_role_prompt(role2, is_first=False)  # 反方

        if not role_prompt1 or not role_prompt2:
            raise InvalidRoleError(f"无效角色: {role1} 或 {role2}")

        self._setup_debate_roles(question, role1, role2)

        # 分析问题类型，决定是否需要高准确度
        question_analysis = analyze_question_type(question)
        accuracy_required = question_analysis["accuracy_required"]
        question_type = question_analysis["type"]
        
        # 显示问题类型分析
        type_labels = {
            "factual": "事实类/Factual（高准确度/High Accuracy）", 
            "philosophical": "哲学类/Philosophical（开放讨论/Open Discussion）", 
            "mixed": "混合类/Mixed"
        }
        print(f"🔍 问题类型 (Question Type): {type_labels.get(question_type, question_type)}")
        if accuracy_required:
            print("⚠️ 准确度模式 (Accuracy Mode): AI会纠正问题中的事实错误 (AI will correct factual errors)")

        # 第一回合：双方知道对手是谁，但看不到具体观点
        DisplayManager.print_separator("-", 40)
        print("第1回合：初始陈述 (Round 1: Opening Statement)")
        DisplayManager.print_separator("-", 40)
        print(f"💡 {role1} vs {role2} - 双方已知晓对手身份 (Both sides know opponent)")
        if is_api1 or is_api2:
            print(f"🌐 使用模型 (Using models): {actual_model1} | {actual_model2}")

        # 根据问题类型选择附加提示词
        if CURRENT_LANGUAGE == "en":
            mode_instruction = ANTI_HALLUCINATION_PROMPT_EN if accuracy_required else PHILOSOPHICAL_PROMPT_EN
        else:
            mode_instruction = ANTI_HALLUCINATION_PROMPT_ZH if accuracy_required else PHILOSOPHICAL_PROMPT_ZH

        # 增强版第一回合提示词 - 让AI知道对手是谁，并要求简洁表达
        # 根据当前语言生成不同的提示词
        if CURRENT_LANGUAGE == "en":
            lang_instruction = "\n**IMPORTANT: You MUST respond entirely in English.**\n"
            prompt1 = f"""{role_prompt1}
{lang_instruction}
{mode_instruction}

【Debate Topic】: {question}

【Your Position】: {role1} (Pro side)
【Opponent Role】: {role2} (Con side)

Please clearly and concisely present your core arguments (highlight 3-5 key points):
"""

            prompt2 = f"""{role_prompt2}
{lang_instruction}
{mode_instruction}

【Debate Topic】: {question}

【Your Position】: {role2} (Con side)
【Opponent Role】: {role1} (Pro side)

Please clearly and concisely present your core arguments (highlight 3-5 key points):
"""
        else:
            prompt1 = f"""{role_prompt1}
{mode_instruction}

【辩论主题】: {question}

【你的立场】: {role1}（正方）
【对手角色】: {role2}（反方）

请简洁有力地阐述你的核心观点（重点突出3-5个关键论点）：
"""

            prompt2 = f"""{role_prompt2}
{mode_instruction}

【辩论主题】: {question}

【你的立场】: {role2}（反方）
【对手角色】: {role1}（正方）

请简洁有力地阐述你的核心观点（重点突出3-5个关键论点）：
"""

        # 第一位辩论者发言（客户端已在前面获取）
        streaming_used1 = False
        if is_api1:
            # API模式：支持流式输出
            if self.config.streaming_output:
                result1 = client1.generate_response(prompt1, max_tokens=500, temperature=self.config.temperature,
                                                   streaming=True, speaker_name=display_name1, response_type="")
                streaming_used1 = True
            else:
                result1 = client1.generate_response(prompt1, max_tokens=500, temperature=self.config.temperature)
        else:
            # Ollama模式
            if self.config.streaming_output:
                result1 = client1._generate_streaming_response(self.config.model_1, prompt1, max_tokens=500,
                                                  temperature=self.config.temperature, timeout=self.config.timeout,
                                                  speaker_name=display_name1, response_type="")
                streaming_used1 = True
            else:
                result1 = client1.generate_response(self.config.model_1, prompt1, max_tokens=500,
                                                  temperature=self.config.temperature, timeout=self.config.timeout,
                                                  streaming=False)

        # 第二位辩论者发言
        streaming_used2 = False
        if is_api2:
            # API模式：支持流式输出
            if self.config.streaming_output:
                result2 = client2.generate_response(prompt2, max_tokens=500, temperature=self.config.temperature,
                                                   streaming=True, speaker_name=display_name2, response_type="")
                streaming_used2 = True
            else:
                result2 = client2.generate_response(prompt2, max_tokens=500, temperature=self.config.temperature)
        else:
            # Ollama模式
            if self.config.streaming_output:
                result2 = client2._generate_streaming_response(self.config.model_2, prompt2, max_tokens=500,
                                                  temperature=self.config.temperature, timeout=self.config.timeout,
                                                  speaker_name=display_name2, response_type="")
                streaming_used2 = True
            else:
                result2 = client2.generate_response(self.config.model_2, prompt2, max_tokens=500,
                                                  temperature=self.config.temperature, timeout=self.config.timeout,
                                                  streaming=False)

        # 安全处理
        if not result1.get("success"):
            result1 = {"success": False, "response": "（模型1无响应）"}
        if not result2.get("success"):
            result2 = {"success": False, "response": "（模型2无响应）"}

        response1 = result1.get("response", "")
        response2 = result2.get("response", "")

        debate_round = [
            {"round": 1, "speaker": display_name1, "content": response1, "type": "opening"},
            {"round": 1, "speaker": display_name2, "content": response2, "type": "opening"}
        ]

        # 非流式输出时才显示（流式输出已经实时显示过了）
        if not streaming_used1:
            self._display_debate_response(display_name1, response1)
        if not streaming_used2:
            self._display_debate_response(display_name2, response2)

        # 后续回合（智能提前结束）
        max_rounds = min(self.config.debate_rounds, 6)
        consensus_reached = False
        consensus_analysis = ""

        for round_num in range(2, max_rounds + 1):
            # 检查共识（使用AI分析）
            if self.config.enable_early_stop and self.config.ai_consensus_analysis and round_num >= self.config.consensus_check_start_round:
                print(f"\n🧠 正在分析双方共识度...")
                consensus_score, analysis, analysis_data = ConsensusDetector.analyze_debate_consensus(
                    self, self.config.coordinator_model, question, debate_round, display_name1, display_name2
                )

                consensus_percentage = int(consensus_score * 100)

                # 显示共识度条形图
                ConsensusDetector.display_consensus_bar(consensus_percentage)

                # 显示简短分析（限制长度，避免输出过长）
                if analysis_data and 'analysis_summary' in analysis_data:
                    short_analysis = analysis_data['analysis_summary'][:150]
                    if len(analysis_data['analysis_summary']) > 150:
                        short_analysis += "..."
                    print(f"📝 分析: {short_analysis}")
                elif analysis and len(analysis) < 200:
                    print(f"📝 分析: {analysis}")

                # 显示详细分析（简化显示）
                if analysis_data:
                    if 'recommendation' in analysis_data:
                        recommendation = analysis_data['recommendation']
                        if recommendation == 'end':
                            print(f"🎯 AI建议: 结束辩论")
                        else:
                            print(f"🔄 AI建议: 继续辩论")

                consensus_analysis = analysis

                # 检查是否达到阈值
                threshold_percentage = int(config.consensus_threshold * 100)
                consensus_reached = InteractiveInterface._handle_consensus_feedback(consensus_score, consensus_percentage, threshold_percentage, consensus_reached)
                if consensus_reached:
                    break

            DisplayManager.print_separator("-", 40)
            if CURRENT_LANGUAGE == "en":
                print(f"Round {round_num}: Mutual Response")
            else:
                print(f"第{round_num}回合：互相回应")
            DisplayManager.print_separator("-", 40)

            # 构建辩论历史上下文
            debate_history = AICouncilScheduler._build_debate_context(debate_round, display_name1, display_name2)

            # 模型1回应模型2 - 增强版：看到完整上下文
            if result1.get("success") and result2.get("success"):
                if CURRENT_LANGUAGE == "en":
                    rebuttal_prompt1 = f"""{role_prompt1}

**IMPORTANT: You MUST respond entirely in English.**

【Debate Topic】: {question}
【Your Position】: {role1} (Pro side)
【Opponent Role】: {role2} (Con side)

{debate_history}

【Your Task】
Refute {role2}'s arguments concisely and forcefully:
1. Point out the core weaknesses in opponent's arguments
2. Use 1-2 key arguments to refute
3. Reaffirm your core position

Please respond concisely (key points only, max 300 words):
"""
                else:
                    rebuttal_prompt1 = f"""{role_prompt1}

【辩论主题】: {question}
【你的立场】: {role1}（正方）
【对手角色】: {role2}（反方）

{debate_history}

【你的任务】
针对{role2}的观点进行简洁有力的反驳：
1. 指出对手观点的核心弱点
2. 用1-2个关键论据进行反驳
3. 重申你的核心立场

请简洁回应（重点突出，不超过300字）：
"""
                client1, _, is_api1 = self._get_client_for_model(self.config.model_1)
                rebuttal_streaming1 = False
                response_type1 = f"Rebuttal to {role2}" if CURRENT_LANGUAGE == "en" else f"反驳{role2}"
                if is_api1:
                    # API模式：支持流式输出
                    if self.config.streaming_output:
                        result1 = client1.generate_response(rebuttal_prompt1, max_tokens=600, temperature=self.config.temperature,
                                                           streaming=True, speaker_name=display_name1, response_type=response_type1)
                        rebuttal_streaming1 = True
                    else:
                        result1 = client1.generate_response(rebuttal_prompt1, max_tokens=600, temperature=self.config.temperature)
                else:
                    # Ollama模式
                    if self.config.streaming_output:
                        result1 = client1._generate_streaming_response(self.config.model_1, rebuttal_prompt1, max_tokens=600,
                                                          temperature=self.config.temperature, timeout=self.config.timeout,
                                                          speaker_name=display_name1, response_type=response_type1)
                        rebuttal_streaming1 = True
                    else:
                        result1 = client1.generate_response(self.config.model_1, rebuttal_prompt1, max_tokens=600,
                                                          temperature=self.config.temperature, timeout=self.config.timeout,
                                                          streaming=False)

                if result1.get("success"):
                    response1 = result1.get("response", "")
                    debate_round.append({
                        "round": round_num,
                        "speaker": display_name1,
                        "content": response1,
                        "type": "rebuttal"
                    })
                    if not rebuttal_streaming1:
                        self._display_debate_response(display_name1, response1, response_type1)

            # 模型2回应模型1 - 增强版：看到完整上下文
            if result1.get("success") and result2.get("success"):
                # 更新辩论历史，包含最新的AI1回应
                debate_history = AICouncilScheduler._build_debate_context(debate_round, display_name1, display_name2)

                if CURRENT_LANGUAGE == "en":
                    rebuttal_prompt2 = f"""{role_prompt2}

**IMPORTANT: You MUST respond entirely in English.**

【Debate Topic】: {question}
【Your Position】: {role2} (Con side)
【Opponent Role】: {role1} (Pro side)

{debate_history}

【Your Task】
Respond to {role1}'s rebuttal concisely and forcefully:
1. Counter opponent's rebuttal points
2. Use 1-2 key arguments to strengthen your position
3. Introduce new debate angles

Please respond concisely (key points only, max 300 words):
"""
                else:
                    rebuttal_prompt2 = f"""{role_prompt2}

【辩论主题】: {question}
【你的立场】: {role2}（反方）
【对手角色】: {role1}（正方）

{debate_history}

【你的任务】
针对{role1}的反驳进行简洁有力的回应：
1. 反驳对手的反驳论点
2. 用1-2个关键论据加强你的立场
3. 提出新的辩论角度

请简洁回应（重点突出，不超过300字）：
"""
                client2, _, is_api2 = self._get_client_for_model(self.config.model_2)
                rebuttal_streaming2 = False
                response_type2 = f"Rebuttal to {role1}" if CURRENT_LANGUAGE == "en" else f"反驳{role1}"
                if is_api2:
                    # API模式：支持流式输出
                    if self.config.streaming_output:
                        result2 = client2.generate_response(rebuttal_prompt2, max_tokens=600, temperature=self.config.temperature,
                                                           streaming=True, speaker_name=display_name2, response_type=response_type2)
                        rebuttal_streaming2 = True
                    else:
                        result2 = client2.generate_response(rebuttal_prompt2, max_tokens=600, temperature=self.config.temperature)
                else:
                    # Ollama模式
                    if self.config.streaming_output:
                        result2 = client2._generate_streaming_response(self.config.model_2, rebuttal_prompt2, max_tokens=600,
                                                          temperature=self.config.temperature, timeout=self.config.timeout,
                                                          speaker_name=display_name2, response_type=response_type2)
                        rebuttal_streaming2 = True
                    else:
                        result2 = client2.generate_response(self.config.model_2, rebuttal_prompt2, max_tokens=600,
                                                          temperature=self.config.temperature, timeout=self.config.timeout,
                                                          streaming=False)

                if result2.get("success"):
                    response2 = result2.get("response", "")
                    debate_round.append({
                        "round": round_num,
                        "speaker": display_name2,
                        "content": response2,
                        "type": "rebuttal"
                    })
                    if not rebuttal_streaming2:
                        self._display_debate_response(display_name2, response2, response_type2)

        # 协调阶段
        if CURRENT_LANGUAGE == "en":
            DisplayManager.print_header("🎯 Coordination Summary")
        else:
            DisplayManager.print_header("🎯 协调总结")

        if consensus_reached:
            if CURRENT_LANGUAGE == "en":
                print("🤝 High consensus reached, generating final summary")
            else:
                print("🤝 双方已达成高度共识，生成最终总结")
            self._generate_consensus_summary(question, debate_round, role1, role2, consensus_analysis)
        else:
            self._coordinate_responses(question, debate_round, role1, role2)

        # 询问用户是否保存辩论记录
        self._ask_save_debate_log(question, debate_round, display_name1, display_name2)

        # 返回完整的辩论记录，让用户可以看到所有发言
        return debate_round

    def _generate_consensus_summary(self, question: str, debate_round: List[Dict[str, Any]],
                                   role1: str, role2: str, consensus_analysis: str) -> str:
        """生成辩论共识总结报告（流式输出）

        当辩论达到共识阈值时，调用协调AI生成专业的总结报告：
        1. 整理完整的辩论过程和共识分析结果
        2. 要求AI生成结构化的总结报告
        3. 必须包含至少2点共识和2点分歧

        这是MACP系统的核心价值之一，能够将AI辩论转化为
        有价值的分析报告，帮助用户深入理解辩论主题
        """
        if CURRENT_LANGUAGE == "en":
            print(f"\n🤖 Coordinator AI ({self.config.coordinator_model}) generating final summary...")
            print("📝 Summary: ", end="", flush=True)
        else:
            print(f"\n🤖 协调AI ({self.config.coordinator_model}) 正在生成最终总结...")
            print("📝 总结: ", end="", flush=True)

        # 构建辩论摘要
        debate_summary = ""
        for entry in debate_round[-6:]:  # 最后6轮对话
            debate_summary += f"\n{entry['speaker']}: {entry.get('content', '')[:200]}"

        # 根据语言选择提示词
        if CURRENT_LANGUAGE == "en":
            summary_prompt = f"""Based on the following debate process and consensus analysis, please generate a final summary report:

【Debate Topic】: {question}
【Debate Parties】: {role1} vs {role2}
【Consensus Analysis】: {consensus_analysis}

【Debate Summary】:
{debate_summary}

Please generate a structured summary report that MUST include:

## 🎯 Debate Summary

### 📊 Consensus Points (MUST list at least 2 points)
1. [First consensus point]
2. [Second consensus point]
(More if applicable)

### ⚔️ Disagreement Points (MUST list at least 2 points)  
1. [First disagreement point]
2. [Second disagreement point]
(More if applicable)

### 🗣️ Position Comparison
- {role1}'s core position
- {role2}'s core position

### 💡 Comprehensive Conclusion
- Final answer to the original question
- Constructive suggestions

Please ensure the summary is objective and neutral."""
        else:
            summary_prompt = f"""基于以下辩论过程和共识分析，请生成最终总结报告：

【辩论主题】: {question}
【辩论双方】: {role1} vs {role2}
【共识分析】: {consensus_analysis}

【辩论过程摘要】:
{debate_summary}

请生成结构化的总结报告，【必须】包含：

## 🎯 辩论总结

### 📊 共识点（【必须】列出至少2点）
1. [第一个共识点]
2. [第二个共识点]
（如有更多可继续列出）

### ⚔️ 分歧点（【必须】列出至少2点）
1. [第一个分歧点]
2. [第二个分歧点]
（如有更多可继续列出）

### 🗣️ 双方立场对比
- {role1}的核心立场
- {role2}的核心立场

### 💡 综合结论
- 对原问题的最终答案
- 建设性建议和解决方案

请确保总结客观、中立，并基于双方的实际论述。"""

        coord_client, coord_model, is_api = self._get_client_for_model(self.config.coordinator_model)
        
        # 使用流式输出
        if is_api:
            # API模式的流式输出
            summary_result = coord_client.generate_response(
                summary_prompt, 
                max_tokens=1200, 
                temperature=self.config.temperature,
                streaming=True
            )
            summary = summary_result.get("response", "")
        else:
            # Ollama模式的流式输出
            summary_result = coord_client._generate_streaming_response(
                coord_model, 
                summary_prompt, 
                max_tokens=1200,
                temperature=self.config.temperature, 
                timeout=self.config.timeout,
                speaker_name="📝 总结" if CURRENT_LANGUAGE == "zh" else "📝 Summary"
            )
            summary = summary_result.get("response", "")

        print()  # 换行
        
        if summary_result.get("success") and summary.strip():
            if CURRENT_LANGUAGE == "en":
                print(f"\n✅ Summary generation complete")
            else:
                print(f"\n✅ 总结生成完成")
            return summary
        else:
            if CURRENT_LANGUAGE == "en":
                print(f"❌ Summary generation failed")
            else:
                print(f"❌ 总结生成失败")
            return f"基于共识分析的总结：{consensus_analysis}\n\n辩论已自动结束，双方达成高度共识。"

    def _coordinate_responses(self, question: str, debate_round: List[Dict[str, Any]],
                            role1: str, role2: str) -> str:
        """协调辩论结果（流式输出）"""
        if CURRENT_LANGUAGE == "en":
            print(f"\n🤖 Coordinator AI ({self.config.coordinator_model}) analyzing...")
            print("📝 Analysis: ", end="", flush=True)
        else:
            print(f"\n🤖 协调AI ({self.config.coordinator_model}) 正在分析...")
            print("📝 分析: ", end="", flush=True)

        # 构建摘要
        debate_summary = ""
        for entry in debate_round:  # 取全部辩论内容
            debate_summary += f"\n{entry['speaker']}: {entry.get('content', '')[:200]}"

        # 根据语言选择提示词
        if CURRENT_LANGUAGE == "en":
            coord_prompt = f"""Please analyze the following debate as a neutral coordinator:

Topic: {question}
Debate Parties: {role1} vs {role2}
Debate Summary: {debate_summary}

Please provide a structured analysis that MUST include:

### 📊 Consensus Points (MUST list at least 2 points)
1. [First consensus point - what both sides agree on]
2. [Second consensus point]
(More if applicable)

### ⚔️ Disagreement Points (MUST list at least 2 points)
1. [First disagreement point - where they differ]
2. [Second disagreement point]
(More if applicable)

### 💡 Comprehensive Suggestion
- Your neutral recommendation to the user
- How to think about this issue

Please be objective and balanced in your analysis."""
        else:
            coord_prompt = f"""请作为中立协调员分析以下辩论：

问题：{question}
辩论双方：{role1} vs {role2}
辩论摘要：{debate_summary}

请提供结构化分析，【必须】包含：

### 📊 共识点（【必须】列出至少2点）
1. [第一个共识点 - 双方都同意的观点]
2. [第二个共识点]
（如有更多可继续列出）

### ⚔️ 分歧点（【必须】列出至少2点）
1. [第一个分歧点 - 双方的不同观点]
2. [第二个分歧点]
（如有更多可继续列出）

### 💡 综合建议
- 给用户的中立建议
- 如何看待这个问题

请保持客观、中立的立场进行分析。"""

        coord_client, coord_model, is_api = self._get_client_for_model(self.config.coordinator_model)
        
        # 使用流式输出
        if is_api:
            coord_result = coord_client.generate_response(
                coord_prompt, 
                max_tokens=1000, 
                temperature=self.config.temperature,
                streaming=True
            )
            coord_response = coord_result.get("response", "")
        else:
            coord_result = coord_client._generate_streaming_response(
                coord_model, 
                coord_prompt, 
                max_tokens=1000,
                temperature=self.config.temperature, 
                timeout=self.config.timeout,
                speaker_name="📝 分析" if CURRENT_LANGUAGE == "zh" else "📝 Analysis"
            )
            coord_response = coord_result.get("response", "")

        print()  # 换行

        if coord_result.get("success") and coord_response.strip():
            if CURRENT_LANGUAGE == "en":
                print(f"\n✅ Coordinator analysis complete")
            else:
                print(f"\n✅ 协调AI分析完成")
            return coord_response
        else:
            if CURRENT_LANGUAGE == "en":
                print(f"❌ Coordinator analysis failed")
            else:
                print(f"❌ 协调AI分析失败")
            return f"协调分析失败"

    # ==================== 【海龟汤模式】 ====================
    def _turtle_soup_ask(self, question: str, role1: Optional[str] = None, role2: Optional[str] = None) -> List[Dict[str, Any]]:
        """海龟汤模式"""
        DisplayManager.print_header("🐢 海龟汤模式")
        print("规则：")
        print("1. 两个AI会轮流向您提问")
        print("2. 每个AI每回合只能问一个问题")
        print("3. 您只能回答 '是'、'否' 或 '不知道'")
        print("4. 目标是让AI猜出谜底")
        DisplayManager.print_separator()

        role1 = role1 or "侦探"
        role2 = role2 or "推理者"

        history = []
        round_count = 0
        max_rounds = self.config.turtle_soup_max_rounds

        while round_count < max_rounds:
            round_count += 1
            DisplayManager.print_separator("-", 40)
            print(f"第{round_count}回合")
            DisplayManager.print_separator("-", 40)

            # 交替提问
            current_role = role1 if round_count % 2 == 1 else role2
            current_model = self.config.model_1 if round_count % 2 == 1 else self.config.model_2

            # 生成问题
            if round_count == 1:
                prompt = f"""你是{current_role}，正在玩海龟汤游戏。
谜面：{question}
你的任务是向玩家提问，每次只能问一个问题，玩家只能回答是、否或不知道。
请开始你的第一个问题（只问一个问题）："""
            else:
                history_text = "\n".join(history[-4:])  # 最近4条历史
                prompt = f"""你是{current_role}，正在玩海龟汤游戏。
谜面：{question}
历史问答：
{history_text}
请基于以上信息问下一个问题（只问一个问题）："""

            client, model_id, is_api = self._get_client_for_model(current_model)
            if is_api:
                result = client.generate_response(prompt, max_tokens=200, temperature=self.config.temperature)
            else:
                result = client.generate_response(model_id, prompt, max_tokens=200,
                                                temperature=self.config.temperature, timeout=self.config.timeout,
                                                streaming=self.config.streaming_output)

            if result.get("success"):
                question_text = result.get("response", "").strip()
                print(f"\n❓ {current_role} 提问：{question_text}")

                # 用户回答
                answer = self._get_turtle_soup_answer()
                if answer == "结束":
                    print("👤 用户选择结束游戏")
                    break

                history.append(f"问：{question_text}")
                history.append(f"答：{answer}")

                # 猜测答案
                if round_count % 3 == 0:
                    guess = self._attempt_guess(current_model, current_role, question, history)
                    if guess and self._confirm_guess(guess):
                        print(f"🎉 恭喜！{current_role} 猜对了！")
                        break
            else:
                print(f"❌ {current_role} 提问失败")
                break

        # 最终总结
        self._finalize_turtle_soup(question, history)
        return []

    @staticmethod
    def _get_turtle_soup_answer() -> str:
        """获取海龟汤答案"""
        while True:
            answer = input("\n您的回答（是/否/不知道/结束）: ").strip().lower()
            if answer in ["是", "否", "不知道", "结束"]:
                return answer
            print("❌ 请只回答：是、否、不知道 或 结束")

    def _attempt_guess(self, model: str, role: str, question: str, history: List[str]) -> Optional[str]:
        """尝试猜测答案"""
        guess_prompt = f"""基于以下信息，请猜测谜底：
谜面：{question}
历史问答：
{"\n".join(history[-6:])}
请给出你的猜测（如果还不确定可以说'还需要更多信息'）："""

        client, model_id, is_api = self._get_client_for_model(model)
        if is_api:
            guess_result = client.generate_response(guess_prompt, max_tokens=300, temperature=self.config.temperature)
        else:
            guess_result = client.generate_response(model_id, guess_prompt, max_tokens=300,
                                                  temperature=self.config.temperature, timeout=self.config.timeout,
                                                  streaming=self.config.streaming_output)
        if guess_result.get("success"):
            guess = guess_result.get("response", "").strip()
            print(f"\n🤔 {role} 猜测：{guess}")
            return guess
        return None

    @staticmethod
    def _confirm_guess(guess: str) -> bool:
        """确认猜测"""
        _ = guess  # 标记参数已知但未使用
        confirm = input("猜对了吗？（是/否）: ").strip().lower()
        return confirm == "是"

    def _finalize_turtle_soup(self, question: str, history: List[str]):
        """完成海龟汤游戏"""
        DisplayManager.print_header("📝 海龟汤游戏结束")

        if history:
            final_prompt = f"""基于以下海龟汤游戏记录，请总结：
谜面：{question}
历史记录：
{"\n".join(history)}
请给出最终分析和谜底解释："""

            coord_client, coord_model, is_api = self._get_client_for_model(self.config.coordinator_model)
            if is_api:
                final_result = coord_client.generate_response(final_prompt, max_tokens=500, temperature=self.config.temperature)
            else:
                final_result = coord_client.generate_response(coord_model, final_prompt, max_tokens=500,
                                                            temperature=self.config.temperature, timeout=self.config.timeout,
                                                            streaming=False)
            if final_result.get("success"):
                summary = final_result.get("response", "")
                print(f"\n📋 最终总结：")
                print(summary[:self.config.display_length] +
                      ("..." if len(summary) > self.config.display_length else ""))

    # ==================== 【辅助方法】 ====================
    def _display_results(self, results: List[Dict[str, Any]]):
        """显示结果"""
        DisplayManager.print_separator("-", 80)
        print("📊 回答结果：")
        DisplayManager.print_separator("-", 80)

        for result in results:
            DisplayManager.print_result(result, self.config.display_length)

    @staticmethod
    def _build_debate_context(debate_round: List[Dict], display_name1: str, display_name2: str) -> str:
        """构建辩论历史上下文
        
        Args:
            debate_round: 辩论轮次记录
            display_name1: 第一个辩论者显示名称（未使用，保留用于未来扩展）
            display_name2: 第二个辩论者显示名称（未使用，保留用于未来扩展）
        """
        _ = (display_name1, display_name2)  # 标记参数已知但未使用（为未来扩展保留）
        context_parts = ["【辩论历史】"]

        for entry in debate_round[-4:]:  # 只显示最近4条发言，避免上下文过长
            speaker = entry["speaker"]
            content = entry["content"][:500]  # 限制每个发言的长度
            round_num = entry["round"]

            context_parts.append(f"第{round_num}回合 - {speaker}：")
            context_parts.append(f"  {content}")
            context_parts.append("")

        return "\n".join(context_parts).strip()

    def _display_debate_response(self, speaker: str, content: str, response_type: str = ""):
        """显示辩论响应"""
        type_prefix = f" {response_type}：" if response_type else "："
        print(f"\n📢 {speaker}{type_prefix}")
        print(content[:self.config.display_length] +
              ("..." if len(content) > self.config.display_length else ""))

    def _save_history_entry(self, question: str, results: List[Dict[str, Any]], mode: str):
        """保存历史记录"""
        entry = {
            "session_id": self.session_id,
            "type": mode,
            "question": question,
            "results": results
        }
        self.history_manager.add_entry(entry)

    def _save_debate_entry(self, question: str, debate_round: List[Dict[str, Any]],
                          role1: str, role2: str):
        """保存辩论历史"""
        entry = {
            "session_id": self.session_id,
            "type": "debate",
            "question": question,
            "roles": [role1, role2],
            "debate_rounds": debate_round
        }
        self.history_manager.add_entry(entry)

    def _ask_save_debate_log(self, question: str, debate_round: List[Dict[str, Any]],
                            role1: str, role2: str):
        """询问用户是否保存辩论记录到日志
        
        辩论结束后，询问用户保存选项：
        1. 存储到日志文件（追加到 macp.txt）
        2. 单独保存为一个新的txt文件
        3. 不保存
        """
        print("\n" + "=" * 50)
        if CURRENT_LANGUAGE == "en":
            print("📝 Debate ended, save debate record?")
            print("=" * 50)
            print("1. 📋 Save to log file (macp.txt)")
            print("2. 📄 Save as separate txt file")
            print("3. ❌ Don't save")
            print("=" * 50)
        else:
            print("📝 辩论已结束，是否保存辩论记录？")
            print("=" * 50)
            print("1. 📋 存储到日志文件 (macp.txt)")
            print("2. 📄 单独保存为新的txt文件")
            print("3. ❌ 不保存")
            print("=" * 50)
        
        while True:
            if CURRENT_LANGUAGE == "en":
                choice = input("Select (1/2/3): ").strip()
            else:
                choice = input("请选择 (1/2/3): ").strip()
            
            if choice == "1":
                # 存储到日志文件
                self._save_debate_entry(question, debate_round, role1, role2)
                if self.config.save_history:
                    self.history_manager.save_history()
                if CURRENT_LANGUAGE == "en":
                    print("✅ Debate record saved to log file (macp.txt)")
                else:
                    print("✅ 辩论记录已保存到日志文件 (macp.txt)")
                break
            elif choice == "2":
                # 单独保存为新的txt文件
                self._save_debate_to_separate_file(question, debate_round, role1, role2)
                break
            elif choice == "3":
                if CURRENT_LANGUAGE == "en":
                    print("⏭️ Skipped saving")
                else:
                    print("⏭️ 跳过保存")
                break
            else:
                if CURRENT_LANGUAGE == "en":
                    print("⚠️ Invalid choice, please enter 1, 2 or 3")
                else:
                    print("⚠️ 无效选择，请输入 1、2 或 3")

    def _save_debate_to_separate_file(self, question: str, debate_round: List[Dict[str, Any]],
                                      role1: str, role2: str):
        """将辩论记录保存到单独的txt文件
        
        创建一个新的txt文件，包含完整的辩论内容，
        文件名基于时间戳和辩论主题生成。
        """
        # 生成文件名（使用时间戳和简化的主题）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 清理问题作为文件名的一部分（移除特殊字符）
        safe_question = re.sub(r'[\\/*?:"<>|]', '', question)[:30].strip()
        if not safe_question:
            safe_question = "Debate" if CURRENT_LANGUAGE == "en" else "辩论"
        
        if CURRENT_LANGUAGE == "en":
            filename = f"Debate_Record_{timestamp}_{safe_question}.txt"
        else:
            filename = f"辩论记录_{timestamp}_{safe_question}.txt"
        filepath = os.path.join(r"C:\Users\yuangu114514\Desktop", filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                if CURRENT_LANGUAGE == "en":
                    f.write("🤖 MACP Debate Record\n")
                else:
                    f.write("🤖 MACP 辩论记录\n")
                f.write("=" * 60 + "\n\n")
                
                if CURRENT_LANGUAGE == "en":
                    f.write(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"🎯 Debate Topic: {question}\n")
                    f.write(f"🎭 Debaters: {role1} vs {role2}\n")
                    f.write(f"📊 Session ID: {self.session_id}\n\n")
                    f.write("-" * 60 + "\n")
                    f.write("📜 Debate Content\n")
                else:
                    f.write(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"🎯 辩论主题: {question}\n")
                    f.write(f"🎭 辩论双方: {role1} vs {role2}\n")
                    f.write(f"📊 会话ID: {self.session_id}\n\n")
                    f.write("-" * 60 + "\n")
                    f.write("📜 辩论内容\n")
                f.write("-" * 60 + "\n\n")
                
                for entry in debate_round:
                    round_num = entry.get("round", "?")
                    speaker = entry.get("speaker", "Unknown" if CURRENT_LANGUAGE == "en" else "未知")
                    content = entry.get("content", "")
                    entry_type = entry.get("type", "")
                    
                    type_label = ""
                    if entry_type == "opening":
                        type_label = "[Opening Statement]" if CURRENT_LANGUAGE == "en" else "[开场陈述]"
                    elif entry_type == "rebuttal":
                        type_label = "[Rebuttal]" if CURRENT_LANGUAGE == "en" else "[反驳]"
                    
                    if CURRENT_LANGUAGE == "en":
                        f.write(f"【Round {round_num}】 {speaker} {type_label}\n")
                    else:
                        f.write(f"【第{round_num}回合】 {speaker} {type_label}\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{content}\n\n")
                
                f.write("=" * 60 + "\n")
                if CURRENT_LANGUAGE == "en":
                    f.write("End of Debate Record\n")
                else:
                    f.write("辩论记录结束\n")
                f.write("=" * 60 + "\n")
            
            if CURRENT_LANGUAGE == "en":
                print(f"✅ Debate record saved to: {filepath}")
            else:
                print(f"✅ 辩论记录已保存到: {filepath}")
            logger.info(f"辩论记录已单独保存到: {filepath}")
            
        except (OSError, IOError) as e:
            print(f"❌ 保存辩论记录失败: {e}")
            logger.error(f"保存辩论记录到单独文件失败: {e}")

    def _setup_debate_roles(self, question: str, role1: str, role2: str):
        """设置辩论角色并执行标签检测

        为辩论双方配置合适的角色，并根据问题内容检测相关标签：
        1. 应用角色的立场偏好（尤其是辩论手的正反方机制）
        2. 分析问题内容，检测相关的专业领域标签
        3. 显示检测到的标签信息，帮助用户理解AI的专业背景

        这确保了辩论双方能够从合适的专业角度和立场参与讨论
        """
        # 检测标签
        if self.config.enable_tags:
            tags = role_system.detect_tags(question)
            if tags:
                logger.info(f"🏷️  检测到标签: {', '.join(tags)}")
                print(f"🏷️  检测到标签: {', '.join(tags)}")

        print(f"🎭 辩论角色: {role1} vs {role2}")

    def competition_debate(self, question: str, role1: str = None, role2: str = None, rounds: int = 3) -> List[Dict[str, Any]]:
        """辩论赛模式 - 双方对抗，最后由裁判判定胜负
        
        与普通辩论模式不同：
        1. 普通辩论模式：寻求共识，达成一致结论
        2. 辩论赛模式：对抗辩论，最后判定谁赢谁输
        
        流程：
        1. 双方进行指定回合数的辩论
        2. 协调AI作为裁判进行评判
        3. 判定胜负并给出理由
        4. 总结共识点和分歧点
        """
        role1 = role1 or self.config.default_role_1
        role2 = role2 or self.config.default_role_2

        # 获取客户端和模型
        client1, model_id1, is_api1 = self._get_client_for_model(self.config.model_1)
        client2, model_id2, is_api2 = self._get_client_for_model(self.config.model_2)

        actual_model1 = model_id1 if is_api1 else self.config.model_1
        actual_model2 = model_id2 if is_api2 else self.config.model_2
        display_name1 = f"{actual_model1}-{role1}"
        display_name2 = f"{actual_model2}-{role2}"

        role_prompt1 = role_system.get_role_prompt(role1, is_first=True)
        role_prompt2 = role_system.get_role_prompt(role2, is_first=False)

        if not role_prompt1 or not role_prompt2:
            raise InvalidRoleError(f"无效角色: {role1} 或 {role2}")

        debate_round = []

        # 分析问题类型
        question_analysis = analyze_question_type(question)
        accuracy_required = question_analysis["accuracy_required"]
        
        if CURRENT_LANGUAGE == "en":
            mode_instruction = ANTI_HALLUCINATION_PROMPT_EN if accuracy_required else PHILOSOPHICAL_PROMPT_EN
        else:
            mode_instruction = ANTI_HALLUCINATION_PROMPT_ZH if accuracy_required else PHILOSOPHICAL_PROMPT_ZH

        if CURRENT_LANGUAGE == "en":
            print(f"\n🏆 Competition Mode: {role1} (Pro) vs {role2} (Con)")
            print(f"📋 Proposition: {question}")
            print(f"⏱️ Rounds: {rounds}")
        else:
            print(f"\n🏆 辩论赛模式 (Competition Mode)：{role1}（正方/Pro） vs {role2}（反方/Con）")
            print(f"📋 辩题 (Proposition)：{question}")
            print(f"⏱️ 回合数 (Rounds)：{rounds}")

        # 第一回合：开场陈述
        DisplayManager.print_separator("-", 40)
        print("第1回合：开场陈述 (Round 1: Opening Statements)")
        DisplayManager.print_separator("-", 40)

        # 正方开场 - 始终使用中英双语提示词让AI用英文回答
        lang_instruction = "\n**IMPORTANT: You MUST respond entirely in English.**\n"
        prompt1 = f"""{role_prompt1}
{lang_instruction}
{mode_instruction}

【Competition Debate / 辩论赛】
Proposition / 辩题: {question}

You are the PRO side. You must SUPPORT this proposition.
你是正方。你必须【支持】这个命题。
Please present your opening statement with 3-5 key arguments.
Be persuasive and logical. You will be judged on the strength of your arguments."""

        print(f"\n📢 {display_name1}（正方/Pro）：", end="", flush=True)
        
        if is_api1:
            result1 = client1.generate_response(prompt1, streaming=True)
        else:
            result1 = client1._generate_streaming_response(
                model_id1, prompt1, timeout=self.config.timeout,
                speaker_name=f"{display_name1}（正方）" if CURRENT_LANGUAGE == "zh" else f"{display_name1} (Pro)"
            )
        
        response1 = result1.get("response", "")
        debate_round.append({"round": 1, "speaker": display_name1, "content": response1, "type": "opening", "side": "pro"})
        print()

        # 反方开场 - 始终使用中英双语提示词让AI用英文回答
        prompt2 = f"""{role_prompt2}
{lang_instruction}
{mode_instruction}

【Competition Debate / 辩论赛】
Proposition / 辩题: {question}

You are the CON side. You must OPPOSE this proposition.
你是反方。你必须【反对】这个命题。
The PRO side argued / 正方的论点: {response1[:500]}...

Please present your opening statement with 3-5 key arguments.
Be persuasive and logical. You will be judged on the strength of your arguments."""

        print(f"\n📢 {display_name2}（反方/Con）：", end="", flush=True)
        
        if is_api2:
            result2 = client2.generate_response(prompt2, streaming=True)
        else:
            result2 = client2._generate_streaming_response(
                model_id2, prompt2, timeout=self.config.timeout,
                speaker_name=f"{display_name2}（反方）" if CURRENT_LANGUAGE == "zh" else f"{display_name2} (Con)"
            )
        
        response2 = result2.get("response", "")
        debate_round.append({"round": 1, "speaker": display_name2, "content": response2, "type": "opening", "side": "con"})
        print()

        # 后续回合：反驳
        for round_num in range(2, rounds + 1):
            DisplayManager.print_separator("-", 40)
            if CURRENT_LANGUAGE == "en":
                print(f"Round {round_num}: Rebuttal")
            else:
                print(f"第{round_num}回合：反驳")
            DisplayManager.print_separator("-", 40)

            # 正方反驳
            last_con_response = debate_round[-1]["content"] if debate_round[-1]["side"] == "con" else response2
            
            if CURRENT_LANGUAGE == "en":
                rebuttal_prompt1 = f"""{role_prompt1}
{lang_instruction}

【Competition Debate - Round {round_num}】
Proposition: {question}
You are PRO side.

CON side's argument: {last_con_response[:600]}...

Please rebut the CON side's arguments and strengthen your position.
Point out flaws in their logic, provide counter-evidence, and reinforce your core arguments."""
            else:
                rebuttal_prompt1 = f"""{role_prompt1}

【辩论赛 - 第{round_num}回合】
辩题：{question}
你是正方。

反方的论点：{last_con_response[:600]}...

请反驳反方的论点并强化你的立场。
指出对方的逻辑漏洞，提供反证，并强化你的核心论点。"""

            print(f"\n📢 {display_name1}（正方）反驳：", end="", flush=True)
            
            if is_api1:
                result1 = client1.generate_response(rebuttal_prompt1, streaming=True)
            else:
                result1 = client1._generate_streaming_response(
                    model_id1, rebuttal_prompt1, timeout=self.config.timeout,
                    speaker_name=f"{display_name1} 反驳" if CURRENT_LANGUAGE == "zh" else f"{display_name1} Rebuttal"
                )
            
            response1 = result1.get("response", "")
            debate_round.append({"round": round_num, "speaker": display_name1, "content": response1, "type": "rebuttal", "side": "pro"})
            print()

            # 反方反驳
            if CURRENT_LANGUAGE == "en":
                rebuttal_prompt2 = f"""{role_prompt2}
{lang_instruction}

【Competition Debate - Round {round_num}】
Proposition: {question}
You are CON side.

PRO side's argument: {response1[:600]}...

Please rebut the PRO side's arguments and strengthen your position.
Point out flaws in their logic, provide counter-evidence, and reinforce your core arguments."""
            else:
                rebuttal_prompt2 = f"""{role_prompt2}

【辩论赛 - 第{round_num}回合】
辩题：{question}
你是反方。

正方的论点：{response1[:600]}...

请反驳正方的论点并强化你的立场。
指出对方的逻辑漏洞，提供反证，并强化你的核心论点。"""

            print(f"\n📢 {display_name2}（反方）反驳：", end="", flush=True)
            
            if is_api2:
                result2 = client2.generate_response(rebuttal_prompt2, streaming=True)
            else:
                result2 = client2._generate_streaming_response(
                    model_id2, rebuttal_prompt2, timeout=self.config.timeout,
                    speaker_name=f"{display_name2} 反驳" if CURRENT_LANGUAGE == "zh" else f"{display_name2} Rebuttal"
                )
            
            response2 = result2.get("response", "")
            debate_round.append({"round": round_num, "speaker": display_name2, "content": response2, "type": "rebuttal", "side": "con"})
            print()

        # 裁判评判
        DisplayManager.print_separator("=", 60)
        if CURRENT_LANGUAGE == "en":
            print("🏛️ JUDGE'S VERDICT")
        else:
            print("🏛️ 裁判评判")
        DisplayManager.print_separator("=", 60)
        
        self._judge_competition(question, debate_round, role1, role2, display_name1, display_name2)

        # 询问是否保存
        self._ask_save_debate_log(question, debate_round, display_name1, display_name2)

        return debate_round

    def _judge_competition(self, question: str, debate_round: List[Dict[str, Any]], 
                          role1: str, role2: str, display_name1: str, display_name2: str):
        """裁判AI评判辩论赛胜负（流式输出）"""
        if CURRENT_LANGUAGE == "en":
            print(f"\n🤖 Judge ({self.config.coordinator_model}) evaluating...")
            print("⚖️ Verdict: ", end="", flush=True)
        else:
            print(f"\n🤖 裁判AI ({self.config.coordinator_model}) 正在评判...")
            print("⚖️ 评判: ", end="", flush=True)

        # 构建辩论摘要
        debate_summary = ""
        for entry in debate_round:
            side = "Pro" if entry["side"] == "pro" else "Con"
            debate_summary += f"\n【{side} - Round {entry['round']}】 {entry['speaker']}:\n{entry['content'][:300]}...\n"

        # 构建裁判提示词
        if CURRENT_LANGUAGE == "en":
            judge_prompt = f"""You are an impartial debate judge. Please evaluate the following debate competition:

【Proposition】: {question}
【PRO Side】: {display_name1}
【CON Side】: {display_name2}

【Debate Record】:
{debate_summary}

Please provide your verdict with the following structure:

## 🏆 Winner Announcement
**Winner: [PRO/CON side]** - [One sentence reason]

## 📊 Scoring (out of 10 for each)
| Criterion | PRO | CON |
|-----------|-----|-----|
| Argument Strength | X | X |
| Logic Rigor | X | X |
| Rebuttal Effectiveness | X | X |
| Evidence Quality | X | X |
| **Total** | XX | XX |

## 🤝 Consensus Points (MUST list at least 2)
1. [First point both sides agree on]
2. [Second point both sides agree on]

## ⚔️ Key Disagreements (MUST list at least 2)
1. [First major disagreement]
2. [Second major disagreement]

## 💬 Judge's Comments
- PRO side's strengths and weaknesses
- CON side's strengths and weaknesses
- Key moments that influenced the verdict

## 💡 Final Recommendation
- Your neutral perspective on the proposition
- Advice for the user on this topic

Please be fair and objective in your judgment."""
        else:
            judge_prompt = f"""你是一位公正的辩论赛裁判。请评判以下辩论赛：

【辩题】：{question}
【正方】：{display_name1}
【反方】：{display_name2}

【辩论记录】：
{debate_summary}

请按以下结构给出你的裁决：

## 🏆 胜负宣布
**获胜方：[正方/反方]** - [一句话理由]

## 📊 评分（每项满分10分）
| 评判项 | 正方 | 反方 |
|--------|------|------|
| 论点强度 | X | X |
| 逻辑严谨 | X | X |
| 反驳有效性 | X | X |
| 论据质量 | X | X |
| **总分** | XX | XX |

## 🤝 共识点（【必须】列出至少2点）
1. [双方都认同的第一个观点]
2. [双方都认同的第二个观点]

## ⚔️ 核心分歧（【必须】列出至少2点）
1. [第一个主要分歧]
2. [第二个主要分歧]

## 💬 裁判点评
- 正方的优点与不足
- 反方的优点与不足
- 影响裁决的关键时刻

## 💡 最终建议
- 你对这个辩题的中立看法
- 给用户关于这个问题的建议

请保持公正客观的态度进行裁决。"""

        coord_client, coord_model, is_api = self._get_client_for_model(self.config.coordinator_model)
        
        # 使用流式输出
        if is_api:
            judge_result = coord_client.generate_response(
                judge_prompt, 
                max_tokens=1500, 
                temperature=0.7,
                streaming=True
            )
        else:
            judge_result = coord_client._generate_streaming_response(
                coord_model, 
                judge_prompt, 
                max_tokens=1500,
                temperature=0.7, 
                timeout=self.config.timeout,
                speaker_name="⚖️ 裁决" if CURRENT_LANGUAGE == "zh" else "⚖️ Verdict"
            )

        print()  # 换行
        
        if judge_result.get("success"):
            if CURRENT_LANGUAGE == "en":
                print(f"\n✅ Judgment complete")
            else:
                print(f"\n✅ 评判完成")
        else:
            if CURRENT_LANGUAGE == "en":
                print(f"\n❌ Judgment failed")
            else:
                print(f"\n❌ 评判失败")

    def cleanup(self):
        """清理资源"""
        if self.config.save_history:
            self.history_manager.save_history()
        logger.info("🧹 资源清理完成")

# ==================== 【用户交互界面】 ====================
# 命令行用户界面，处理用户输入和系统输出

class InteractiveInterface:
    """MACP命令行交互界面

    提供用户友好的命令行界面：
    - 命令解析和执行
    - 菜单显示和导航
    - 用户输入验证
    - 结果格式化输出

    支持的主要命令：
    - 直接提问（并行模式）
    - /debate（辩论模式）
    - /turtle（海龟汤模式）
    - /consensus（共识配置）
    - /help（帮助信息）
    """

    def __init__(self, scheduler: AICouncilScheduler):
        self.scheduler = scheduler

    def run(self):
        """运行交互界面"""
        self._print_welcome()
        self._print_commands()

        # 检查是否需要配置API（用户在启动时选择了API模式但没有Ollama）
        global NEED_API_SETUP
        if NEED_API_SETUP:
            print("\n" + "=" * 60)
            print("🌐 检测到您选择了 API 模式，现在开始配置")
            print("   (Detected API mode selection, starting configuration)")
            print("=" * 60)
            self._configure_api_mode()
            NEED_API_SETUP = False

        while True:
            try:
                user_input = input(f"\n📝 请输入问题或命令 (Enter question or command)：").strip()

                if not user_input:
                    continue

                if user_input.startswith('/'):
                    self._handle_command(user_input[1:])
                else:
                    self._handle_question(user_input)

            except KeyboardInterrupt:
                self._handle_interrupt()
            except Exception as e:
                logger.error(f"发生错误：{e}")
                print(f"❌ 发生错误 (Error occurred)：{e}")

    @staticmethod
    def _print_welcome():
        """打印欢迎信息 (Print welcome message)"""
        DisplayManager.print_header("🤖 MACP 多AI协作平台 (Multi-AI Collaboration Platform) v5.0")
        print(f"模型1 (Model 1)：{config.model_1}")
        print(f"模型2 (Model 2)：{config.model_2}")
        print(f"协调模型 (Coordinator)：{config.coordinator_model}")
        opt_status = "开启/Enabled" if config.optimize_memory else "关闭/Disabled"
        print(f"优化模式 (Optimize Mode)：{opt_status}")
        DisplayManager.print_separator()

    @staticmethod
    def _print_commands():
        """打印可用命令"""
        print(f"\n{get_text('available_commands')}")
        
        # 命令列表（中英双语）
        commands = [
            ("help", "显示帮助 (Show help)"),
            ("models", "查看可用模型 (View available models)"),
            ("config", "查看当前配置 (View current config)"),
            ("history", "查看历史记录 (View history)"),
            ("api", "配置API模式 (Configure API mode)"),
            ("debate", "辩论模式-寻求共识 (Debate mode - seek consensus)"),
            ("competition", "辩论赛模式-判定胜负 (Competition - judge winner)"),
            ("turtle", "海龟汤模式 (Turtle soup mode)"),
            ("consensus", "配置共识检测 (Configure consensus detection)"),
            ("streaming", "切换流式输出 (Toggle streaming output)"),
            ("optimize", "开启优化模式 (Enable optimize mode)"),
            ("roles", "查看可用角色 (View available roles)"),
            ("tags", "查看标签系统 (View tag system)"),
            ("mode", "切换协调模式 (Switch coordination mode)"),
            ("addai", "添加新AI模型 (Add new AI model)"),
            ("listai", "列出所有AI模型 (List all AI models)"),
            ("removeai", "移除AI模型 (Remove AI model)"),
            ("language", "切换语言 (Switch language)"),
            ("clear", "清屏 (Clear screen)"),
            ("exit", "退出程序 (Exit program)")
        ]

        for cmd, desc in commands:
            print(f"  /{cmd:<12} - {desc}")
        DisplayManager.print_separator()

    def _handle_question(self, question: str):
        """处理问题输入 (Handle question input)"""
        print(f"\n🔍 正在处理问题 (Processing question)...")
        self.scheduler.progress_tracker.start()

        try:
            self.scheduler.ask_both_models(question, mode="parallel")
            total_time = self.scheduler.progress_tracker.get_elapsed_time()
            print(f"\n✅ 总耗时 (Total time)：{total_time:.2f}秒/s")
        except Exception as e:
            logger.error(f"处理问题失败: {e}")
            print(f"❌ 处理问题失败 (Failed to process question): {e}")

    def _handle_command(self, command: str):
        """处理命令"""
        command = command.lower()

        handlers = {
            'help': self._print_commands,
            'models': self._show_models,
            'config': self._show_config,
            'history': self._show_history,
            'api': self._configure_api_mode,
            'debate': self._enter_debate_mode,
            'competition': self._enter_competition_mode,
            'turtle': self._enter_turtle_soup_mode,
            'consensus': self._configure_consensus,
            'optimize': self._toggle_optimize_mode,
            'roles': self._show_roles,
            'tags': self._show_tags,
            'mode': self._toggle_coordination_mode,
            'streaming': self._toggle_streaming_mode,
            'language': self._switch_language,
            'addai': self._add_ai_model,
            'listai': self._list_ai_models,
            'removeai': self._remove_ai_model,
            'clear': DisplayManager.clear_screen,
            'exit': self._exit_program
        }

        handler = handlers.get(command)
        if handler:
            try:
                handler()
            except Exception as e:
                logger.error(f"执行命令 /{command} 失败: {e}")
                print(f"❌ 执行命令失败 (Command execution failed): {e}")
        else:
            print(f"❌ 未知命令 (Unknown command)：/{command}")

    def _show_models(self):
        """显示可用模型 (Show available models)"""
        print("\n📦 检查可用模型 (Checking available models)...")
        models = self.scheduler.client.list_models()
        print(DisplayManager.format_model_list(models))

    @staticmethod
    def _show_config():
        """显示当前配置 (Show current config)"""
        config_dict = config.to_dict()
        print(DisplayManager.format_config_display(config_dict))

    def _show_history(self):
        """显示历史记录 (Show history)"""
        print(f"\n📜 历史记录 (History) | 会话ID (Session ID)：{self.scheduler.session_id}")
        history = self.scheduler.history_manager.get_recent_history(5)

        if history:
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('timestamp', '')[:16]
                entry_type = entry.get('type', 'unknown')
                question = entry.get('question', '')[:60]
                print(f"\n  [{i}] {timestamp} - {entry_type}")
                print(f"      问题 (Question)：{question}...")
        else:
            print("  暂无历史记录 (No history records)")

    def _enter_debate_mode(self):
        """进入辩论模式 (Enter debate mode)"""
        DisplayManager.print_header("💬 辩论模式 (Debate Mode)")
        print("\n选择协调模式 (Select coordination mode)：")
        print("  1. AI自动协调 (AI Auto-coordination) [默认/default]")
        print("  2. 用户手动协调 (User Manual coordination)")
        mode_choice = input("选择/Select (1/2): ").strip()
        if mode_choice == "2":
            config.coordination_mode = "user"
            print("✅ 已选择用户协调模式 (User coordination mode selected)")
        else:
            config.coordination_mode = "auto"
            print("✅ 已选择AI自动协调模式 (AI auto-coordination mode selected)")

        # 输入问题
        question = input("\n请输入辩论问题 (Enter debate topic)：").strip()
        if not question:
            print("❌ 问题不能为空 (Topic cannot be empty)")
            return

        # 选择角色
        role1, role2 = self._select_debate_roles()

        # 回合数
        rounds_input = input(f"\n辩论回合数 (Debate rounds) [默认/default:{config.debate_rounds}]: ").strip()
        if rounds_input.isdigit():
            config.debate_rounds = int(rounds_input)

        # 开始辩论
        print(f"\n🎬 开始辩论 (Starting debate)：{role1} vs {role2}")
        print(f"问题 (Topic)：{question}")
        DisplayManager.print_separator()

        self.scheduler.progress_tracker.start()
        try:
            self.scheduler.ask_both_models(question, mode="debate", role1=role1, role2=role2)
            total_time = self.scheduler.progress_tracker.get_elapsed_time()
            print(f"\n✅ 辩论完成 (Debate complete) | 总耗时 (Total time)：{total_time:.2f}秒/s")
        except Exception as e:
            logger.error(f"辩论失败: {e}")
            print(f"❌ 辩论失败 (Debate failed): {e}")

    def _enter_competition_mode(self):
        """进入辩论赛模式 (Enter competition mode)"""
        DisplayManager.print_header("🏆 辩论赛模式 (Competition Mode)")
        print("\n🎯 在此模式下，AI双方将进行对抗辩论，最后由裁判AI判定胜负。")
        print("   (In this mode, AI debaters will argue, and a judge will determine the winner.)")
        print("这与普通辩论模式（寻求共识）不同。")
        print("   (This is different from debate mode which seeks consensus.)\n")

        # 输入辩题
        question = input("请输入辩论命题 (Enter debate proposition)：").strip()
        if not question:
            print("❌ 命题不能为空 (Proposition cannot be empty)")
            return

        # 选择角色
        role1, role2 = self._select_debate_roles()

        # 回合数
        rounds_input = input(f"\n辩论回合数 (Debate rounds) [默认/default:3]: ").strip()
        
        rounds = int(rounds_input) if rounds_input.isdigit() else 3

        # 开始辩论赛
        print(f"\n🎬 开始辩论赛 (Starting competition)：{role1}（正方/Pro） vs {role2}（反方/Con）")
        print(f"辩题 (Proposition)：{question}")
        print(f"回合数 (Rounds)：{rounds}")
        DisplayManager.print_separator()

        self.scheduler.progress_tracker.start()
        try:
            self.scheduler.competition_debate(question, role1=role1, role2=role2, rounds=rounds)
            total_time = self.scheduler.progress_tracker.get_elapsed_time()
            print(f"\n✅ 辩论赛完成 (Competition complete) | 总耗时 (Total time)：{total_time:.2f}秒/s")
        except Exception as e:
            logger.error(f"辩论赛失败: {e}")
            print(f"❌ 辩论赛失败 (Competition failed): {e}")

    def _enter_turtle_soup_mode(self):
        """进入海龟汤模式 (Enter turtle soup mode)"""
        DisplayManager.print_header("🐢 海龟汤模式 (Turtle Soup Mode)")

        question = input("\n请输入海龟汤谜面 (Enter riddle)：").strip()
        if not question:
            print("❌ 谜面不能为空 (Riddle cannot be empty)")
            return

        role1 = input("\nAI1角色 (AI1 role) [默认/default: 侦探/Detective]: ").strip() or "侦探"
        role2 = input("AI2角色 (AI2 role) [默认/default: 推理者/Reasoner]: ").strip() or "推理者"

        print(f"\n🎮 开始海龟汤游戏 (Starting Turtle Soup game)")
        print(f"谜面 (Riddle)：{question}")
        print(f"AI角色 (AI roles)：{role1} 和/and {role2}")
        DisplayManager.print_separator()

        try:
            self.scheduler.ask_both_models(question, mode="turtle_soup", role1=role1, role2=role2)
        except Exception as e:
            logger.error(f"海龟汤游戏失败: {e}")
            print(f"❌ 海龟汤游戏失败: {e}")

    @staticmethod
    def _toggle_optimize_mode():
        """切换优化模式 (Toggle optimize mode)"""
        config.optimize_memory = not config.optimize_memory
        status = "开启/Enabled" if config.optimize_memory else "关闭/Disabled"
        print(f"✅ 优化模式 (Optimize mode)：{status}")

    @staticmethod
    def _toggle_streaming_mode():
        """切换流式输出模式 (Toggle streaming mode)"""
        config.streaming_output = not config.streaming_output
        status = "开启/Enabled" if config.streaming_output else "关闭/Disabled"
        mode_desc = "AI回答将逐字实时显示 (Real-time display)" if config.streaming_output else "AI回答将一次性显示 (Display at once)"
        print(f"✅ 流式输出 (Streaming output)：{status}")
        print(f"   {mode_desc}")

    @staticmethod
    def _switch_language():
        """切换界面语言 / Switch interface language"""
        global CURRENT_LANGUAGE
        
        DisplayManager.print_header(get_text("language_title"))
        
        current = "中文 (Chinese)" if CURRENT_LANGUAGE == "zh" else "English (英文)"
        print(f"{get_text('current_language')}: {current}")
        print()
        print(get_text("select_language"))
        print("  1. 中文 (Chinese)")
        print("  2. English (英文)")
        print()
        
        choice = input(">>> ").strip()
        
        if choice == "1":
            CURRENT_LANGUAGE = "zh"
            config.language = "zh"
            config.save_to_file(CONFIG_FILE_PATH)  # 保存配置
            print("\n✅ 语言已切换为中文")
            print("   界面将以中文显示")
            print("   ✅ 设置已保存，下次启动自动生效")
        elif choice == "2":
            CURRENT_LANGUAGE = "en"
            config.language = "en"
            config.save_to_file(CONFIG_FILE_PATH)  # 保存配置
            print("\n✅ Language changed to English")
            print("   Interface will be displayed in English")
            print("   ✅ Settings saved, will take effect on next startup")
        else:
            if CURRENT_LANGUAGE == "en":
                print("⚠️ Invalid choice, language unchanged")
            else:
                print("⚠️ 无效选择，语言未改变")
        
        DisplayManager.print_separator()

    def _add_ai_model(self):
        """添加新的AI模型（支持本地Ollama和API）"""
        if CURRENT_LANGUAGE == "en":
            DisplayManager.print_header("➕ Add New AI Model")
            print("Select AI type:")
            print("  1. Local Ollama model")
            print("  2. API model (OpenAI compatible)")
            print("  3. Cancel")
        else:
            DisplayManager.print_header("➕ 添加新AI模型")
            print("选择AI类型：")
            print("  1. 本地Ollama模型")
            print("  2. API模型（兼容OpenAI格式）")
            print("  3. 取消")
        
        choice = input(">>> ").strip()
        
        if choice == "1":
            # 添加本地Ollama模型
            self._add_ollama_model()
        elif choice == "2":
            # 添加API模型
            self._add_api_model()
        else:
            if CURRENT_LANGUAGE == "en":
                print("⏭️ Cancelled")
            else:
                print("⏭️ 已取消")

    def _add_ollama_model(self):
        """添加本地Ollama模型"""
        if CURRENT_LANGUAGE == "en":
            print("\n📦 Available local Ollama models:")
        else:
            print("\n📦 可用的本地Ollama模型：")
        
        # 获取Ollama模型列表
        try:
            models = self.scheduler.client.get_available_models()
            if models:
                for i, model in enumerate(models, 1):
                    print(f"  {i}. {model}")
                
                if CURRENT_LANGUAGE == "en":
                    model_input = input("\nSelect model number or enter model name: ").strip()
                else:
                    model_input = input("\n选择模型编号或输入模型名称: ").strip()
                
                # 解析输入
                if model_input.isdigit():
                    idx = int(model_input)
                    if 1 <= idx <= len(models):
                        model_name = models[idx - 1]
                    else:
                        print("❌ Invalid selection" if CURRENT_LANGUAGE == "en" else "❌ 无效选择")
                        return
                else:
                    model_name = model_input
                
                # 输入AI名称
                if CURRENT_LANGUAGE == "en":
                    ai_name = input(f"Enter a name for this AI (default: {model_name}): ").strip() or model_name
                else:
                    ai_name = input(f"为这个AI起个名字（默认: {model_name}）: ").strip() or model_name
                
                # 添加到配置
                new_ai = {
                    "name": ai_name,
                    "type": "ollama",
                    "model": model_name,
                    "api_config": None
                }
                config.extra_ai_models.append(new_ai)
                config.save_to_file(CONFIG_FILE_PATH)
                
                if CURRENT_LANGUAGE == "en":
                    print(f"✅ AI model '{ai_name}' ({model_name}) added successfully!")
                else:
                    print(f"✅ AI模型 '{ai_name}' ({model_name}) 添加成功！")
            else:
                print("❌ No models found" if CURRENT_LANGUAGE == "en" else "❌ 未找到模型")
        except Exception as e:
            print(f"❌ Error: {e}")

    def _add_api_model(self):
        """添加API模型"""
        if CURRENT_LANGUAGE == "en":
            print("\n🌐 Configure API Model")
            print("\nSelect API provider:")
            print("  1. SiliconFlow (硅基流动)")
            print("  2. DeepSeek")
            print("  3. Volcengine Ark (火山引擎)")
            print("  4. OpenAI")
            print("  5. xAI (Grok)")
            print("  6. Google Gemini")
            print("  7. Anthropic Claude")
            print("  8. OpenRouter")
            print("  9. Custom (OpenAI compatible)")
        else:
            print("\n🌐 配置API模型")
            print("\n选择API提供方：")
            print("  1. 硅基流动 (SiliconFlow)")
            print("  2. DeepSeek")
            print("  3. 火山引擎 (Volcengine Ark)")
            print("  4. OpenAI")
            print("  5. xAI (Grok)")
            print("  6. Google Gemini")
            print("  7. Anthropic Claude")
            print("  8. OpenRouter (多模型聚合)")
            print("  9. 自定义（兼容OpenAI格式）")
        
        provider_choice = input(">>> ").strip() or "9"
        
        provider_map = {
            "1": ("siliconflow", "https://api.siliconflow.cn/v1"),
            "2": ("deepseek", "https://api.deepseek.com/v1"),
            "3": ("volcengine", "https://ark.cn-beijing.volces.com/api/v3"),
            "4": ("openai", "https://api.openai.com/v1"),
            "5": ("xai", "https://api.x.ai/v1"),
            "6": ("gemini", "https://generativelanguage.googleapis.com/v1beta/openai"),
            "7": ("claude", "https://api.anthropic.com/v1"),
            "8": ("openrouter", "https://openrouter.ai/api/v1"),
            "9": ("custom", "https://api.openai.com/v1"),
        }
        provider, default_base = provider_map.get(provider_choice, provider_map["9"])
        
        # 显示提供方说明
        provider_info = {
            "siliconflow": ("硅基流动", "国内平台，支持多种开源模型", "https://cloud.siliconflow.cn/"),
            "deepseek": ("DeepSeek", "国内AI，推理能力强", "https://platform.deepseek.com/"),
            "volcengine": ("火山引擎", "字节跳动旗下，豆包模型", "https://console.volcengine.com/ark"),
            "openai": ("OpenAI", "GPT系列模型", "https://platform.openai.com/"),
            "xai": ("xAI", "马斯克的Grok模型", "https://x.ai/"),
            "gemini": ("Google Gemini", "谷歌AI模型", "https://aistudio.google.com/"),
            "claude": ("Anthropic Claude", "Claude系列模型", "https://console.anthropic.com/"),
            "openrouter": ("OpenRouter", "多模型聚合平台，一个API访问多种模型", "https://openrouter.ai/"),
        }
        
        if provider in provider_info:
            name, desc, url = provider_info[provider]
            if CURRENT_LANGUAGE == "en":
                print(f"\n📌 {name}: {desc}")
                print(f"   Get API key: {url}")
            else:
                print(f"\n📌 {name}：{desc}")
                print(f"   获取API密钥：{url}")
        
        # 检查是否有已保存的密钥
        provider_key_mapping = {
            "siliconflow": config.siliconflow_api_key,
            "deepseek": config.deepseek_api_key,
            "volcengine": config.volcengine_api_key,
            "openai": getattr(config, 'openai_api_key', ''),
            "xai": getattr(config, 'xai_api_key', ''),
            "gemini": getattr(config, 'gemini_api_key', ''),
            "claude": getattr(config, 'claude_api_key', ''),
            "openrouter": getattr(config, 'openrouter_api_key', ''),
        }
        saved_key = provider_key_mapping.get(provider, "")
        
        # 配置API
        if CURRENT_LANGUAGE == "en":
            base_url = input(f"API Base URL (default: {default_base}): ").strip() or default_base
        else:
            base_url = input(f"API基础地址（默认: {default_base}）: ").strip() or default_base
        
        api_url = f"{base_url.rstrip('/')}/chat/completions"
        
        # API密钥
        if saved_key:
            if CURRENT_LANGUAGE == "en":
                print(f"🔑 Found saved API key for {provider}")
                use_saved = input("Use saved key? (Y/n): ").strip().lower() != 'n'
            else:
                print(f"🔑 找到已保存的 {provider} API密钥")
                use_saved = input("使用已保存的密钥？(Y/n): ").strip().lower() != 'n'
            
            if use_saved:
                api_key = saved_key
            else:
                api_key = input("API Key: ").strip()
        else:
            api_key = input("API Key: ").strip()
        
        if not api_key:
            print("❌ API key required" if CURRENT_LANGUAGE == "en" else "❌ 必须提供API密钥")
            return
        
        # 保存密钥到全局配置
        provider_key_attr = {
            "siliconflow": "siliconflow_api_key",
            "deepseek": "deepseek_api_key",
            "volcengine": "volcengine_api_key",
            "openai": "openai_api_key",
            "xai": "xai_api_key",
            "gemini": "gemini_api_key",
            "claude": "claude_api_key",
            "openrouter": "openrouter_api_key",
        }
        if provider in provider_key_attr:
            setattr(config, provider_key_attr[provider], api_key)
        
        # 显示推荐模型
        recommended_models = {
            "siliconflow": ["Qwen/Qwen2.5-7B-Instruct", "Qwen/Qwen2.5-32B-Instruct", "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"],
            "deepseek": ["deepseek-chat", "deepseek-reasoner"],
            "volcengine": ["doubao-pro-32k", "doubao-lite-32k"],
            "openai": ["gpt-4o", "gpt-4o-mini", "gpt-3.5-turbo", "o1-mini"],
            "xai": ["grok-beta", "grok-2-1212"],
            "gemini": ["gemini-2.0-flash-exp", "gemini-1.5-pro", "gemini-1.5-flash"],
            "claude": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
            "openrouter": ["openai/gpt-4o", "anthropic/claude-3.5-sonnet", "google/gemini-pro", "meta-llama/llama-3.1-70b-instruct"],
        }
        
        if provider in recommended_models:
            if CURRENT_LANGUAGE == "en":
                print(f"\n📋 Recommended models for {provider}:")
            else:
                print(f"\n📋 {provider} 推荐模型：")
            for i, model in enumerate(recommended_models[provider], 1):
                print(f"  {i}. {model}")
        
        # 尝试获取模型列表
        if CURRENT_LANGUAGE == "en":
            model_name = input("\nModel name (enter number or type name): ").strip()
        else:
            model_name = input("\n模型名称（输入编号或直接输入名称）: ").strip()
        
        # 如果输入的是数字，转换为模型名
        if model_name.isdigit() and provider in recommended_models:
            idx = int(model_name) - 1
            models = recommended_models[provider]
            if 0 <= idx < len(models):
                model_name = models[idx]
        
        if not model_name:
            print("❌ Model name required" if CURRENT_LANGUAGE == "en" else "❌ 必须提供模型名称")
            return
        
        # AI名称
        if CURRENT_LANGUAGE == "en":
            ai_name = input(f"Enter a name for this AI (default: {model_name}): ").strip() or model_name
        else:
            ai_name = input(f"为这个AI起个名字（默认: {model_name}）: ").strip() or model_name
        
        # 添加到配置
        new_ai = {
            "name": ai_name,
            "type": "api",
            "model": model_name,
            "api_config": {
                "provider": provider,
                "base_url": base_url,
                "api_url": api_url,
                "api_key": api_key,
                "model": model_name
            }
        }
        config.extra_ai_models.append(new_ai)
        config.save_to_file(CONFIG_FILE_PATH)
        
        if CURRENT_LANGUAGE == "en":
            print(f"✅ API AI model '{ai_name}' added successfully!")
        else:
            print(f"✅ API AI模型 '{ai_name}' 添加成功！")

    def _list_ai_models(self):
        """列出所有AI模型"""
        if CURRENT_LANGUAGE == "en":
            DisplayManager.print_header("📋 All AI Models")
            print("\n🔹 Built-in Models:")
            print(f"  1. Model 1: {config.model_1} ({'API' if config.model_1_use_api else 'Ollama'})")
            print(f"  2. Model 2: {config.model_2} ({'API' if config.model_2_use_api else 'Ollama'})")
            print(f"  3. Coordinator: {config.coordinator_model} ({'API' if config.coordinator_use_api else 'Ollama'})")
        else:
            DisplayManager.print_header("📋 所有AI模型")
            print("\n🔹 内置模型：")
            print(f"  1. 模型1: {config.model_1} ({'API' if config.model_1_use_api else 'Ollama'})")
            print(f"  2. 模型2: {config.model_2} ({'API' if config.model_2_use_api else 'Ollama'})")
            print(f"  3. 协调模型: {config.coordinator_model} ({'API' if config.coordinator_use_api else 'Ollama'})")
        
        if config.extra_ai_models:
            if CURRENT_LANGUAGE == "en":
                print("\n🔸 Additional Models:")
            else:
                print("\n🔸 额外添加的模型：")
            for i, ai in enumerate(config.extra_ai_models, 1):
                ai_type = ai.get("type", "unknown")
                ai_name = ai.get("name", "Unknown")
                model = ai.get("model", "Unknown")
                print(f"  {i}. {ai_name} ({model}) [{ai_type.upper()}]")
        else:
            if CURRENT_LANGUAGE == "en":
                print("\n🔸 No additional models added. Use /addai to add more.")
            else:
                print("\n🔸 暂无额外添加的模型。使用 /addai 添加更多。")
        
        DisplayManager.print_separator()

    def _remove_ai_model(self):
        """移除AI模型"""
        if not config.extra_ai_models:
            if CURRENT_LANGUAGE == "en":
                print("❌ No additional AI models to remove")
            else:
                print("❌ 没有可移除的额外AI模型")
            return
        
        if CURRENT_LANGUAGE == "en":
            DisplayManager.print_header("➖ Remove AI Model")
            print("Select model to remove:")
        else:
            DisplayManager.print_header("➖ 移除AI模型")
            print("选择要移除的模型：")
        
        for i, ai in enumerate(config.extra_ai_models, 1):
            print(f"  {i}. {ai.get('name', 'Unknown')} ({ai.get('model', '')})")
        
        if CURRENT_LANGUAGE == "en":
            print(f"  0. Cancel")
        else:
            print(f"  0. 取消")
        
        choice = input(">>> ").strip()
        
        if choice == "0" or not choice:
            return
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(config.extra_ai_models):
                removed = config.extra_ai_models.pop(idx)
                config.save_to_file(CONFIG_FILE_PATH)
                if CURRENT_LANGUAGE == "en":
                    print(f"✅ Model '{removed.get('name', '')}' removed")
                else:
                    print(f"✅ 模型 '{removed.get('name', '')}' 已移除")
            else:
                print("❌ Invalid selection" if CURRENT_LANGUAGE == "en" else "❌ 无效选择")
        else:
            print("❌ Invalid input" if CURRENT_LANGUAGE == "en" else "❌ 无效输入")

    @staticmethod
    def _show_roles():
        """显示可用角色 (Show available roles)"""
        print("\n🎭 可用角色 (Available roles) [支持输入数字选择/Select by number]：")
        roles = role_system.get_all_roles()
        for i, role in enumerate(roles, 1):
            print(f"  {i}. {role}")

    @staticmethod
    def _show_tags():
        """显示标签系统 (Show tag system)"""
        print("\n🏷️  标签系统 (Tag System)：")
        for tag, roles in TAG_TO_ROLES.items():
            print(f"  {tag}: {', '.join(roles)}")

    @staticmethod
    def _configure_consensus():
        """配置共识检测 (Configure consensus detection)"""
        print("\n🎯 共识检测配置 (Consensus Detection Config)")
        ai_status = "开启/On" if config.ai_consensus_analysis else "关闭/Off"
        sum_status = "开启/On" if config.auto_summarize_at_threshold else "关闭/Off"
        print(f"当前设置 (Current settings)：")
        print(f"  - AI共识分析 (AI consensus analysis): {ai_status}")
        print(f"  - 自动总结 (Auto summary): {sum_status}")
        print(f"  - 共识阈值 (Consensus threshold): {int(config.consensus_threshold * 100)}%")
        print(f"  - 检测起始回合 (Start round): {config.consensus_check_start_round}")

        print(f"\n选项 (Options)：")
        ai_cur = "开/On" if config.ai_consensus_analysis else "关/Off"
        sum_cur = "开/On" if config.auto_summarize_at_threshold else "关/Off"
        print(f"  1. 切换AI共识分析 (Toggle AI analysis) [当前/Current: {ai_cur}]")
        print(f"  2. 切换自动总结 (Toggle auto summary) [当前/Current: {sum_cur}]")
        print(f"  3. 设置共识阈值 (Set threshold) [当前/Current: {int(config.consensus_threshold * 100)}%]")
        print(f"  4. 设置检测起始回合 (Set start round) [当前/Current: {config.consensus_check_start_round}]")

        choice = input("选择/Select (1-4) 或回车返回/Enter to return: ").strip()

        if choice == '1':
            config.ai_consensus_analysis = not config.ai_consensus_analysis
            status = "开启/Enabled" if config.ai_consensus_analysis else "关闭/Disabled"
            print(f"✅ AI共识分析 (AI consensus analysis)：{status}")
        elif choice == '2':
            config.auto_summarize_at_threshold = not config.auto_summarize_at_threshold
            status = "开启/Enabled" if config.auto_summarize_at_threshold else "关闭/Disabled"
            print(f"✅ 自动总结 (Auto summary)：{status}")
        elif choice == '3':
            try:
                threshold = float(input("输入新阈值/Enter new threshold (0-100): ").strip()) / 100.0
                if 0.0 <= threshold <= 1.0:
                    config.consensus_threshold = threshold
                    print(f"✅ 共识阈值已设置为 (Threshold set to) {int(threshold * 100)}%")
                else:
                    print("❌ 阈值必须在 0-100 之间 (Threshold must be 0-100)")
            except ValueError:
                print("❌ 请输入有效的数字 (Please enter a valid number)")
        elif choice == '4':
            try:
                round_num = int(input("输入起始回合数/Enter start round (1-6): ").strip())
                if 1 <= round_num <= 6:
                    config.consensus_check_start_round = round_num
                    print(f"✅ 检测起始回合已设置为第{round_num}回合 (Start round set to {round_num})")
                else:
                    print("❌ 回合数必须在 1-6 之间 (Round must be 1-6)")
            except ValueError:
                print("❌ 请输入有效的数字 (Please enter a valid number)")
        elif choice == '':
            return
        else:
            print("❌ 无效选择 (Invalid selection)")

    @staticmethod
    def _toggle_coordination_mode():
        """切换协调模式 (Toggle coordination mode)"""
        current = config.coordination_mode
        new_mode = "user" if current == "auto" else "auto"
        config.coordination_mode = new_mode
        print(f"✅ 协调模式已切换 (Coordination mode switched)：{current} -> {new_mode}")

    def _handle_interrupt(self):
        """处理中断信号 (Handle interrupt signal)"""
        print("\n\n⚠️ 检测到中断信号 (Interrupt signal detected)")
        choice = input("是否退出程序？(Exit program?) (y/N): ").strip().lower()
        if choice == 'y':
            self._exit_program()

    def _configure_api_mode(self):
        """配置API模式 (Configure API mode)"""
        DisplayManager.print_header("🔗 API模式配置 (API Mode Configuration)")
        api_status = "已启用/Enabled" if config.api_mode_enabled else "未启用/Disabled"
        key_status = "已设置/Set" if config.api_key else "未设置/Not set"
        m1_api = "是/Yes" if config.model_1_use_api else "否/No"
        m2_api = "是/Yes" if config.model_2_use_api else "否/No"
        coord_api = "是/Yes" if config.coordinator_use_api else "否/No"
        
        print(f"当前API模式状态 (Current API mode)：{api_status}")
        print(f"API提供方 (API Provider)：{getattr(config, 'api_provider', 'custom')}")
        print(f"API基础地址 (API Base URL)：{getattr(config, 'api_base_url', '')}")
        print(f"API地址 (API URL)：{config.api_url}")
        print(f"API模型 (API Model)：{config.api_model}")
        print(f"API密钥 (API Key)：{key_status}")
        print(f"模型1使用API (Model 1 uses API)：{m1_api}")
        print(f"模型2使用API (Model 2 uses API)：{m2_api}")
        print(f"协调AI使用API (Coordinator uses API)：{coord_api}")
        DisplayManager.print_separator()
        enable_api = InputValidator.get_yes_no_input("是否启用API模式？(Enable API mode?) (y/n): ", default=config.api_mode_enabled)
        if enable_api:
            # 逐个配置：模型1、模型2、协调AI
            any_use_api = False
            if CURRENT_LANGUAGE == "en":
                targets = [
                    ("Model 1", "model_1"),
                    ("Model 2", "model_2"),
                    ("Coordinator", "coordinator"),
                ]
            else:
                targets = [
                    ("模型1", "model_1"),
                    ("模型2", "model_2"),
                    ("协调AI", "coordinator"),
                ]

            for label, key in targets:
                print("\n" + "-" * 40)
                if CURRENT_LANGUAGE == "en":
                    print(f"⚙️  Configure API for {label}")
                else:
                    print(f"⚙️  配置 {label} 的API参数")
                use_api_attr = f"{key}_use_api"
                current_use = getattr(config, use_api_attr, False)
                if CURRENT_LANGUAGE == "en":
                    use_api = InputValidator.get_yes_no_input(
                        f"Use external API for {label}? (Current: {'Yes' if current_use else 'No'})", default=current_use
                    )
                else:
                    use_api = InputValidator.get_yes_no_input(
                        f"{label} 是否使用外部API？（当前: {'是' if current_use else '否'}）", default=current_use
                    )
                setattr(config, use_api_attr, use_api)

                if not use_api:
                    continue

                any_use_api = True

                # 选择提供方
                provider_attr = f"{key}_api_provider"
                base_attr = f"{key}_api_base_url"
                url_attr = f"{key}_api_url"
                key_attr = f"{key}_api_key"
                model_attr = f"{key}_api_model"

                current_provider = getattr(config, provider_attr, "") or "custom"
                if CURRENT_LANGUAGE == "en":
                    print(f"\n🏢 Select API provider for {label} (Current: {current_provider}):")
                    print("  1. SiliconFlow")
                    print("  2. DeepSeek")
                    print("  3. Volcengine Ark")
                    print("  4. Custom (OpenAI compatible)")
                    provider_choice = input("Enter number (1-4, Enter for current/custom): ").strip() or "4"
                else:
                    print(f"\n🏢 为 {label} 选择API提供方（当前: {current_provider}）：")
                    print("  1. 硅基流动 (SiliconFlow)")
                    print("  2. DeepSeek")
                    print("  3. 火山引擎 (Volcengine Ark)")
                    print("  4. 自定义 (兼容OpenAI格式)")
                    provider_choice = input("输入编号(1-4，回车保持当前/自定义): ").strip() or "4"

                provider_map = {
                    "1": ("siliconflow", "https://api.siliconflow.cn/v1"),
                    "2": ("deepseek", "https://api.deepseek.com/v1"),
                    "3": ("volcengine", "https://ark.cn-beijing.volces.com/api/v3"),
                    "4": (current_provider or "custom", getattr(config, base_attr, "") or getattr(config, "api_base_url", "https://api.openai.com/v1") or "https://api.openai.com/v1"),
                }
                provider, default_base = provider_map.get(provider_choice, provider_map["4"])
                setattr(config, provider_attr, provider)

                # 检查是否有该提供方的已保存密钥（从全局或其他模型配置中查找）
                saved_keys_for_provider = {}
                provider_key_mapping = {
                    "siliconflow": "siliconflow_api_key",
                    "deepseek": "deepseek_api_key", 
                    "volcengine": "volcengine_api_key",
                }
                
                # 查找已保存的密钥
                global_saved_key = getattr(config, provider_key_mapping.get(provider, ""), "")
                existing_key_for_this = getattr(config, key_attr, "")
                
                # 从其他模型配置中查找同一提供方的密钥
                for other_key in ["model_1", "model_2", "coordinator"]:
                    if other_key != key:
                        other_provider = getattr(config, f"{other_key}_api_provider", "")
                        if other_provider == provider:
                            other_key_value = getattr(config, f"{other_key}_api_key", "")
                            if other_key_value:
                                saved_keys_for_provider[other_key] = other_key_value
                
                # 配置基础地址
                current_base = getattr(config, base_attr, "") or default_base
                if CURRENT_LANGUAGE == "en":
                    print("\n🔧 Configure API Base URL:")
                    base_url = input(f"{label} API Base URL (Current: {current_base}): ").strip()
                else:
                    print("\n🔧 配置API基础地址：")
                    base_url = input(f"{label} API基础地址 (当前: {current_base}): ").strip()
                if not base_url:
                    base_url = current_base
                base_url = base_url.rstrip("/")
                setattr(config, base_attr, base_url)

                # chat completions endpoint
                default_chat_url = f"{base_url}/chat/completions"
                current_chat = getattr(config, url_attr, "") or default_chat_url
                if CURRENT_LANGUAGE == "en":
                    api_url = input(f"{label} ChatCompletions URL (Current: {current_chat}): ").strip()
                else:
                    api_url = input(f"{label} ChatCompletions地址 (当前: {current_chat}): ").strip()
                api_url = (api_url or current_chat).rstrip("/")
                setattr(config, url_attr, api_url)

                # API Key：提供使用已保存密钥或输入新密钥的选项
                existing_key = existing_key_for_this or global_saved_key or config.api_key
                
                # 如果有已保存的密钥（来自同一提供方的其他配置）
                if saved_keys_for_provider or existing_key:
                    if CURRENT_LANGUAGE == "en":
                        print(f"\n🔑 API Key Configuration:")
                        print("  1. Use saved key" + (" ✅ Key exists" if existing_key else ""))
                        if saved_keys_for_provider:
                            print(f"     (Same provider configured for: {', '.join(saved_keys_for_provider.keys())})")
                        print("  2. Enter new key")
                        key_choice = input("Select (1/2, Enter for saved): ").strip() or "1"
                    else:
                        print(f"\n🔑 API密钥配置：")
                        print("  1. 使用已保存的密钥" + (" ✅ 当前已有密钥" if existing_key else ""))
                        if saved_keys_for_provider:
                            print(f"     (同提供方其他模型已配置: {', '.join(saved_keys_for_provider.keys())})")
                        print("  2. 输入新的密钥")
                        key_choice = input("请选择 (1/2，回车使用已保存): ").strip() or "1"
                    
                    if key_choice == "2":
                        if CURRENT_LANGUAGE == "en":
                            api_key_input = input(f"Enter API key for {label}: ").strip()
                        else:
                            api_key_input = input(f"请输入 {label} 的API密钥: ").strip()
                        if api_key_input:
                            setattr(config, key_attr, api_key_input)
                            # 同时保存到提供方全局密钥
                            if provider in provider_key_mapping:
                                setattr(config, provider_key_mapping[provider], api_key_input)
                            existing_key = api_key_input
                    else:
                        # 使用已保存的密钥
                        if not existing_key and saved_keys_for_provider:
                            # 使用同一提供方其他模型的密钥
                            existing_key = list(saved_keys_for_provider.values())[0]
                        if existing_key:
                            setattr(config, key_attr, existing_key)
                            if CURRENT_LANGUAGE == "en":
                                print(f"   ✅ Using saved key")
                            else:
                                print(f"   ✅ 已使用保存的密钥")
                else:
                    # 没有已保存的密钥，直接输入
                    if CURRENT_LANGUAGE == "en":
                        api_key_input = input(f"{label} API Key: ").strip()
                    else:
                        api_key_input = input(f"{label} API密钥: ").strip()
                    if api_key_input:
                        setattr(config, key_attr, api_key_input)
                        # 同时保存到提供方全局密钥
                        if provider in provider_key_mapping:
                            setattr(config, provider_key_mapping[provider], api_key_input)
                        existing_key = api_key_input

                # 先尝试拉取该提供方的模型列表
                models: List[str] = []
                if existing_key:
                    temp_client = APIClient(api_url=api_url, api_key=existing_key,
                                            model_name=getattr(config, model_attr, "") or config.api_model,
                                            timeout=config.timeout)
                    models = temp_client.list_models()

                current_model = getattr(config, model_attr, "") or config.api_model
                if models:
                    if CURRENT_LANGUAGE == "en":
                        print("\n📦 Available models:")
                    else:
                        print("\n📦 获取到可用模型：")
                    for i, mid in enumerate(models, 1):
                        print(f"  {i}. {mid}")
                    if CURRENT_LANGUAGE == "en":
                        model_choice = input(f"{label} Select model (1-{len(models)}), or enter name (Enter to keep {current_model}): ").strip()
                    else:
                        model_choice = input(f"{label} 选择模型编号(1-{len(models)})，或直接输入模型名(回车保留当前 {current_model}): ").strip()
                    if model_choice.isdigit():
                        idx = int(model_choice)
                        if 1 <= idx <= len(models):
                            setattr(config, model_attr, models[idx - 1])
                    elif model_choice:
                        setattr(config, model_attr, model_choice)
                else:
                    if CURRENT_LANGUAGE == "en":
                        print(f"\n⚠️  Cannot auto-fetch model list for {label} (platform may not support /models, or key/network issue).")
                        api_model_input = input(f"Enter model name for {label} (Current: {current_model}): ").strip()
                    else:
                        print(f"\n⚠️  无法自动获取 {label} 的模型列表（该平台可能不支持 /models，或Key/网络问题）。")
                        api_model_input = input(f"请输入 {label} 使用的模型名称 (当前: {current_model}): ").strip()
                    if api_model_input:
                        setattr(config, model_attr, api_model_input)

            # 若至少有一个AI使用API，则认为API模式开启
            config.api_mode_enabled = any_use_api
            if not any_use_api:
                if CURRENT_LANGUAGE == "en":
                    print("⚠️  No AI configured to use API, disabling API mode, using local Ollama only.")
                else:
                    print("⚠️  所有AI都未配置使用API，将关闭API模式，仅使用本地Ollama。")

            # 保存配置
            config.save_to_file("macp_config.json")
            if CURRENT_LANGUAGE == "en":
                print("✅ API configuration saved")
            else:
                print("✅ API配置已保存")

            # 重新初始化调度器以应用新配置
            if CURRENT_LANGUAGE == "en":
                print("\n🔄 Reinitializing system...")
            else:
                print("\n🔄 正在重新初始化系统...")
            try:
                # 重新创建调度器实例
                new_scheduler = AICouncilScheduler()
                self.scheduler = new_scheduler
                if CURRENT_LANGUAGE == "en":
                    print("✅ System reinitialized successfully")
                else:
                    print("✅ 系统重新初始化完成")
            except (AICouncilException, requests.exceptions.RequestException, ValueError) as e:
                print(f"❌ 重新初始化失败 (Reinitialization failed): {e}")

        else:
            config.api_mode_enabled = False
            print("✅ 已禁用API模式 (API mode disabled)")

        DisplayManager.print_separator()

    def _exit_program(self):
        """退出程序 (Exit program)"""
        print(f"\n📊 会话统计 (Session Statistics)：")
        print(f"  会话ID (Session ID)：{self.scheduler.session_id}")
        print(f"  总记录数 (Total Records)：{len(self.scheduler.history_manager.history)}")
        print("\n👋 再见！(Goodbye!)")

        # 清理资源
        self.scheduler.cleanup()

        sys.exit(0)

    def _select_debate_roles(self) -> Tuple[str, str]:
        """选择辩论角色"""
        self._show_roles()
        role1_input = input(f"\n模型1角色（默认：{config.default_role_1}）: ").strip()
        role2_input = input(f"模型2角色（默认：{config.default_role_2}）: ").strip()

        role1 = InputValidator.validate_role_input(role1_input, role_system.get_all_roles())
        role2 = InputValidator.validate_role_input(role2_input, role_system.get_all_roles())
        return role1, role2

    @staticmethod
    def _handle_consensus_feedback(consensus_score: float, consensus_percentage: int,
                                 threshold_percentage: int, current_consensus_reached: bool) -> bool:
        """处理AI共识分析结果并决定辩论进程

        根据AI的共识分析结果向用户展示当前辩论状态：
        1. 显示共识度条形图（视觉化表示）
        2. 根据共识度给出不同的进度反馈
        3. 检查是否达到自动结束阈值（70%）
        4. 返回是否应该结束辩论的决策

        这是实现"智能辩论结束"的关键环节，
        让系统能够根据AI的语义理解做出合理决策
        """
        if consensus_score >= config.consensus_threshold:
            logger.info(f"✅ 共识度达标 ({consensus_percentage}%)，自动结束辩论")
            print(f"\n🎯 共识度已达到{consensus_percentage}%（≥{threshold_percentage}%阈值），自动结束辩论并生成总结")
            return True
        elif consensus_score >= 0.5:
            remaining_to_threshold = threshold_percentage - consensus_percentage
            print(f"📈 共识度{consensus_percentage}%，距离阈值还差{remaining_to_threshold}%，辩论继续...")
        else:
            print(f"⚖️  共识度{consensus_percentage}%，分歧明显，继续深入辩论...")

        return current_consensus_reached

# ==================== 【主函数】 ====================
def main():
    """MACP系统主入口函数

    执行完整的系统初始化和运行流程：
    1. 显示系统信息和版本号
    2. 初始化AICouncilScheduler（核心调度器）
    3. 创建InteractiveInterface（用户界面）
    4. 启动交互式命令循环
    5. 处理系统异常和清理资源

    这是整个应用程序的启动点，负责协调所有组件的初始化
    """
    print("🚀 启动MACP多AI协作平台 v5.0 - 终极优化版")
    print("=" * 80)
    print("新增功能：")
    print("1. ✅ 模块化架构 - 代码更清晰")
    print("2. ✅ 增强错误处理 - 更稳定")
    print("3. ✅ 日志系统 - 便于调试")
    print("4. ✅ 性能监控 - 实时跟踪")
    print("5. ✅ 配置管理 - 动态加载")
    print("6. ✅ 代码优化 - 减少冗余")
    print("7. ✅ 类型注解 - 更好的维护性")
    print("=" * 80)

    try:
        # 初始化调度器
        scheduler = AICouncilScheduler()

        # 启动交互界面
        interface = InteractiveInterface(scheduler)
        interface.run()

    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        logger.error(f"程序运行时发生严重错误: {e}", exc_info=e)
        print(f"\n❌ 程序运行时发生严重错误: {e}")
        print("请检查日志文件以获取详细信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
