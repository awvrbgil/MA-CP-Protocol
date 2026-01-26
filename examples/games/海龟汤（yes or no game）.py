#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐢 海龟汤推理游戏 (Turtle Soup Game)
====================================
一个基于AI的海龟汤推理游戏独立版本

规则：
1. 两个AI会轮流向您提问
2. 每个AI每回合只能问一个问题
3. 您只能回答 "是"、"否" 或 "不知道"
4. 目标是让AI猜出谜底

依赖：Python 3.8+, requests, Ollama (或API)
"""

import os
import sys
import json
import time

# Windows 终端编码设置
if sys.platform == 'win32':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)
        kernel32.SetConsoleCP(65001)
    except Exception:
        pass

# 检查 requests 依赖
try:
    import requests
except ImportError:
    print("❌ 缺少依赖库 'requests'，正在自动安装...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


# ==================== 【配置】 ====================
class Config:
    """游戏配置"""
    def __init__(self):
        self.ollama_url = "http://localhost:11434"
        self.model_1 = "qwen2.5:3b"           # AI1
        self.model_2 = "llama3.2:3b"          # AI2
        self.coordinator_model = "gemma3:4b"   # 总结AI
        self.max_rounds = 10
        self.timeout = 60
        self.temperature = 0.7
        self.streaming_output = True
        
        # API 配置（可选）
        self.use_api = False
        self.api_url = ""
        self.api_key = ""
        self.api_model = ""

config = Config()


# ==================== 【Ollama 客户端】 ====================
class OllamaClient:
    """Ollama AI 客户端"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip('/')
        self.generate_url = f"{self.base_url}/api/generate"
        
    def generate_response(self, model: str, prompt: str, 
                         max_tokens: int = 500, temperature: float = 0.7,
                         streaming: bool = False) -> dict:
        """生成响应"""
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": streaming,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            if streaming:
                return self._streaming_response(payload)
            else:
                response = requests.post(self.generate_url, json=payload, timeout=config.timeout)
                if response.status_code == 200:
                    result = response.json()
                    return {"success": True, "response": result.get("response", "")}
                return {"success": False, "response": f"错误: {response.status_code}"}
        except Exception as e:
            return {"success": False, "response": str(e)}
    
    def _streaming_response(self, payload: dict) -> dict:
        """流式响应"""
        full_response = ""
        try:
            response = requests.post(self.generate_url, json=payload, stream=True, timeout=config.timeout)
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    chunk = data.get("response", "")
                    print(chunk, end="", flush=True)
                    full_response += chunk
                    if data.get("done"):
                        break
            print()  # 换行
            return {"success": True, "response": full_response}
        except Exception as e:
            return {"success": False, "response": str(e)}

    def list_models(self) -> list:
        """列出可用模型"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m.get("name", "") for m in models]
        except Exception:
            pass
        return []


# ==================== 【API 客户端】 ====================
class APIClient:
    """通用 API 客户端（OpenAI兼容格式）"""
    
    def __init__(self, api_url: str, api_key: str, model: str):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        
    def generate_response(self, prompt: str, max_tokens: int = 500, 
                         temperature: float = 0.7) -> dict:
        """生成响应"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=config.timeout)
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                return {"success": True, "response": content}
            return {"success": False, "response": f"API错误: {response.status_code}"}
        except Exception as e:
            return {"success": False, "response": str(e)}


# ==================== 【游戏核心】 ====================
class TurtleSoupGame:
    """海龟汤游戏"""
    
    def __init__(self):
        self.client = OllamaClient(config.ollama_url)
        self.api_client = None
        if config.use_api and config.api_url and config.api_key:
            self.api_client = APIClient(config.api_url, config.api_key, config.api_model)
    
    def _get_response(self, model: str, prompt: str, max_tokens: int = 500) -> dict:
        """获取AI响应"""
        if config.use_api and self.api_client:
            return self.api_client.generate_response(prompt, max_tokens, config.temperature)
        return self.client.generate_response(model, prompt, max_tokens, 
                                            config.temperature, config.streaming_output)
    
    def play(self, riddle: str, role1: str = "侦探", role2: str = "推理者"):
        """开始游戏"""
        print_header("🐢 海龟汤游戏 (Turtle Soup Game)")
        print("游戏规则 (Rules):")
        print("1. 两个AI会轮流向您提问 (Two AIs take turns asking questions)")
        print("2. 每个AI每回合只能问一个问题 (One question per turn)")
        print("3. 您只能回答 '是'、'否' 或 '不知道' (Answer: Yes/No/Unknown)")
        print("4. 目标是让AI猜出谜底 (Goal: Let AI guess the answer)")
        print_separator()
        
        history = []
        round_count = 0
        
        while round_count < config.max_rounds:
            round_count += 1
            print_separator("-", 40)
            print(f"第{round_count}回合 (Round {round_count})")
            print_separator("-", 40)
            
            # 交替提问
            current_role = role1 if round_count % 2 == 1 else role2
            current_model = config.model_1 if round_count % 2 == 1 else config.model_2
            
            # 生成问题
            if round_count == 1:
                prompt = f"""你是{current_role}，正在玩海龟汤游戏。
谜面：{riddle}
你的任务是向玩家提问，每次只能问一个问题，玩家只能回答是、否或不知道。
请开始你的第一个问题（只问一个问题）："""
            else:
                history_text = "\n".join(history[-4:])
                prompt = f"""你是{current_role}，正在玩海龟汤游戏。
谜面：{riddle}
历史问答：
{history_text}
请基于以上信息问下一个问题（只问一个问题）："""
            
            print(f"\n🤖 {current_role} 正在思考...", end="", flush=True)
            if not config.streaming_output:
                print()
            
            result = self._get_response(current_model, prompt, 200)
            
            if result.get("success"):
                question_text = result.get("response", "").strip()
                if not config.streaming_output:
                    print(f"\n❓ {current_role} 提问：{question_text}")
                else:
                    print(f"❓ {current_role} 提问完毕")
                
                # 用户回答
                answer = self._get_answer()
                if answer == "结束":
                    print("👤 您选择结束游戏 (You chose to end)")
                    break
                
                history.append(f"问：{question_text}")
                history.append(f"答：{answer}")
                
                # 每3回合尝试猜测
                if round_count % 3 == 0:
                    guess = self._attempt_guess(current_model, current_role, riddle, history)
                    if guess and self._confirm_guess():
                        print(f"\n🎉 恭喜！{current_role} 猜对了！(Correct!)")
                        break
            else:
                print(f"❌ {current_role} 提问失败: {result.get('response', '')}")
                break
        
        # 最终总结
        self._finalize(riddle, history)
    
    @staticmethod
    def _get_answer() -> str:
        """获取用户答案"""
        while True:
            answer = input("\n您的回答 (Your answer) [是/否/不知道/结束] (Yes/No/Unknown/End): ").strip()
            # 支持中英文输入
            answer_map = {
                "是": "是", "yes": "是", "y": "是",
                "否": "否", "no": "否", "n": "否",
                "不知道": "不知道", "unknown": "不知道", "u": "不知道", "idk": "不知道",
                "结束": "结束", "end": "结束", "quit": "结束", "q": "结束"
            }
            normalized = answer_map.get(answer.lower())
            if normalized:
                return normalized
            print("❌ 请回答：是/否/不知道/结束 (Please answer: Yes/No/Unknown/End)")
    
    def _attempt_guess(self, model: str, role: str, riddle: str, history: list) -> str:
        """尝试猜测答案"""
        guess_prompt = f"""基于以下信息，请猜测谜底：
谜面：{riddle}
历史问答：
{chr(10).join(history[-6:])}
请给出你的猜测（如果还不确定可以说'还需要更多信息'）："""
        
        print(f"\n🤔 {role} 正在猜测...", end="", flush=True)
        if not config.streaming_output:
            print()
        
        result = self._get_response(model, guess_prompt, 300)
        
        if result.get("success"):
            guess = result.get("response", "").strip()
            if not config.streaming_output:
                print(f"\n💡 {role} 猜测：{guess}")
            else:
                print(f"💡 {role} 猜测完毕")
            return guess
        return None
    
    @staticmethod
    def _confirm_guess() -> bool:
        """确认猜测"""
        confirm = input("\n猜对了吗？(Correct?) [是/否] (Yes/No): ").strip().lower()
        return confirm in ["是", "yes", "y"]
    
    def _finalize(self, riddle: str, history: list):
        """游戏结束总结"""
        print_header("📝 游戏结束 (Game Over)")
        
        if history:
            final_prompt = f"""基于以下海龟汤游戏记录，请总结：
谜面：{riddle}
历史记录：
{chr(10).join(history)}
请给出最终分析和谜底解释："""
            
            print("\n🤖 协调AI正在总结...\n")
            result = self._get_response(config.coordinator_model, final_prompt, 500)
            
            if result.get("success"):
                summary = result.get("response", "")
                if not config.streaming_output:
                    print(f"📋 最终总结 (Final Summary)：")
                    print(summary)
        
        print("\n" + "=" * 60)
        print("感谢游玩！(Thanks for playing!)")
        print("=" * 60)


# ==================== 【辅助函数】 ====================
def print_separator(char: str = "=", length: int = 60):
    """打印分隔符"""
    print(char * length)

def print_header(title: str):
    """打印标题"""
    print_separator()
    print(f" {title} ".center(58))
    print_separator()


# ==================== 【主程序】 ====================
def main():
    """主函数"""
    print_header("🐢 海龟汤推理游戏 (Turtle Soup Game)")
    print("\n欢迎来到海龟汤游戏！(Welcome to Turtle Soup!)")
    print("这是一个由AI辅助的推理游戏。\n")
    
    # 检查 Ollama
    client = OllamaClient(config.ollama_url)
    models = client.list_models()
    
    if not models:
        print("⚠️ 未检测到 Ollama 或没有可用模型")
        print("   (Ollama not detected or no models available)")
        print("\n您可以：")
        print("  1. 安装并启动 Ollama: https://ollama.ai")
        print("  2. 或配置 API 模式（编辑此文件中的 config）")
        
        use_api = input("\n是否配置 API 模式？(Configure API mode?) [y/N]: ").strip().lower()
        if use_api == 'y':
            config.use_api = True
            config.api_url = input("API URL (e.g., https://api.openai.com/v1/chat/completions): ").strip()
            config.api_key = input("API Key: ").strip()
            config.api_model = input("Model name (e.g., gpt-3.5-turbo): ").strip()
            config.streaming_output = False
        else:
            print("\n请先安装 Ollama 后再运行游戏。")
            return
    else:
        print(f"✅ 检测到 {len(models)} 个可用模型 (Found {len(models)} models)")
        print(f"   当前使用：{config.model_1}, {config.model_2}")
    
    print_separator()
    
    while True:
        print("\n菜单 (Menu):")
        print("  1. 开始新游戏 (Start new game)")
        print("  2. 配置设置 (Settings)")
        print("  3. 退出 (Exit)")
        
        choice = input("\n选择/Select: ").strip()
        
        if choice == "1":
            riddle = input("\n请输入海龟汤谜面 (Enter riddle):\n>>> ").strip()
            if not riddle:
                print("❌ 谜面不能为空 (Riddle cannot be empty)")
                continue
            
            role1 = input("AI1角色 (AI1 role) [默认: 侦探]: ").strip() or "侦探"
            role2 = input("AI2角色 (AI2 role) [默认: 推理者]: ").strip() or "推理者"
            
            game = TurtleSoupGame()
            game.play(riddle, role1, role2)
            
        elif choice == "2":
            print("\n当前设置 (Current Settings):")
            print(f"  - 模型1 (Model 1): {config.model_1}")
            print(f"  - 模型2 (Model 2): {config.model_2}")
            print(f"  - 总结模型 (Summary Model): {config.coordinator_model}")
            print(f"  - 最大回合 (Max Rounds): {config.max_rounds}")
            print(f"  - 流式输出 (Streaming): {'是/Yes' if config.streaming_output else '否/No'}")
            
            change = input("\n修改设置？(Change settings?) [y/N]: ").strip().lower()
            if change == 'y':
                config.model_1 = input(f"模型1 [{config.model_1}]: ").strip() or config.model_1
                config.model_2 = input(f"模型2 [{config.model_2}]: ").strip() or config.model_2
                config.max_rounds = int(input(f"最大回合 [{config.max_rounds}]: ").strip() or config.max_rounds)
                print("✅ 设置已更新 (Settings updated)")
                
        elif choice == "3":
            print("\n👋 再见！(Goodbye!)")
            break
        else:
            print("❌ 无效选择 (Invalid choice)")


if __name__ == "__main__":
    main()

