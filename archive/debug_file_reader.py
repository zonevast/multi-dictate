#!/usr/bin/env python3
"""Debug the file reader to see why it's not finding files"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(__file__))

from multi_dictate.file_context_reader import FileContextReader
from pathlib import Path

def debug_file_reader():
    """Debug file reader to see what it's finding"""
    print("🔍 DEBUGGING FILE READER")
    print("=" * 50)

    reader = FileContextReader()

    # Create test directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create banking project structure
        os.makedirs(f"{temp_dir}/banking-service/src/main/java/com/bank/controller", exist_ok=True)
        os.makedirs(f"{temp_dir}/config", exist_ok=True)

        # Create Java file
        java_file = f"{temp_dir}/banking-service/src/main/java/com/bank/controller/CustomerController.java"
        with open(java_file, 'w') as f:
            f.write("""
public class CustomerController {
    private static final String TEST_ACCOUNT = "123-FAKE-456";
    private static final String DEMO_EMAIL = "fake@bank.example";
}
""")

        # Create JSON config file
        config_file = f"{temp_dir}/config/banking-config.json"
        with open(config_file, 'w') as f:
            f.write("""
{
    "database": "postgresql://bank_user:fake_pass@localhost:5432/banking_db",
    "api_endpoints": {
        "test": "https://test.bank.example.com/api"
    }
}
""")

        print(f"📁 Created test directory: {temp_dir}")
        print(f"📄 Java file: {java_file}")
        print(f"📄 Config file: {config_file}")
        print()

        # Test what files are found by the reader
        print("🧪 Testing File Context Reader...")

        path_obj = Path(temp_dir)
        print(f"Path exists: {path_obj.exists()}")
        print(f"Path is directory: {path_obj.is_dir()}")
        print()

        # Manually check what files would be found
        relevant_patterns = [
            "*.java", "*.py", "*.js", "*.ts", "*.json", "*.yml", "*.yaml", "*.xml", "*.properties", "*.env", "*.config"
        ]

        print("🔍 All files in directory (for debugging):")
        for file_path in path_obj.glob("**/*"):
            if file_path.is_file():
                print(f"   File: {file_path}")
                depth = len(file_path.relative_to(path_obj).parts)
                print(f"      Depth: {depth}")
                print(f"      Extension: {file_path.suffix}")

        print("\n🔍 Manual file search:")
        found_files = []
        for pattern in relevant_patterns:
            for file_path in path_obj.glob(f"**/{pattern}"):
                depth = len(file_path.relative_to(path_obj).parts)
                if depth <= 8:  # Updated to match file reader (Java/Maven depth)
                    found_files.append(file_path)
                    print(f"   Found: {file_path} (depth: {depth})")

        print(f"\n📊 Total files found: {len(found_files)}")

        # Test the actual file reader
        print(f"\n🧪 Testing File Context Reader result:")
        result = reader.read_from_clipboard(temp_dir)
        print(f"Success: {result.get('success')}")
        print(f"Files found: {result.get('files_found')}")
        print(f"File names: {result.get('file_names', [])}")

        if result.get('content'):
            print(f"Content preview (first 200 chars):")
            print(result['content'][:200] + "...")

if __name__ == '__main__':
    debug_file_reader()