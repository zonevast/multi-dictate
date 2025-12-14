#!/usr/bin/env python3
"""
Benchmark Script: Qwen vs Gemini for Prompt Optimization
Tests both models on a complex optimization task to help select the default.
"""

import time
import sys
import os
import yaml
from box import Box

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), "multi_dictate"))

try:
    from multi_dictate.qwen_processor import QwenProcessor
    from multi_dictate.gemini_processor import GeminiProcessor
except ImportError as e:
    print(f"Import Error: {e}")
    # Fallback for direct execution
    sys.path.append(os.path.dirname(__file__))
    from multi_dictate.qwen_processor import QwenProcessor
    from multi_dictate.gemini_processor import GeminiProcessor

def load_config():
    config_path = os.path.expanduser("~/.config/multi-dictate/dictate.yaml")
    local_config = "dictate.yaml"
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return Box(yaml.safe_load(f))
    elif os.path.exists(local_config):
        with open(local_config, 'r') as f:
            return Box(yaml.safe_load(f))
    return None

def main():
    print("🚀 Starting Model Benchmark: Qwen vs Gemini")
    
    config = load_config()
    if not config:
        print("❌ Could not load dictate.yaml configuration")
        return

    # Initialize Processors
    processors = {}
    
    # 1. Qwen
    try:
        qwen_model = config.general.get('qwen_model', 'qwen-turbo')
        print(f"🔌 Initializing Qwen ({qwen_model})...")
        qwen = QwenProcessor(qwen_model)
        if qwen.available:
            processors['qwen'] = qwen
    except Exception as e:
        print(f"❌ Qwen Init Failed: {e}")

    # 2. Gemini
    try:
        gemini_model = config.general.get('gemini_model', 'flash')
        api_key = config.general.get('gemini_api_key')
        if not api_key and hasattr(config.general, 'gemini_api_keys'):
            api_key = config.general.gemini_api_keys[0] # Take first
            
        if api_key:
            print(f"🔌 Initializing Gemini ({gemini_model}) [SDK Mode]...")
            # GeminiProcessor expects list of keys usually
            gemini = GeminiProcessor([api_key], gemini_model) 
            processors['gemini'] = gemini
        else:
            print(f"🔌 Initializing Gemini ({gemini_model}) [CLI Check Mode]...")
            # Initialize with None to trigger CLI fallback in Processor
            gemini = GeminiProcessor([], gemini_model)
            processors['gemini'] = gemini
    except Exception as e:
        print(f"❌ Gemini Init Failed: {e}")

    if not processors:
        print("❌ No processors available to test!")
        return

    # Test Prompt
    print("\n🧪 Running Optimization Test...")
    test_input = """
    You are an Expert Prompt Engineer.
    Task: Turn this messy voice command into a professional prompt.
    Voice: "check strict null checks in typescript compiler options cause my build failed with property access error"
    """
    
    results = {}
    
    for name, proc in processors.items():
        print(f"\n🏃 Testing {name.upper()}...")
        start = time.time()
        try:
            # We assume process_dictation takes (text, context)
            response = proc.process_dictation(test_input, None)
            duration = time.time() - start
            
            results[name] = {
                'time': duration,
                'length': len(response) if response else 0,
                'response': response
            }
            print(f"   ✅ Done in {duration:.2f}s")
        except Exception as e:
            print(f"   ❌ Failed: {e}")
            results[name] = None

    # Compare
    print("\n🏆 BENCHMARK RESULTS")
    print("-" * 60)
    best_model = None
    min_time = float('inf')
    
    for name, res in results.items():
        if res:
            print(f"Model: {name.upper()}")
            print(f"Time:  {res['time']:.2f}s")
            print(f"Chars: {res['length']}")
            snippet = res['response'][:100].replace('\n', ' ')
            print(f"Snippet: {snippet}...")
            print("-" * 60)
            
            if res['time'] < min_time:
                min_time = res['time']
                best_model = name
                
    if best_model:
        print(f"\n✨ FASTEST MODEL: {best_model.upper()}")
        print(f"💡 Recommended Default: {best_model.upper()}")
    
if __name__ == "__main__":
    main()
