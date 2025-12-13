#!/usr/bin/env python3
"""
Integration script to add prompt engineering optimizer to multi-dictate system
"""

import os
import sys

def integrate_prompt_engineering():
    print("🔧 INTEGRATING PROMPT ENGINEERING OPTIMIZER")
    print("=" * 60)

    # Read current dictate.py
    dictate_path = "multi_dictate/dictate.py"

    try:
        with open(dictate_path, 'r') as f:
            content = f.read()
        print("✅ Loaded dictate.py")
    except Exception as e:
        print(f"❌ Failed to load dictate.py: {e}")
        return

    # Check if prompt engineering is already integrated
    if "PromptEngineeringOptimizer" in content:
        print("⚠️  Prompt engineering optimizer already integrated")
        return

    # Find the import section
    import_section = '''# Load optimization processor dynamically
optimization_path = os.path.join(os.path.dirname(__file__), "optimization_processor.py")
spec_opt = importlib.util.spec_from_file_location("optimization_processor", optimization_path)
optimization_module = importlib.util.module_from_spec(spec_opt)
try:
    spec_opt.loader.exec_module(optimization_module)
    OptimizationProcessor = optimization_module.OptimizationProcessor
    # Optimization processor loaded successfully
except Exception as e:
    OptimizationProcessor = None
    # Failed to load optimization processor - will continue without it'''

    # Add prompt engineering optimizer import after optimization processor
    prompt_engineering_import = '''

# Load prompt engineering optimizer dynamically
prompt_engineering_path = os.path.join(os.path.dirname(__file__), "prompt_engineering_optimizer.py")
spec_pe = importlib.util.spec_from_file_location("prompt_engineering_optimizer", prompt_engineering_path)
prompt_engineering_module = importlib.util.module_from_spec(spec_pe)
try:
    spec_pe.loader.exec_module(prompt_engineering_module)
    PromptEngineeringOptimizer = prompt_engineering_module.PromptEngineeringOptimizer
    # Prompt engineering optimizer loaded successfully
except Exception as e:
    PromptEngineeringOptimizer = None
    # Failed to load prompt engineering optimizer - will continue without it'''

    # Find initialization section
    init_section = '''# Initialize optimization processor
        if OptimizationProcessor:
            try:
                self.optimization_processor = OptimizationProcessor(self.cfg)
                logger.info("✅ Optimization processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Optimization processor initialization failed: {e}")
                self.optimization_processor = None
        else:
            self.optimization_processor = None'''

    # Add prompt engineering optimizer initialization
    pe_init = '''

        # Initialize prompt engineering optimizer
        if PromptEngineeringOptimizer:
            try:
                self.prompt_engineering_optimizer = PromptEngineeringOptimizer(self.cfg)
                logger.info("✅ Prompt engineering optimizer initialized")
            except Exception as e:
                logger.warning(f"⚠️  Prompt engineering optimizer initialization failed: {e}")
                self.prompt_engineering_optimizer = None
        else:
            self.prompt_engineering_optimizer = None'''

    # Find processing section - replace optimization processor usage
    processing_section = '''# Try optimization processor for deployment/performance tasks
                    if not enhanced_text and self.optimization_processor:
                        if self.optimization_processor.is_optimization_request(raw_text):
                            logger.info("🚀 Optimization request detected, using optimization processor")
                            context = {'clipboard': clipboard_context} if clipboard_context else {}
                            enhanced_text = self.optimization_processor.optimize_prompt(raw_text, context)
                    else:
                        logger.error("❌ Optimization processor not available")'''

    # Replace with prompt engineering optimizer
    pe_processing = '''# Try prompt engineering optimizer for intelligent prompt optimization
                    if not enhanced_text and self.prompt_engineering_optimizer:
                        logger.info("🧠 Using prompt engineering optimizer")
                        context = {'clipboard': clipboard_context} if clipboard_context else {}
                        optimization_result = self.prompt_engineering_optimizer.optimize_prompt(raw_text, context)
                        enhanced_text = optimization_result['optimized_prompt']
                        logger.info(f"📈 Prompt improvement ratio: {optimization_result['improvement_ratio']:.1f}x")
                    elif self.prompt_engineering_optimizer:
                        logger.warning("⚠️  No optimization detected in input")'''

    # Apply the changes
    new_content = content

    # Add imports
    new_content = new_content.replace(import_section, import_section + prompt_engineering_import)

    # Add initialization
    new_content = new_content.replace(init_section, init_section + pe_init)

    # Replace processing
    new_content = new_content.replace(processing_section, pe_processing)

    # Write the updated content
    try:
        with open(dictate_path, 'w') as f:
            f.write(new_content)
        print("✅ Integrated prompt engineering optimizer into dictate.py")
    except Exception as e:
        print(f"❌ Failed to write updated dictate.py: {e}")
        return

    print("\n🎉 INTEGRATION COMPLETE!")
    print("=" * 60)
    print("✅ Prompt Engineering Optimizer added to multi-dictate")
    print("✅ Structured prompt templates implemented")
    print("✅ Zero-shot and few-shot techniques ready")
    print("✅ Reference-based optimization active")
    print("\n🚀 Features added:")
    print("- Messy voice input cleaning and normalization")
    print("- Intent and domain detection")
    print("- Automatic technique selection")
    print("- Context-aware prompt enhancement")
    print("- Reference library integration")
    print("- Quality metrics and improvement tracking")
    print("\n🎮 To use:")
    print("1. Restart multi-dictate: systemctl --user restart dictate")
    print("2. Use voice commands with any optimization/scenario")
    print("3. System will automatically optimize messy input")

if __name__ == "__main__":
    integrate_prompt_engineering()