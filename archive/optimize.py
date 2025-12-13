#!/usr/bin/env python3
"""
Simple optimization tool - direct interface to the 9-stage pipeline.
Usage: python3 optimize.py "your prompt" [--clipboard "context"]
"""

import sys
import os
import argparse
import subprocess

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_dictate.prompt_generation_pipeline import PromptGenerationPipeline

def main():
    parser = argparse.ArgumentParser(
        description="Simple prompt optimization using 9-stage pipeline",
        epilog="Examples:\n"
               "  python3 optimize.py \"fix slow api\" --clipboard \"/var/www/app\"\n"
               "  python3 optimize.py \"plan migration\" --no-context"
    )

    parser.add_argument("prompt", help="Prompt to optimize")
    parser.add_argument("--clipboard", "-c", help="Clipboard context or file path")
    parser.add_argument("--no-context", action="store_true", help="Don't use system clipboard")

    args = parser.parse_args()

    # Initialize pipeline
    pipeline = PromptGenerationPipeline()

    # Prepare context
    context = {}
    if args.clipboard:
        context = {"clipboard": args.clipboard}
    elif not args.no_context:
        # Try to get from system clipboard
        try:
            result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                context = {"clipboard": result.stdout.strip()}
                print(f"📁 Using clipboard context: {result.stdout.strip()[:50]}...")
        except:
            pass

    print("🚀 9-Stage Pipeline Optimization")
    print("=" * 40)
    print(f"📝 Input: '{args.prompt}'")
    if context:
        print(f"📁 Context: {context}")
    print()

    try:
        # Process through pipeline
        result = pipeline.process_through_pipeline(args.prompt, context)

        if result.success:
            print("✅ Pipeline SUCCESS!")
            print(f"📊 Quality Score: {result.quality_score:.1f}/100")
            print(f"📈 Improvement: {result.quality_score/100:.1f}x")
            print(f"⏱️  Time: {result.processing_time:.3f}s")
            print(f"🔄 Iterations: {result.iterations}")
            print()

            # Show stage summary
            stages = result.stage_results
            if 'raw_intent' in stages:
                raw = stages['raw_intent']
                print(f"🎯 Raw Intent: {raw.length} words, ambiguity: {raw.ambiguity_level:.2f}")

            if 'intent_clarification' in stages:
                intent = stages['intent_clarification']
                print(f"🔍 Intent: {intent.task_type.value} → {intent.domain} ({intent.depth.value})")

            if 'skeleton' in stages:
                skeleton = stages['skeleton']
                print(f"🏗️  Skeleton: {skeleton.value}")

            if 'constraints' in stages:
                constraints = stages['constraints']
                if constraints.tech_stack:
                    print(f"💻 Tech Stack: {', '.join(constraints.tech_stack)}")
                if constraints.constraints:
                    print(f"⚖️  Constraints: {len(constraints.constraints)} rules")

            print()
            print("📝 FINAL OPTIMIZED PROMPT:")
            print("=" * 50)
            print(result.final_prompt)
            print("=" * 50)

        else:
            print("❌ Pipeline FAILED!")
            print(f"Iterations: {result.iterations}")
            if result.stage_results:
                last_quality = result.stage_results.get('quality_gate')
                if last_quality and last_quality.issues:
                    print(f"Issues: {', '.join(last_quality.issues)}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()