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
from typing import Dict, Any, List, Optional, Tuple

# ==================== 【依赖检查】 ====================
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

    def __init__(self, log_file: str = "macp.log", level: int = logging.INFO):
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
            # 控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.level)
            console_handler.setFormatter(log_format)
            self.logger.addHandler(console_handler)

            # 文件处理器
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
        self.streaming_output = True                  # 是否启用流式输出

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

# 创建全局配置实例，整个系统共享同一份配置
config = Config()

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
    "情感体验": ["叙事导演", "玩家代表", "魔鬼代言人"],     # 情感体验、用户感受相关
    "技术实现": ["系统架构师", "项目经理", "魔鬼代言人"],   # 技术实现、工程开发相关
    "用户体验": ["玩家代表", "叙事导演", "系统架构师"],     # 用户界面、交互体验相关
    "法律合规": ["律师", "项目经理", "魔鬼代言人"],         # 法律合规、知识产权相关
    "伦理道德": ["哲学家", "律师", "魔鬼代言人"],           # 伦理道德、价值观相关
    "辩论技巧": ["辩论手", "律师", "魔鬼代言人"]            # 辩论技巧、论证逻辑相关
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
    "辩论技巧": ["辩论", "争论", "讨论", "反驳", "论证", "逻辑"]
}

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
        "辩手": "辩论手"
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
                                    timeout: int = 90) -> Dict[str, Any]:
        """生成流式模型响应"""
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

            # 处理流式响应
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

    def generate_response(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> Dict[str, Any]:
        """生成AI响应

        Args:
            prompt: 提示词
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            包含响应信息的字典
        """
        start_time = time.time()

        try:
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
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

        # 构造显示名：模型名-角色名
        display_name1 = f"{self.config.model_1}-{role1}"
        display_name2 = f"{self.config.model_2}-{role2}"

        role_prompt1 = role_system.get_role_prompt(role1, is_first=True)   # 正方
        role_prompt2 = role_system.get_role_prompt(role2, is_first=False)  # 反方

        if not role_prompt1 or not role_prompt2:
            raise InvalidRoleError(f"无效角色: {role1} 或 {role2}")

        self._setup_debate_roles(question, role1, role2)

        # 第一回合：双方知道对手是谁，但看不到具体观点
        DisplayManager.print_separator("-", 40)
        print("第1回合：初始陈述")
        DisplayManager.print_separator("-", 40)
        print(f"💡 {role1} vs {role2} - 双方已知晓对手身份")

        # 增强版第一回合提示词 - 让AI知道对手是谁，并要求简洁表达
        prompt1 = f"""{role_prompt1}

【辩论主题】: {question}

【你的立场】: {role1}（正方）
【对手角色】: {role2}（反方）

请简洁有力地阐述你的核心观点（重点突出3-5个关键论点）：
"""

        prompt2 = f"""{role_prompt2}

【辩论主题】: {question}

【你的立场】: {role2}（反方）
【对手角色】: {role1}（正方）

请简洁有力地阐述你的核心观点（重点突出3-5个关键论点）：
"""

        # 使用正确的客户端进行提问
        client1, model_id1, is_api1 = self._get_client_for_model(self.config.model_1)
        client2, model_id2, is_api2 = self._get_client_for_model(self.config.model_2)

        if is_api1:
            result1 = client1.generate_response(prompt1, max_tokens=500, temperature=self.config.temperature)
        else:
            result1 = client1.generate_response(self.config.model_1, prompt1, max_tokens=500,
                                              temperature=self.config.temperature, timeout=self.config.timeout,
                                              streaming=self.config.streaming_output)

        if is_api2:
            result2 = client2.generate_response(prompt2, max_tokens=500, temperature=self.config.temperature)
        else:
            result2 = client2.generate_response(self.config.model_2, prompt2, max_tokens=500,
                                              temperature=self.config.temperature, timeout=self.config.timeout,
                                              streaming=self.config.streaming_output)

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

        self._display_debate_response(display_name1, response1)
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
                logger.info(f"🔄 AI共识分析: {consensus_percentage}% - {analysis}")

                # 显示共识度条形图
                ConsensusDetector.display_consensus_bar(consensus_percentage)

                print(f"📝 AI分析: {analysis}")

                # 显示详细分析（如果有）
                if analysis_data:
                    if 'key_agreements' in analysis_data and analysis_data['key_agreements']:
                        agreements = analysis_data['key_agreements'][:3]
                        print(f"🤝 共识点: {len(agreements)}项")
                        for i, agreement in enumerate(agreements, 1):
                            print(f"   {i}. {agreement}")

                    if 'key_disagreements' in analysis_data and analysis_data['key_disagreements']:
                        disagreements = analysis_data['key_disagreements'][:3]
                        print(f"⚔️  分歧点: {len(disagreements)}项")
                        for i, disagreement in enumerate(disagreements, 1):
                            print(f"   {i}. {disagreement}")

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
            print(f"第{round_num}回合：互相回应")
            DisplayManager.print_separator("-", 40)

            # 构建辩论历史上下文
            debate_history = AICouncilScheduler._build_debate_context(debate_round, display_name1, display_name2)

            # 模型1回应模型2 - 增强版：看到完整上下文
            if result1.get("success") and result2.get("success"):
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
                if is_api1:
                    result1 = client1.generate_response(rebuttal_prompt1, max_tokens=600, temperature=self.config.temperature)
                else:
                    result1 = client1.generate_response(self.config.model_1, rebuttal_prompt1, max_tokens=600,
                                                      temperature=self.config.temperature, timeout=self.config.timeout,
                                                      streaming=self.config.streaming_output)

                if result1.get("success"):
                    response1 = result1.get("response", "")
                    debate_round.append({
                        "round": round_num,
                        "speaker": display_name1,
                        "content": response1,
                        "type": "rebuttal"
                    })
                    self._display_debate_response(display_name1, response1, f"反驳{role2}")

            # 模型2回应模型1 - 增强版：看到完整上下文
            if result1.get("success") and result2.get("success"):
                # 更新辩论历史，包含最新的AI1回应
                debate_history = AICouncilScheduler._build_debate_context(debate_round, display_name1, display_name2)

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
                if is_api2:
                    result2 = client2.generate_response(rebuttal_prompt2, max_tokens=600, temperature=self.config.temperature)
                else:
                    result2 = client2.generate_response(self.config.model_2, rebuttal_prompt2, max_tokens=600,
                                                      temperature=self.config.temperature, timeout=self.config.timeout,
                                                      streaming=self.config.streaming_output)

                if result2.get("success"):
                    response2 = result2.get("response", "")
                    debate_round.append({
                        "round": round_num,
                        "speaker": display_name2,
                        "content": response2,
                        "type": "rebuttal"
                    })
                    self._display_debate_response(display_name2, response2, f"反驳{role1}")

        # 协调阶段
        DisplayManager.print_header("🎯 协调总结")

        if consensus_reached:
            print("🤝 双方已达成高度共识，生成最终总结")
            self._generate_consensus_summary(question, debate_round, role1, role2, consensus_analysis)
        else:
            self._coordinate_responses(question, debate_round, role1, role2)

        # 保存记录
        if self.config.save_history:
            self._save_debate_entry(question, debate_round, display_name1, display_name2)

        # 返回完整的辩论记录，让用户可以看到所有发言
        return debate_round

    def _generate_consensus_summary(self, question: str, debate_round: List[Dict[str, Any]],
                                   role1: str, role2: str, consensus_analysis: str) -> str:
        """生成辩论共识总结报告

        当辩论达到共识阈值时，调用协调AI生成专业的总结报告：
        1. 整理完整的辩论过程和共识分析结果
        2. 要求AI生成结构化的总结报告
        3. 包含辩论回顾、共识评估、双方观点对比和综合结论

        这是MACP系统的核心价值之一，能够将AI辩论转化为
        有价值的分析报告，帮助用户深入理解辩论主题
        """
        print(f"\n🤖 协调AI ({self.config.coordinator_model}) 正在生成最终总结...")

        # 构建辩论摘要
        debate_summary = ""
        for entry in debate_round[-6:]:  # 最后6轮对话
            debate_summary += f"\n{entry['speaker']}: {entry.get('content', '')[:200]}"

        summary_prompt = f"""基于以下辩论过程和共识分析，请生成最终总结报告：

【辩论主题】: {question}
【辩论双方】: {role1} vs {role2}
【共识分析】: {consensus_analysis}

【辩论过程摘要】:
{debate_summary}

请生成结构化的总结报告，包含：

## 🎯 辩论总结

### 📊 共识评估
- 最终共识度：XX%
- 达成共识的主要方面
- 仍存在的分歧点

### 🗣️ 双方观点对比
- {role1}的核心立场
- {role2}的核心立场
- 双方观点的演变过程

### 💡 综合结论
- 对原问题的最终答案
- 建设性建议和解决方案

### 📈 辩论质量评估
- 论证逻辑性
- 观点深度
- 沟通有效性

请确保总结客观、中立，并基于双方的实际论述。"""

        # 调试信息
        logger.info(f"共识总结调试 - 问题: {question}")
        logger.info(f"共识总结调试 - 辩论轮数: {len(debate_round)}")
        logger.info(f"共识总结调试 - 共识分析长度: {len(consensus_analysis)}")
        logger.info(f"共识总结调试 - 协调模型: {self.config.coordinator_model}")

        coord_client, coord_model, is_api = self._get_client_for_model(self.config.coordinator_model)
        if is_api:
            summary_result = coord_client.generate_response(summary_prompt, max_tokens=1000, temperature=self.config.temperature)
        else:
            summary_result = coord_client.generate_response(coord_model, summary_prompt, max_tokens=1000,
                                                          temperature=self.config.temperature, timeout=self.config.timeout,
                                                          streaming=False)

        # 详细调试信息
        logger.info(f"共识总结调试 - 请求结果: {summary_result}")
        logger.info(f"共识总结调试 - 成功状态: {summary_result.get('success')}")
        logger.info(f"共识总结调试 - 响应长度: {len(summary_result.get('response', ''))}")

        if summary_result.get("success"):
            summary = summary_result.get("response", "")
            logger.info(f"共识总结调试 - 响应内容: {summary[:200]}...")

            if not summary.strip():
                logger.warning("共识总结调试 - 响应内容为空")
                print("⚠️  共识总结AI返回了空响应")
                return f"基于共识分析的总结：{consensus_analysis}\n\n辩论已自动结束，双方达成高度共识。"

            print(f"\n✅ 共识总结生成完成：")
            print(summary[:self.config.display_length] +
                  ("..." if len(summary) > self.config.display_length else ""))
            return summary
        else:
            logger.warning(f"共识总结生成失败 - 错误详情: {summary_result}")
            print(f"❌ 共识总结生成失败 - 详情: {summary_result.get('error', '未知错误')}")
            return f"基于共识分析的总结：{consensus_analysis}\n\n辩论已自动结束，双方达成高度共识。"

    def _coordinate_responses(self, question: str, debate_round: List[Dict[str, Any]],
                            role1: str, role2: str) -> str:
        """协调辩论结果"""
        print(f"\n🤖 协调AI ({self.config.coordinator_model}) 正在分析...")

        # 构建摘要
        debate_summary = ""
        for entry in debate_round[:4]:  # 只取前4轮
            debate_summary += f"\n{entry['speaker']}: {entry.get('content', '')[:150]}"

        coord_prompt = f"""请作为中立协调员分析以下辩论：
问题：{question}
辩论双方：{role1} vs {role2}
辩论摘要：{debate_summary}

请提供简要分析（限{self.config.max_tokens}token）：
1. 核心共识点
2. 主要分歧
3. 综合建议"""

        # 调试信息
        logger.info(f"协调AI调试 - 问题: {question}")
        logger.info(f"协调AI调试 - 辩论轮数: {len(debate_round)}")
        logger.info(f"协调AI调试 - 摘要长度: {len(debate_summary)}")
        logger.info(f"协调AI调试 - 协调模型: {self.config.coordinator_model}")

        coord_client, coord_model, is_api = self._get_client_for_model(self.config.coordinator_model)
        if is_api:
            coord_result = coord_client.generate_response(coord_prompt, max_tokens=800, temperature=self.config.temperature)
        else:
            coord_result = coord_client.generate_response(coord_model, coord_prompt, max_tokens=800,
                                                        temperature=self.config.temperature, timeout=self.config.timeout,
                                                        streaming=False)

        # 详细调试信息
        logger.info(f"协调AI调试 - 请求结果: {coord_result}")
        logger.info(f"协调AI调试 - 成功状态: {coord_result.get('success')}")
        logger.info(f"协调AI调试 - 响应长度: {len(coord_result.get('response', ''))}")

        if coord_result.get("success"):
            coord_response = coord_result.get("response", "")
            logger.info(f"协调AI调试 - 响应内容: {coord_response[:200]}...")

            if not coord_response.strip():
                logger.warning("协调AI调试 - 响应内容为空")
                print("⚠️  协调AI返回了空响应")
                return "协调AI返回了空响应，请检查模型配置"

            print(f"\n✅ 协调AI分析完成：")
            print(coord_response[:self.config.display_length] +
                  ("..." if len(coord_response) > self.config.display_length else ""))
            return coord_response
        else:
            logger.warning(f"协调AI分析失败 - 错误详情: {coord_result}")
            print(f"❌ 协调AI分析失败 - 详情: {coord_result.get('error', '未知错误')}")
            return f"协调分析失败: {coord_result.get('error', '未知错误')}"

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

        while True:
            try:
                user_input = input(f"\n请输入问题或命令：").strip()

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
                print(f"❌ 发生错误：{e}")

    @staticmethod
    def _print_welcome():
        """打印欢迎信息"""
        DisplayManager.print_header("🤖 MACP 多AI协作平台 v5.0")

        print(f"模型1：{config.model_1}")
        print(f"模型2：{config.model_2}")
        print(f"协调模型：{config.coordinator_model}")
        print(f"优化模式：{'开启' if config.optimize_memory else '关闭'}")
        DisplayManager.print_separator()

    @staticmethod
    def _print_commands():
        """打印可用命令"""
        print("\n📋 可用命令：")
        commands = [
            ("help", "显示帮助"),
            ("models", "查看可用模型"),
            ("config", "查看当前配置"),
            ("history", "查看历史记录"),
            ("api", "配置API模式"),
            ("debate", "进入辩论模式"),
            ("turtle", "进入海龟汤模式"),
            ("consensus", "配置共识检测"),
            ("streaming", "切换流式输出模式"),
            ("optimize", "开启优化模式"),
            ("roles", "查看可用角色"),
            ("tags", "查看标签系统"),
            ("mode", "切换协调模式（auto/user）"),
            ("clear", "清屏"),
            ("exit", "退出程序")
        ]

        for cmd, desc in commands:
            print(f"  /{cmd:<12} - {desc}")
        DisplayManager.print_separator()

    def _handle_question(self, question: str):
        """处理问题输入"""
        print(f"\n🔍 正在处理问题...")
        self.scheduler.progress_tracker.start()

        try:
            self.scheduler.ask_both_models(question, mode="parallel")
            total_time = self.scheduler.progress_tracker.get_elapsed_time()
            print(f"\n✅ 总耗时：{total_time:.2f}秒")
        except Exception as e:
            logger.error(f"处理问题失败: {e}")
            print(f"❌ 处理问题失败: {e}")

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
            'turtle': self._enter_turtle_soup_mode,
            'consensus': self._configure_consensus,
            'optimize': self._toggle_optimize_mode,
            'roles': self._show_roles,
            'tags': self._show_tags,
            'mode': self._toggle_coordination_mode,
            'streaming': self._toggle_streaming_mode,
            'clear': DisplayManager.clear_screen,
            'exit': self._exit_program
        }

        handler = handlers.get(command)
        if handler:
            try:
                handler()
            except Exception as e:
                logger.error(f"执行命令 /{command} 失败: {e}")
                print(f"❌ 执行命令失败: {e}")
        else:
            print(f"❌ 未知命令：/{command}")

    def _show_models(self):
        """显示可用模型"""
        print("\n📦 检查可用模型...")
        models = self.scheduler.client.list_models()
        print(DisplayManager.format_model_list(models))

    @staticmethod
    def _show_config():
        """显示当前配置"""
        config_dict = config.to_dict()
        print(DisplayManager.format_config_display(config_dict))

    def _show_history(self):
        """显示历史记录"""
        print(f"\n📜 历史记录（会话ID：{self.scheduler.session_id}）：")
        history = self.scheduler.history_manager.get_recent_history(5)

        if history:
            for i, entry in enumerate(history, 1):
                timestamp = entry.get('timestamp', '')[:16]
                entry_type = entry.get('type', 'unknown')
                question = entry.get('question', '')[:60]
                print(f"\n  [{i}] {timestamp} - {entry_type}")
                print(f"      问题：{question}...")
        else:
            print("  暂无历史记录")

    def _enter_debate_mode(self):
        """进入辩论模式"""
        DisplayManager.print_header("💬 辩论模式")

        # 选择协调模式
        print("\n选择协调模式：")
        print("  1. AI自动协调（默认）")
        print("  2. 用户手动协调")

        mode_choice = input("选择（1/2）: ").strip()
        if mode_choice == "2":
            config.coordination_mode = "user"
            print("✅ 已选择用户协调模式")
        else:
            config.coordination_mode = "auto"
            print("✅ 已选择AI自动协调模式")

        # 输入问题
        question = input("\n请输入辩论问题：").strip()
        if not question:
            print("❌ 问题不能为空")
            return

        # 选择角色
        role1, role2 = self._select_debate_roles()

        # 回合数
        rounds_input = input(f"\n辩论回合数（默认:{config.debate_rounds}）: ").strip()
        if rounds_input.isdigit():
            config.debate_rounds = int(rounds_input)

        # 开始辩论
        print(f"\n🎬 开始辩论：{role1} vs {role2}")
        print(f"问题：{question}")
        DisplayManager.print_separator()

        self.scheduler.progress_tracker.start()
        try:
            self.scheduler.ask_both_models(question, mode="debate", role1=role1, role2=role2)
            total_time = self.scheduler.progress_tracker.get_elapsed_time()
            print(f"\n✅ 辩论完成 | 总耗时：{total_time:.2f}秒")
        except Exception as e:
            logger.error(f"辩论失败: {e}")
            print(f"❌ 辩论失败: {e}")

    def _enter_turtle_soup_mode(self):
        """进入海龟汤模式"""
        DisplayManager.print_header("🐢 海龟汤模式")

        question = input("\n请输入海龟汤谜面：").strip()
        if not question:
            print("❌ 谜面不能为空")
            return

        role1 = input("\nAI1角色（默认：侦探）: ").strip() or "侦探"
        role2 = input("AI2角色（默认：推理者）: ").strip() or "推理者"

        print(f"\n🎮 开始海龟汤游戏")
        print(f"谜面：{question}")
        print(f"AI角色：{role1} 和 {role2}")
        DisplayManager.print_separator()

        try:
            self.scheduler.ask_both_models(question, mode="turtle_soup", role1=role1, role2=role2)
        except Exception as e:
            logger.error(f"海龟汤游戏失败: {e}")
            print(f"❌ 海龟汤游戏失败: {e}")

    @staticmethod
    def _toggle_optimize_mode():
        """切换优化模式"""
        config.optimize_memory = not config.optimize_memory
        status = "开启" if config.optimize_memory else "关闭"
        print(f"✅ 优化模式已{status}")

    @staticmethod
    def _toggle_streaming_mode():
        """切换流式输出模式"""
        config.streaming_output = not config.streaming_output
        status = "开启" if config.streaming_output else "关闭"
        mode_desc = "AI回答将逐字实时显示" if config.streaming_output else "AI回答将一次性显示"
        print(f"✅ 流式输出已{status}")
        print(f"   {mode_desc}")

    @staticmethod
    def _show_roles():
        """显示可用角色"""
        print("\n🎭 可用角色（支持输入数字选择）：")
        roles = role_system.get_all_roles()
        for i, role in enumerate(roles, 1):
            print(f"  {i}. {role}")

    @staticmethod
    def _show_tags():
        """显示标签系统"""
        print("\n🏷️  标签系统：")
        for tag, roles in TAG_TO_ROLES.items():
            print(f"  {tag}: {', '.join(roles)}")

    @staticmethod
    def _configure_consensus():
        """配置共识检测"""
        print("\n🎯 共识检测配置")
        print(f"当前设置：")
        print(f"  - AI共识分析: {'开启' if config.ai_consensus_analysis else '关闭'}")
        print(f"  - 自动总结: {'开启' if config.auto_summarize_at_threshold else '关闭'}")
        print(f"  - 共识阈值: {int(config.consensus_threshold * 100)}%")
        print(f"  - 检测起始回合: 第{config.consensus_check_start_round}回合")

        print(f"\n选项：")
        print(f"  1. 切换AI共识分析 (当前: {'开' if config.ai_consensus_analysis else '关'})")
        print(f"  2. 切换自动总结 (当前: {'开' if config.auto_summarize_at_threshold else '关'})")
        print(f"  3. 设置共识阈值 (当前: {int(config.consensus_threshold * 100)}%)")
        print(f"  4. 设置检测起始回合 (当前: {config.consensus_check_start_round})")

        choice = input("选择 (1-4) 或回车返回: ").strip()

        if choice == '1':
            config.ai_consensus_analysis = not config.ai_consensus_analysis
            status = "开启" if config.ai_consensus_analysis else "关闭"
            print(f"✅ AI共识分析已{status}")
        elif choice == '2':
            config.auto_summarize_at_threshold = not config.auto_summarize_at_threshold
            status = "开启" if config.auto_summarize_at_threshold else "关闭"
            print(f"✅ 自动总结已{status}")
        elif choice == '3':
            try:
                threshold = float(input("输入新阈值 (0-100): ").strip()) / 100.0
                if 0.0 <= threshold <= 1.0:
                    config.consensus_threshold = threshold
                    print(f"✅ 共识阈值已设置为 {int(threshold * 100)}%")
                else:
                    print("❌ 阈值必须在 0-100 之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        elif choice == '4':
            try:
                round_num = int(input("输入起始回合数 (1-6): ").strip())
                if 1 <= round_num <= 6:
                    config.consensus_check_start_round = round_num
                    print(f"✅ 检测起始回合已设置为第{round_num}回合")
                else:
                    print("❌ 回合数必须在 1-6 之间")
            except ValueError:
                print("❌ 请输入有效的数字")
        elif choice == '':
            return
        else:
            print("❌ 无效选择")

    @staticmethod
    def _toggle_coordination_mode():
        """切换协调模式"""
        current = config.coordination_mode
        new_mode = "user" if current == "auto" else "auto"
        config.coordination_mode = new_mode
        print(f"✅ 协调模式已切换：{current} -> {new_mode}")

    def _handle_interrupt(self):
        """处理中断信号"""
        print("\n\n⚠️  检测到中断信号")
        choice = input("是否退出程序？（y/N）: ").strip().lower()
        if choice == 'y':
            self._exit_program()

    def _configure_api_mode(self):
        """配置API模式"""
        DisplayManager.print_header("🔗 API模式配置")

        print(f"当前API模式状态：{'已启用' if config.api_mode_enabled else '未启用'}")
        print(f"API提供方：{getattr(config, 'api_provider', 'custom')}")
        print(f"API基础地址：{getattr(config, 'api_base_url', '')}")
        print(f"API地址：{config.api_url}")
        print(f"API模型：{config.api_model}")
        print(f"API密钥：{'已设置' if config.api_key else '未设置'}")
        print(f"模型1使用API：{'是' if config.model_1_use_api else '否'}")
        print(f"模型2使用API：{'是' if config.model_2_use_api else '否'}")
        print(f"协调AI使用API：{'是' if config.coordinator_use_api else '否'}")

        DisplayManager.print_separator()

        # 询问是否启用API模式
        enable_api = InputValidator.get_yes_no_input("是否启用API模式？", default=config.api_mode_enabled)
        if enable_api:
            # 逐个配置：模型1、模型2、协调AI
            any_use_api = False
            targets = [
                ("模型1", "model_1"),
                ("模型2", "model_2"),
                ("协调AI", "coordinator"),
            ]

            for label, key in targets:
                print("\n" + "-" * 40)
                print(f"⚙️  配置 {label} 的API参数")
                use_api_attr = f"{key}_use_api"
                current_use = getattr(config, use_api_attr, False)
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

                # 配置基础地址
                current_base = getattr(config, base_attr, "") or default_base
                print("\n🔧 配置API基础地址：")
                base_url = input(f"{label} API基础地址 (当前: {current_base}): ").strip()
                if not base_url:
                    base_url = current_base
                base_url = base_url.rstrip("/")
                setattr(config, base_attr, base_url)

                # chat completions endpoint
                default_chat_url = f"{base_url}/chat/completions"
                current_chat = getattr(config, url_attr, "") or default_chat_url
                api_url = input(f"{label} ChatCompletions地址 (当前: {current_chat}): ").strip()
                api_url = (api_url or current_chat).rstrip("/")
                setattr(config, url_attr, api_url)

                # API Key：优先已有单独key，其次全局api_key
                existing_key = getattr(config, key_attr, "") or config.api_key
                api_key_input = input(f"{label} API密钥 (当前: {'已设置' if existing_key else '未设置'}，留空保持不变): ").strip()
                if api_key_input:
                    setattr(config, key_attr, api_key_input)
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
                    print("\n📦 获取到可用模型：")
                    for i, mid in enumerate(models, 1):
                        print(f"  {i}. {mid}")
                    model_choice = input(f"{label} 选择模型编号(1-{len(models)})，或直接输入模型名(回车保留当前 {current_model}): ").strip()
                    if model_choice.isdigit():
                        idx = int(model_choice)
                        if 1 <= idx <= len(models):
                            setattr(config, model_attr, models[idx - 1])
                    elif model_choice:
                        setattr(config, model_attr, model_choice)
                else:
                    print(f"\n⚠️  无法自动获取 {label} 的模型列表（该平台可能不支持 /models，或Key/网络问题）。")
                    api_model_input = input(f"请输入 {label} 使用的模型名称 (当前: {current_model}): ").strip()
                    if api_model_input:
                        setattr(config, model_attr, api_model_input)

            # 若至少有一个AI使用API，则认为API模式开启
            config.api_mode_enabled = any_use_api
            if not any_use_api:
                print("⚠️  所有AI都未配置使用API，将关闭API模式，仅使用本地Ollama。")

            # 保存配置
            config.save_to_file("macp_config.json")
            print("✅ API配置已保存")

            # 重新初始化调度器以应用新配置
            print("\n🔄 正在重新初始化系统...")
            try:
                # 重新创建调度器实例
                new_scheduler = AICouncilScheduler()
                self.scheduler = new_scheduler
                print("✅ 系统重新初始化完成")
            except (AICouncilException, requests.exceptions.RequestException, ValueError) as e:
                print(f"❌ 重新初始化失败: {e}")

        else:
            config.api_mode_enabled = False
            print("✅ 已禁用API模式")

        DisplayManager.print_separator()

    def _exit_program(self):
        """退出程序"""
        print(f"\n📊 会话统计：")
        print(f"  会话ID：{self.scheduler.session_id}")
        print(f"  总记录数：{len(self.scheduler.history_manager.history)}")
        print("\n👋 再见！")

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
