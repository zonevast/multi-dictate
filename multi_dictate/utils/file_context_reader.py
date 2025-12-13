#!/usr/bin/env python3
"""
File Context Reader - Separate from ChromaDB RAG
Reads files from clipboard paths and provides context
This is NOT stored in ChromaDB - just temporary enhancement
"""

import os
import glob
from pathlib import Path
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class FileContextReader:
    """Reads file content from clipboard paths - separate from ChromaDB memory"""

    def __init__(self):
        self.max_file_size = 2000  # Max characters per file
        self.max_files = 3         # Max files to read

    def read_from_clipboard(self, clipboard_content: str) -> Dict:
        """Read file content from clipboard path"""
        if not clipboard_content or not isinstance(clipboard_content, str):
            return {"success": False, "content": "", "files_found": 0}

        try:
            # Check if clipboard looks like a file path
            if clipboard_content.strip().startswith('/') and os.path.exists(clipboard_content.strip()):
                path = Path(clipboard_content.strip())

                if path.is_file():
                    return self._read_single_file(path)
                elif path.is_dir():
                    return self._read_directory(path)

            # Check if clipboard contains multiple file paths
            return self._read_multiple_files(clipboard_content)

        except Exception as e:
            logger.warning(f"Could not read files from clipboard: {e}")
            return {"success": False, "content": f"❌ Error reading files: {e}", "files_found": 0}

    def _read_single_file(self, file_path: Path) -> Dict:
        """Read a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Truncate if too long
            if len(content) > self.max_file_size:
                content = content[:self.max_file_size] + "\n...[truncated]"

            return {
                "success": True,
                "content": f"📄 File: {file_path.name}\n{content}",
                "files_found": 1,
                "file_names": [file_path.name],
                "file_paths": [str(file_path)]
            }
        except Exception as e:
            return {
                "success": False,
                "content": f"📄 File: {file_path.name}\n❌ Could not read: {e}",
                "files_found": 0
            }

    def _read_directory(self, dir_path: Path) -> Dict:
        """Read relevant files from directory"""
        content_parts = []
        files_read = 0
        file_names = []

        # Priority files to look for
        priority_files = [
            'WORKFLOW_RULES.md', 'workflow_rules.md', 'WORKFLOW.md', 'workflow.md',
            'README.md', 'TESTING.md', 'DEPLOYMENT.md', 'ARCHITECTURE.md',
            'package.json', 'requirements.txt', 'docker-compose.yml',
            'application.properties', 'appsettings.json', 'config.json',
            'docker-compose.yml', 'pom.xml', 'build.gradle', 'Cargo.toml'
        ]

        # Look for priority files first
        for priority_file in priority_files:
            file_path = dir_path / priority_file
            if file_path.exists() and file_path.is_file():
                file_content = self._safe_read_file(file_path)
                if file_content:
                    content_parts.append(file_content)
                    files_read += 1
                    file_names.append(priority_file)
                    if files_read >= self.max_files:
                        break

        # Initialize priority files list
        priority_files_sorted = []

        # If no priority files found, search for relevant code/config files
        if files_read == 0:
            # Define relevant file patterns for analysis
            relevant_patterns = [
                "*.java", "*.py", "*.js", "*.ts", "*.go", "*.rs", "*.cpp", "*.c",
                "*.json", "*.yml", "*.yaml", "*.xml", "*.properties", "*.env", "*.config",
                "*.sql", "*.sh", "*.bat", "*.md", "*.txt"
            ]

            # Search for relevant files recursively (limit depth to avoid too many files)
            found_files = []
            for pattern in relevant_patterns:
                for file_path in dir_path.glob(f"**/{pattern}"):
                    # Limit to first level and common directories
                    depth = len(file_path.relative_to(dir_path).parts)
                    if depth <= 8:  # Limit depth to 8 levels (to accommodate Java/Maven project structures)
                        found_files.append(file_path)

            # Sort by priority (config files first, then main code files)
            config_files = [f for f in found_files if f.suffix in ['.json', '.yml', '.yaml', '.properties', '.env', '.config', '.xml']]
            code_files = [f for f in found_files if f.suffix in ['.java', '.py', '.js', '.ts', '.go', '.rs', '.cpp', '.c']]
            other_files = [f for f in found_files if f not in config_files and f not in code_files]

            # Take files in priority order, preferring config and main code files
            priority_files_sorted = config_files[:2] + code_files[:3] + other_files[:2]

            for file_path in priority_files_sorted:
                if files_read >= self.max_files:
                    break
                file_content = self._safe_read_file(file_path)
                if file_content:
                    content_parts.append(file_content)
                    files_read += 1
                    file_names.append(file_path.name)

        if content_parts:
            directory_name = dir_path.name
            content = f"📁 Directory: {directory_name}\n\n" + "\n\n".join(content_parts)
            return {
                "success": True,
                "content": content,
                "files_found": files_read,
                "file_names": file_names,
                "file_paths": [str(path) for path in priority_files_sorted[:files_read]],  # Add full paths as strings
                "directory": directory_name
            }

        return {
            "success": False,
            "content": f"📁 Directory: {dir_path.name}\n📄 No readable files found",
            "files_found": 0,
            "file_names": [],
            "file_paths": []
        }

    def _read_multiple_files(self, clipboard_content: str) -> Dict:
        """Read multiple file paths from clipboard"""
        lines = [line.strip() for line in clipboard_content.split('\n') if line.strip()]
        file_paths = [line for line in lines if line.startswith('/') and os.path.exists(line)]

        if not file_paths:
            return {"success": False, "content": "", "files_found": 0}

        content_parts = [f"📁 {len(file_paths)} Files from Clipboard:"]
        files_read = 0
        file_names = []

        for file_path in file_paths[:self.max_files]:
            path = Path(file_path)
            file_content = self._safe_read_file(path)
            if file_content:
                content_parts.append(file_content)
                files_read += 1
                file_names.append(path.name)

        return {
            "success": True,
            "content": "\n".join(content_parts),
            "files_found": files_read,
            "file_names": file_names
        }

    def _safe_read_file(self, file_path: Path) -> Optional[str]:
        """Safely read a file with error handling"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Limit content size
            if len(content) > self.max_file_size:
                content = content[:self.max_file_size] + "\n...[truncated]"

            return f"📄 {file_path.name}:\n{content}"
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return f"📄 {file_path.name}:\n❌ Could not read: {e}"

    def get_file_summary(self, clipboard_content: str) -> Dict:
        """Get a summary of what files would be read without reading them"""
        if not clipboard_content or not isinstance(clipboard_content, str):
            return {"files_found": 0, "file_names": []}

        try:
            if clipboard_content.strip().startswith('/') and os.path.exists(clipboard_content.strip()):
                path = Path(clipboard_content.strip())

                if path.is_file():
                    return {"files_found": 1, "file_names": [path.name]}
                elif path.is_dir():
                    # Look for priority files
                    priority_files = ['WORKFLOW_RULES.md', 'workflow_rules.md', 'README.md']
                    found_files = []
                    for pf in priority_files:
                        if (path / pf).exists():
                            found_files.append(pf)
                    return {"files_found": len(found_files), "file_names": found_files}

            return {"files_found": 0, "file_names": []}
        except Exception as e:
            return {"files_found": 0, "file_names": [], "error": str(e)}