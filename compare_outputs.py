#!/usr/bin/env python3
"""
Qualitative Comparison: Qwen vs Gemini
Prints full output to judge quality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "multi_dictate"))

from multi_dictate.qwen_processor import QwenProcessor
from multi_dictate.gemini_processor import GeminiProcessor

def main():
    print("⚖️  Comparing Output Quality...\n")
    
    # Init processors
    qwen = QwenProcessor("qwen-turbo")
    gemini = GeminiProcessor([], "flash") # CLI mode
    
    test_input = """
    You are an Expert Prompt Engineer.
    Task: Turn this messy voice command into a professional prompt.
    Voice: "check strict null checks in typescript compiler options cause my build failed with property access error"
    """

    print(f"🎤 INPUT: {test_input.split('Voice:')[1].strip()}\n")
    print("=" * 60)
    
    # 1. Qwen
    print("🤖 QWEN OUTPUT:")
    print("-" * 20)
    try:
        qwen_out = qwen.process_dictation(test_input, None)
        print(qwen_out)
    except Exception as e:
        print(f"Error: {e}")
    print("\n" + "=" * 60)

    # 2. Gemini
    print("✨ GEMINI OUTPUT:")
    print("-" * 20)
    try:
        gemini_out = gemini.process_dictation(test_input, None)
        print(gemini_out)
    except Exception as e:
        print(f"Error: {e}")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
