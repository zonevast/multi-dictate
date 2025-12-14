import sys
import os
import logging
from box import Box

sys.path.append(os.getcwd())

try:
    from multi_dictate.prompt_engineering_optimizer import PromptEngineeringOptimizer
    from multi_dictate.smart_ai_router import SmartAIRouter
except ImportError:
    sys.path.append(os.path.join(os.getcwd(), 'multi_dictate'))
    from multi_dictate.prompt_engineering_optimizer import PromptEngineeringOptimizer
    from multi_dictate.smart_ai_router import SmartAIRouter

logging.basicConfig(level=logging.ERROR)

def test_extraction_capability():
    config = Box({
        "general": {
            "ai_provider": "auto",
            "qwen_model": "qwen-turbo"
        }
    })

    print("🚀 INITIALIZING NOISE EXTRACTION TEST...")
    optimizer = PromptEngineeringOptimizer(config)
    router = SmartAIRouter(config)

    # SCENARIO: Clipboard has relevant tech data BURIED in noise
    voice_input = "Analyze this error and suggest a fix, ignore the chat noise"
    
    messy_clipboard = """
    [Chat Log - 10:00 AM]
    Alice: Hey Bob, did you see the game last night?
    Bob: Yeah, amazing goal!
    
    [System Log - 10:05 AM]
    CRITICAL ERROR: ConnectionRefusedError: [Errno 111] Connection refused
    Target: 192.168.1.55:8080
    Service: PaymentGateway
    Retrying... Failed (3 attempts)
    
    [Chat Log - 10:06 AM]
    Alice: Wait, is the server down?
    Bob: I think so, I can't access the dashboard.
    Alice: lunch?
    Bob: sure.
    
    -- 
    Company Confidential Footer
    Do not distribute.
    """

    print("\n🔶 SCENARIO: Extraction from Noisy Clipboard 🔶")
    print("-" * 50)
    print(f"🎤 Voice: \"{voice_input}\"")
    print(f"📋 Clipboard Content (Contains noise):\n{messy_clipboard}")
    
    meta_prompt = optimizer.construct_system_prompt_request(voice_input, messy_clipboard)
    
    try:
        if router.processors:
            print(f"\n⏳ Processing with {router.current_processor}...")
            result = router.process_dictation(meta_prompt, None)
            print("\n✨ OPTIMIZED RESULT (Should only contain technical info):")
            print("=" * 60)
            print(result)
            print("=" * 60)
        else:
            print("⚠️  No AI processors active.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_extraction_capability()
