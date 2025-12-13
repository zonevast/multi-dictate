#!/usr/bin/env python3
"""
Integrate enhanced reference system with prompt engineering optimizer
"""

import os

def integrate_enhanced_system():
    print("🔧 INTEGRATING ENHANCED REFERENCE SYSTEM")
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

    # Check if enhanced reference system is already integrated
    if "EnhancedReferenceSystem" in content:
        print("⚠️  Enhanced reference system already integrated")
        return

    # Add enhanced reference system import
    import_section = '''# Load prompt engineering optimizer dynamically
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

    enhanced_import = '''

# Load enhanced reference system dynamically
enhanced_ref_path = os.path.join(os.path.dirname(__file__), "enhanced_reference_system.py")
spec_ref = importlib.util.spec_from_file_location("enhanced_reference_system", enhanced_ref_path)
enhanced_ref_module = importlib.util.module_from_spec(spec_ref)
try:
    spec_ref.loader.exec_module(enhanced_ref_module)
    EnhancedReferenceSystem = enhanced_ref_module.EnhancedReferenceSystem
    # Enhanced reference system loaded successfully
except Exception as e:
    EnhancedReferenceSystem = None
    # Failed to load enhanced reference system - will continue without it'''

    # Add initialization
    init_section = '''# Initialize prompt engineering optimizer
        if PromptEngineeringOptimizer:
            try:
                self.prompt_engineering_optimizer = PromptEngineeringOptimizer(self.cfg)
                logger.info("✅ Prompt engineering optimizer initialized")
            except Exception as e:
                logger.warning(f"⚠️  Prompt engineering optimizer initialization failed: {e}")
                self.prompt_engineering_optimizer = None
        else:
            self.prompt_engineering_optimizer = None'''

    enhanced_init = '''

        # Initialize enhanced reference system
        if EnhancedReferenceSystem:
            try:
                self.enhanced_reference_system = EnhancedReferenceSystem()
                logger.info("✅ Enhanced reference system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Enhanced reference system initialization failed: {e}")
                self.enhanced_reference_system = None
        else:
            self.enhanced_reference_system = None'''

    # Replace processing section
    processing_section = '''# Try prompt engineering optimizer for intelligent prompt optimization
                    if not enhanced_text and self.prompt_engineering_optimizer:
                        logger.info("🧠 Using prompt engineering optimizer")
                        context = {'clipboard': clipboard_context} if clipboard_context else {}
                        optimization_result = self.prompt_engineering_optimizer.optimize_prompt(raw_text, context)
                        enhanced_text = optimization_result['optimized_prompt']
                        logger.info(f"📈 Prompt improvement ratio: {optimization_result['improvement_ratio']:.1f}x")
                    elif self.prompt_engineering_optimizer:
                        logger.warning("⚠️  No optimization detected in input")'''

    enhanced_processing = '''# Try prompt engineering optimizer for intelligent prompt optimization
                    if not enhanced_text and self.prompt_engineering_optimizer:
                        logger.info("🧠 Using prompt engineering optimizer")
                        context = {'clipboard': clipboard_context} if clipboard_context else {}
                        optimization_result = self.prompt_engineering_optimizer.optimize_prompt(raw_text, context)

                        # Enhance with reference system if available
                        if self.enhanced_reference_system:
                            url_match = re.search(r'https?://[^\s<>"{}|\\^`[\]]+', raw_text + " " + str(clipboard_context or ""))
                            url = url_match.group(0) if url_match else None

                            enhanced_text = self.enhanced_reference_system.enhance_prompt_with_references(
                                optimization_result['optimized_prompt'],
                                url,
                                {'original_input': raw_text, 'clipboard': clipboard_context}
                            )
                            logger.info("🔗 Enhanced with page-specific and domain references")
                        else:
                            enhanced_text = optimization_result['optimized_prompt']

                        logger.info(f"📈 Prompt improvement ratio: {optimization_result['improvement_ratio']:.1f}x")
                    elif self.prompt_engineering_optimizer:
                        logger.warning("⚠️  No optimization detected in input")'''

    # Apply the changes
    new_content = content

    # Add imports
    new_content = new_content.replace(import_section, import_section + enhanced_import)

    # Add initialization
    new_content = new_content.replace(init_section, init_section + enhanced_init)

    # Replace processing
    new_content = new_content.replace(processing_section, enhanced_processing)

    # Write the updated content
    try:
        with open(dictate_path, 'w') as f:
            f.write(new_content)
        print("✅ Integrated enhanced reference system into dictate.py")
    except Exception as e:
        print(f"❌ Failed to write updated dictate.py: {e}")
        return

    print("\n🎉 ENHANCED SYSTEM INTEGRATION COMPLETE!")
    print("=" * 60)
    print("✅ Enhanced reference system added to multi-dictate")
    print("✅ Page-specific templates with URL detection")
    print("✅ Domain-specific examples (plumbing, engineering, medical)")
    print("✅ Complex deployment scenarios")
    print("✅ Directory-based file analysis")
    print("✅ Reference integration in prompts")
    print("\n🚀 Enhanced Features:")
    print("- Dashboard, API, Profile page optimizations")
    print("- Plumbing system design examples")
    print("- Industrial automation scenarios")
    print("- Medical system migration patterns")
    print("- Multi-region deployment strategies")
    print("- Real-time project file analysis")
    print("\n🎮 To use:")
    print("1. Restart multi-dictate: systemctl --user restart dictate")
    print("2. Try complex scenarios:")
    print("   • 'my dashboard is slow and database queries timeout'")
    print("   • 'implement industrial automation with safety compliance'")
    print("   • 'need hospital system migration with HIPAA compliance'")
    print("   • 'deploy trading platform with sub-millisecond latency'")

if __name__ == "__main__":
    integrate_enhanced_system()