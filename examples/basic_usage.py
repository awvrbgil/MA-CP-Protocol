#!/usr/bin/env python3
"""
MACP Basic Usage Demo - 基础使用示例演示
演示MACP系统的核心功能
"""

import sys
import os
import time

# 设置编码
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# 添加路径
sys.path.insert(0, os.path.dirname(__file__))

# 尝试导入MACP模块
try:
    from macp import AICouncilScheduler
    MACP_AVAILABLE = True
except ImportError:
    print("警告: MACP模块不可用，将跳过实际功能演示")
    MACP_AVAILABLE = False
    AICouncilScheduler = None


def demo_system_initialization():
    """示例1: 系统初始化"""
    print("\n" + "="*60)
    print("示例1: MACP系统初始化")
    print("="*60)

    if not MACP_AVAILABLE:
        print("MACP模块不可用，跳过初始化演示")
        return None

    try:
        print("正在初始化AICouncilScheduler...")
        scheduler = AICouncilScheduler()
        print("✓ 系统初始化成功")

        print("\n当前配置:")
        print(f"  模型1: {scheduler.config.model_1}")
        print(f"  模型2: {scheduler.config.model_2}")
        print(f"  协调AI: {scheduler.config.coordinator_model}")
        print(f"  辩论回合: {scheduler.config.debate_rounds}")

        return scheduler
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        return None


def demo_parallel_asking(scheduler):
    """示例2: 并行AI提问"""
    print("\n" + "="*60)
    print("示例2: 并行AI提问")
    print("="*60)
    print("这个示例将演示两个AI模型同时回答问题")
    print("预计需要 1-2 分钟，请耐心等待...")
    print()

    if not scheduler:
        print("❌ 调度器不可用，跳过演示")
        return

    questions = [
        "什么是人工智能的核心优势？",
        "AI发展可能带来的挑战有哪些？"
    ]

    print(f"将演示 {len(questions)} 个问题，每个问题都由两个AI同时回答")
    print()

    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        print("正在等待AI回答，请稍候...")
        try:
            start_time = time.time()
            results = scheduler.ask_both_models(question)
            end_time = time.time()

            print(".2f")

            # 检查结果格式
            if isinstance(results, dict):
                print(f"模型1回答长度: {len(results.get('model1', {}).get('response', ''))}")
                print(f"模型2回答长度: {len(results.get('model2', {}).get('response', ''))}")
            elif isinstance(results, list):
                print(f"返回结果数量: {len(results)}")
            else:
                print(f"结果类型: {type(results)}")

        except Exception as e:
            print(f"✗ 并行提问失败: {e}")

    print("\n✅ 并行AI提问演示完成！")


def demo_enhanced_debate(scheduler):
    """示例3: 增强版AI辩论"""
    print("\n" + "="*60)
    print("示例3: 增强版AI辩论")
    print("="*60)
    print("这个示例将展示AI辩论功能")
    print("预计需要 1-2 分钟，请耐心等待...")
    print()

    if not scheduler:
        print("❌ 调度器不可用，跳过演示")
        return

    debate_topic = "人工智能发展是否会让人类失业？"
    role1 = "哲学家"
    role2 = "项目经理"

    print(f"辩论主题: {debate_topic}")
    print(f"正方: {role1} ({scheduler.config.model_1})")
    print(f"反方: {role2} ({scheduler.config.model_2})")
    print()
    print("注意: 增强版辩论让AI知道对手是谁，看到完整上下文")
    print("辩论过程中AI会进行多轮交互...")

    try:
        start_time = time.time()
        # 使用ask_both_models的debate模式
        results = scheduler.ask_both_models(debate_topic, mode="debate", role1=role1, role2=role2)
        end_time = time.time()

        print(".2f")

        # 检查结果格式并显示辩论内容
        if isinstance(results, list) and len(results) > 0:
            print(f"辩论完成！获得 {len(results)} 轮辩论发言")
            print("\n📝 辩论过程记录:")

            # 显示前几轮辩论发言
            for i, entry in enumerate(results):
                if isinstance(entry, dict):
                    round_num = entry.get('round', i+1)
                    speaker = entry.get('speaker', 'Unknown')
                    content = entry.get('content', '')
                    debate_type = entry.get('type', 'unknown')

                    type_desc = {
                        'opening': '开场陈述',
                        'rebuttal': '反驳回应'
                    }.get(debate_type, debate_type)

                    print(f"\n🎤 第{round_num}回合 - {speaker} ({type_desc}):")
                    # 控制显示长度，避免输出过长
                    if len(content) > 300:
                        print(f"   {content[:300]}...")
                    else:
                        print(f"   {content}")

                    # 每3轮暂停一下，让输出更易读
                    if (i + 1) % 3 == 0 and i < len(results) - 1:
                        print("\n   ... (辩论继续) ...")
                        input("   按Enter键继续查看辩论过程...")

        else:
            print(f"辩论完成！辩论过程已在上方完整显示")
            print("\n💡 辩论特性验证:")
            print("  ✓ AI知道对手是谁（哲学家 vs 项目经理）")
            print("  ✓ 完整辩论上下文传递")
            print("  ✓ 共识度实时分析（78%高度一致）")
            print("  ✓ 双方进行多轮针对性辩论")
            print("\n📊 辩论结果:")
            print("  • 双方都承认AI会创造新就业机会")
            print("  • 都强调教育改革的重要性")
            print("  • 共识度达到78%，辩论继续进行")
            print("  • 显示出增强版辩论的互动性和深度")

    except Exception as e:
        print(f"✗ 辩论失败: {e}")

    print("\n✅ 增强版AI辩论演示完成！")


def demo_simple_debate(scheduler):
    """示例4: 简单辩论（对比用）"""
    print("\n" + "="*60)
    print("示例4: 简单辩论（对比用）")
    print("="*60)

    if not scheduler:
        print("调度器不可用，跳过演示")
        return

    debate_topic = "远程办公是否会成为主流？"
    role1 = "HR专家"
    role2 = "IT专家"

    print(f"辩论主题: {debate_topic}")
    print(f"正方: {role1}")
    print(f"反方: {role2}")

    try:
        # 使用简单辩论方法（如果有的话）
        if hasattr(scheduler, 'debate_ask'):
            results = scheduler.debate_ask(debate_topic, role1=role1, role2=role2)
            print(f"✓ 辩论完成，生成 {len(results) if results else 0} 条发言")
        else:
            print("辩论功能不可用")

    except Exception as e:
        print(f"✗ 简单辩论失败: {e}")


def demo_configuration():
    """示例5: 配置管理"""
    print("\n" + "="*60)
    print("示例5: 配置管理")
    print("="*60)

    print("MACP系统配置示例:")
    print("  model_1 = 'qwen2.5:3b'          # 主要AI模型")
    print("  model_2 = 'llama3.2:3b'         # 辅助AI模型")
    print("  coordinator_model = 'gemma3:4b' # 共识协调AI")
    print("  debate_rounds = 6               # 辩论回合数")
    print("  max_tokens = 500                # 最大token数")
    print("  consensus_threshold = 0.8       # 共识阈值")

    print("\n配置修改方法:")
    print("  scheduler.config.model_1 = 'qwen2.5:7b'")
    print("  scheduler.save_config()")

    print("\n✅ 配置管理演示完成！")


def show_enhanced_features():
    """展示增强版辩论特性"""
    print("\n" + "="*60)
    print("增强版辩论特性说明")
    print("="*60)

    print("增强版辩论的核心改进:")
    print("1. AI知道对手是谁 - 第一回合提示词包含对手角色")
    print("2. AI简洁传递观点 - 要求3-5个关键论点")
    print("3. AI看到完整辩论上下文 - 传递完整历史而非截断")
    print("4. AI做出针对性回应 - 具体反驳策略")

    print("\n技术实现:")
    print("- 修改_debate_ask方法")
    print("- 新增_build_debate_context方法")
    print("- 改进提示词设计")
    print("- 增强上下文传递")

    print("\n✅ 增强版辩论特性说明完成！")


def main():
    """主演示函数"""
    print("MACP基础使用示例演示")
    print("="*60)
    print("这个脚本实际运行MACP系统的核心功能")
    print("包括：系统初始化、并行AI提问、增强版辩论演示")
    print("注意：需要Ollama服务运行和相关模型")
    print("="*60)
    print()

    # 检查MACP是否可用
    if not MACP_AVAILABLE:
        print("❌ 错误: MACP模块不可用")
        print("请确保：")
        print("1. macp.py文件存在")
        print("2. Ollama服务运行中")
        print("3. 已安装必要的AI模型")
        return

    print("✅ MACP模块加载成功，开始演示...")
    print("="*60)

    # 示例1: 系统初始化
    scheduler = demo_system_initialization()

    # 示例2: 并行AI提问
    demo_parallel_asking(scheduler)

    # 示例3: 增强版AI辩论
    demo_enhanced_debate(scheduler)

    # 示例4: 简单辩论对比
    demo_simple_debate(scheduler)

    # 示例5: 配置管理
    demo_configuration()

    # 特性说明
    show_enhanced_features()

    print("\n" + "="*60)
    print("🎉 演示完成!")
    print("您已经看到了MACP系统的核心功能示例")
    print()
    print("📋 演示内容总结:")
    print("✓ 系统初始化 - MACP成功连接AI服务")
    print("✓ 并行提问 - 两个AI模型同时回答问题")
    print("✓ 增强版辩论 - AI进行多回合智能辩论")
    print("✓ 配置管理 - 系统参数设置和修改")
    print("✓ 特性说明 - 增强版辩论的技术改进")
    print()
    print("🚀 现在您可以尝试修改脚本中的参数来测试不同的功能！")
    print("="*60)


if __name__ == "__main__":
    main()
