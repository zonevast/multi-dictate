#!/usr/bin/env python3
"""
Qwen Model Integration CLI
Direct interface for testing optimization with Qwen and live output.
Usage: python3 qwen_optimize.py prompt "your task here" --clipboard "/path/to/context"
"""

import sys
import os
import argparse
import json
import time
import subprocess
from typing import Optional, Dict, Any

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_dictate.prompt_generation_pipeline import PromptGenerationPipeline
from multi_dictate.prompt_quality_scorer import PromptQualityScorer

class QwenIntegration:
    """Integration with Qwen model for optimization testing."""

    def __init__(self):
        self.pipeline = PromptGenerationPipeline()
        self.quality_scorer = PromptQualityScorer()

        # Qwen model configuration
        self.qwen_models = {
            "qwen-turbo": {
                "name": "Qwen Turbo",
                "provider": "ollama",  # Using Ollama for local inference
                "size": "7b",
                "speed": "fast"
            },
            "qwen-plus": {
                "name": "Qwen Plus",
                "provider": "ollama",
                "size": "14b",
                "speed": "medium"
            },
            "qwen-max": {
                "name": "Qwen Max",
                "provider": "api",  # Would use API for larger models
                "size": "72b",
                "speed": "slow"
            }
        }

    def run_optimization_with_qwen(self, prompt: str, context: Dict = None,
                                 model: str = "qwen-turbo",
                                 show_stages: bool = True,
                                 live_output: bool = True) -> Dict[str, Any]:
        """
        Run complete optimization pipeline with Qwen model.

        Args:
            prompt: User input prompt
            context: Additional context (clipboard, files, etc.)
            model: Qwen model variant
            show_stages: Show stage-by-stage processing
            live_output: Show live AI output

        Returns:
            Complete results with pipeline output and AI response
        """
        print("🚀 Qwen Optimization Pipeline Starting...")
        print(f"📝 Input: '{prompt}'")
        if context:
            print(f"📁 Context: {context}")
        print(f"🤖 Model: {self.qwen_models[model]['name']}")
        print("=" * 60)

        start_time = time.time()

        try:
            # Stage 1: Pipeline Processing
            if show_stages:
                print("\n📋 Stage 1: Pipeline Processing")
                print("-" * 30)

            pipeline_result = self.pipeline.process_through_pipeline(prompt, context)

            if not pipeline_result.success:
                print("❌ Pipeline failed!")
                return {"success": False, "error": "Pipeline processing failed"}

            if show_stages:
                print(f"✅ Pipeline Success!")
                print(f"   Quality Score: {pipeline_result.quality_score:.1f}/100")
                print(f"   Iterations: {pipeline_result.iterations}")
                print(f"   Processing Time: {pipeline_result.processing_time:.3f}s")

                # Show stage summary
                stages = pipeline_result.stage_results
                if 'intent_clarification' in stages:
                    intent = stages['intent_clarification']
                    print(f"   Intent: {intent.task_type.value} → {intent.domain} ({intent.depth.value})")
                if 'skeleton' in stages:
                    print(f"   Skeleton: {stages['skeleton'].value}")

            # Stage 2: Quality Scoring
            if show_stages:
                print(f"\n📊 Stage 2: Quality Assessment")
                print("-" * 30)

            quality_result = self.quality_scorer.score_prompt_quality(
                prompt,
                pipeline_result.final_prompt,
                context
            )

            if show_stages:
                print(f"✅ Quality Score: {quality_result.overall_score}/100")
                print(f"   Improvement Ratio: {quality_result.improvement_ratio:.1f}x")
                print(f"   Enhancement Detected: {quality_result.enhancement_detected}")

            # Stage 3: Qwen Model Processing
            if show_stages:
                print(f"\n🤖 Stage 3: Qwen Model Processing")
                print("-" * 30)

            qwen_response = self._call_qwen_model(
                pipeline_result.final_prompt,
                model,
                live_output=live_output
            )

            total_time = time.time() - start_time

            # Final Results
            print(f"\n🎯 Complete Results")
            print("=" * 30)
            print(f"⏱️  Total Time: {total_time:.2f}s")
            print(f"📊 Pipeline Quality: {pipeline_result.quality_score:.1f}/100")
            print(f"📈 Quality Score: {quality_result.overall_score}/100")
            print(f"🔄 Optimization Ratio: {quality_result.improvement_ratio:.1f}x")

            return {
                "success": True,
                "pipeline_result": pipeline_result,
                "quality_result": quality_result,
                "qwen_response": qwen_response,
                "total_time": total_time,
                "optimized_prompt": pipeline_result.final_prompt
            }

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}

    def _call_qwen_model(self, prompt: str, model: str = "qwen-turbo",
                        live_output: bool = True) -> str:
        """Call Qwen model with the optimized prompt."""
        print(f"Calling {self.qwen_models[model]['name']}...")

        # Check if Ollama is available
        try:
            # Check if model is available
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                print("⚠️  Ollama not found. Please install Ollama first:")
                print("   curl -fsSL https://ollama.ai/install.sh | sh")
                return "Error: Ollama not available. Please install Ollama to use Qwen models."

            # Check if specific model is available
            if model not in result.stdout:
                print(f"📥 Downloading {model} model...")
                download_result = subprocess.run(
                    ["ollama", "pull", model],
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minutes timeout for download
                )
                if download_result.returncode != 0:
                    print(f"❌ Failed to download {model}: {download_result.stderr}")
                    return f"Error: Failed to download {model} model."

        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
            return f"Error: Cannot access Ollama - {e}"

        try:
            # Call the model
            if live_output:
                print("\n🤖 Qwen Response:")
                print("-" * 40)

                # Use subprocess.run with live output
                process = subprocess.Popen(
                    ["ollama", "run", model, prompt],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                    universal_newlines=True
                )

                response_lines = []
                while True:
                    output = process.stdout.readline()
                    if output == '' and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
                        response_lines.append(output.strip())

                # Check for errors
                stderr_output = process.stderr.read()
                if stderr_output and "error" in stderr_output.lower():
                    print(f"⚠️  Error in model response: {stderr_output}")

                full_response = '\n'.join(response_lines)
                print("-" * 40)
                return full_response

            else:
                # Non-interactive mode
                result = subprocess.run(
                    ["ollama", "run", model, prompt],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout
                )

                if result.returncode == 0:
                    return result.stdout
                else:
                    error_msg = f"Model call failed: {result.stderr}"
                    print(f"❌ {error_msg}")
                    return error_msg

        except subprocess.TimeoutExpired:
            error_msg = "Model call timed out (2 minutes)"
            print(f"❌ {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error calling model: {e}"
            print(f"❌ {error_msg}")
            return error_msg

    def quick_optimize(self, prompt: str, context: Dict = None) -> str:
        """Quick optimization without detailed output."""
        try:
            pipeline_result = self.pipeline.process_through_pipeline(prompt, context)
            if pipeline_result.success:
                return pipeline_result.final_prompt
            else:
                return f"Pipeline failed: {prompt}"
        except Exception as e:
            return f"Error: {e}"

def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Qwen Optimization CLI - Test prompts with Qwen models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python3 qwen_optimize.py prompt "fix slow api" --clipboard "/var/www/app"

  # Use different model
  python3 qwen_optimize.py prompt "debug authentication" --model qwen-plus

  # Quick mode (no stages)
  python3 qwen_optimize.py prompt "optimize database" --quick

  # Show only optimized prompt
  python3 qwen_optimize.py prompt "plan migration" --optimize-only

  # Interactive mode
  python3 qwen_optimize.py interactive
        """
    )

    parser.add_argument("command",
                       choices=["prompt", "test", "interactive", "install", "models"],
                       help="Command to run")

    parser.add_argument("prompt_text",
                       nargs="?",
                       help="Prompt text to optimize")

    parser.add_argument("--clipboard", "-c",
                       help="Clipboard content or file path context")

    parser.add_argument("--model", "-m",
                       choices=["qwen-turbo", "qwen-plus", "qwen-max"],
                       default="qwen-turbo",
                       help="Qwen model to use")

    parser.add_argument("--quick", "-q",
                       action="store_true",
                       help="Quick mode - minimal output")

    parser.add_argument("--optimize-only", "-o",
                       action="store_true",
                       help="Show only optimized prompt, no AI response")

    parser.add_argument("--no-stages",
                       action="store_true",
                       help="Don't show stage-by-stage processing")

    parser.add_argument("--no-live",
                       action="store_true",
                       help="Don't show live AI output")

    args = parser.parse_args()

    # Initialize Qwen integration
    qwen = QwenIntegration()

    if args.command == "install":
        print("📥 Installing Ollama...")
        print("Visit: https://ollama.ai/download")
        print("Then run: ollama pull qwen-turbo")
        return

    elif args.command == "models":
        print("🤖 Available Qwen Models:")
        for model_id, info in qwen.qwen_models.items():
            print(f"  • {model_id}: {info['name']} ({info['size']}) - {info['speed']} speed")
        return

    elif args.command == "interactive":
        print("🎮 Interactive Mode")
        print("=" * 30)

        while True:
            try:
                prompt = input("\nEnter prompt (or 'quit'): ").strip()
                if prompt.lower() in ['quit', 'exit', 'q']:
                    break

                clipboard = input("Enter context (optional): ").strip()
                context = {"clipboard": clipboard} if clipboard else {}

                model = input("Model (qwen-turbo/qwen-plus) [qwen-turbo]: ").strip()
                if not model:
                    model = "qwen-turbo"
                elif model not in qwen.qwen_models:
                    model = "qwen-turbo"

                result = qwen.run_optimization_with_qwen(
                    prompt, context, model,
                    show_stages=not args.quick,
                    live_output=not args.no_live
                )

                input("\nPress Enter for next prompt...")

            except KeyboardInterrupt:
                break
        return

    elif args.command == "test":
        # Run predefined tests
        test_cases = [
            "Perform a detailed page-by-page test",
            "make api faster response time",
            "fix authentication not working",
            "plan microservices migration",
            "optimize database queries"
        ]

        for i, test_prompt in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}/{len(test_cases)}: {test_prompt}")
            context = {"clipboard": "/home/yousef/multi-dictate"}

            result = qwen.run_optimization_with_qwen(
                test_prompt, context, "qwen-turbo",
                show_stages=False,
                live_output=False
            )

            if result["success"]:
                print(f"✅ Success - Quality: {result['quality_result'].overall_score:.1f}/100")
            else:
                print(f"❌ Failed - {result.get('error', 'Unknown error')}")

            if i < len(test_cases):
                input("Press Enter for next test...")

        return

    elif args.command == "prompt":
        if not args.prompt_text:
            print("❌ Error: Prompt text required")
            parser.print_help()
            return

        # Prepare context
        context = {}
        if args.clipboard:
            context = {"clipboard": args.clipboard}
        elif not args.clipboard:
            # Try to get from system clipboard
            try:
                result = subprocess.run(['xclip', '-selection', 'clipboard', '-o'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0 and result.stdout.strip():
                    context = {"clipboard": result.stdout.strip()}
                    print(f"📁 Using clipboard context: {result.stdout.strip()[:50]}...")
            except:
                pass

        # Check if only optimization is needed
        if args.optimize_only:
            print("⚡ Quick Optimization Mode")
            print("-" * 30)

            optimized_prompt = qwen.quick_optimize(args.prompt_text, context)
            print("📝 Optimized Prompt:")
            print("=" * 40)
            print(optimized_prompt)
            print("=" * 40)
            return

        # Full optimization with Qwen
        result = qwen.run_optimization_with_qwen(
            args.prompt_text,
            context,
            args.model,
            show_stages=not args.quick and not args.no_stages,
            live_output=not args.no_live
        )

        if not result["success"]:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

        # Success summary
        print(f"\n🎉 Optimization Complete!")
        print(f"📊 Final Quality Score: {result['quality_result'].overall_score:.1f}/100")
        print(f"📈 Improvement Ratio: {result['quality_result'].improvement_ratio:.1f}x")
        print(f"⏱️  Total Time: {result['total_time']:.2f}s")

if __name__ == "__main__":
    main()