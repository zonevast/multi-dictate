#!/usr/bin/env python3
"""Context collection for RAG-enhanced dictation"""

import logging
import subprocess
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class ContextCollector:
    """Collects context from user environment for RAG enhancement"""

    def __init__(self):
        self.last_clipboard = None
        self.clipboard_history = []
        self.app_history = []
        self.max_history = 10

    def collect_all_context(self) -> Dict:
        """Collect all available context"""
        context = {
            'timestamp': datetime.now().isoformat(),
            'time_context': self._get_time_context(),
            'active_window': self._get_active_window(),
            'clipboard_content': self._get_clipboard_content(),
            'recent_applications': self._get_recent_applications(),
            'current_directory': self._get_current_directory(),
            'environment_state': self._get_environment_state()
        }

        # Update histories
        self._update_histories(context)

        return context

    def _get_time_context(self) -> Dict:
        """Get time-based context"""
        now = datetime.now()
        hour = now.hour

        time_context = {
            'hour': hour,
            'day_part': self._get_day_part(hour),
            'day_of_week': now.strftime("%A"),
            'is_weekend': now.weekday() >= 5,
            'energy_suggestion': self._suggest_energy_level(hour)
        }

        return time_context

    def _get_day_part(self, hour: int) -> str:
        """Determine part of day"""
        if 5 <= hour < 9:
            return "early_morning"
        elif 9 <= hour < 12:
            return "morning"
        elif 12 <= hour < 14:
            return "midday"
        elif 14 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 20:
            return "evening"
        elif 20 <= hour < 23:
            return "night"
        else:
            return "late_night"

    def _suggest_energy_level(self, hour: int) -> str:
        """Suggest typical energy level based on time"""
        if 9 <= hour < 11:
            return "peak_cognitive"
        elif 14 <= hour < 16:
            return "second_wind"
        elif hour >= 21 or hour < 6:
            return "wind_down"
        else:
            return "moderate"

    def _get_active_window(self) -> Dict:
        """Get active window information"""
        try:
            # Try xdotool first
            result = subprocess.run(
                ['xdotool', 'getwindowfocus', 'getwindowname'],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0:
                window_name = result.stdout.strip()
                return {
                    'title': window_name,
                    'type': self._classify_window(window_name),
                    'productivity_likely': self._is_productivity_app(window_name)
                }

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Fallback: try wmctrl
        try:
            result = subprocess.run(
                ['wmctrl', '-a', ':ACTIVE:'],
                capture_output=True, text=True, timeout=1
            )
            if result.returncode == 0:
                window_name = result.stdout.strip()
                return {
                    'title': window_name,
                    'type': self._classify_window(window_name),
                    'productivity_likely': self._is_productivity_app(window_name)
                }
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return {
            'title': 'Unknown',
            'type': 'unknown',
            'productivity_likely': False
        }

    def _classify_window(self, title: str) -> str:
        """Classify window type based on title"""
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in ['terminal', 'console', 'shell']):
            return 'terminal'
        elif any(keyword in title_lower for keyword in ['chrome', 'firefox', 'browser', 'safari']):
            return 'browser'
        elif any(keyword in title_lower for keyword in ['code', 'vscode', 'vim', 'emacs', 'intellij']):
            return 'editor'
        elif any(keyword in title_lower for keyword in ['slack', 'discord', 'teams', 'zoom']):
            return 'communication'
        elif any(keyword in title_lower for keyword in ['docs', 'word', 'libreoffice']):
            return 'document'
        elif any(keyword in title_lower for keyword in ['spotify', 'music', 'vlc', 'youtube']):
            return 'media'
        else:
            return 'other'

    def _is_productivity_app(self, title: str) -> bool:
        """Check if app is typically used for productivity"""
        productive_types = ['terminal', 'editor', 'document', 'browser']
        window_type = self._classify_window(title)
        return window_type in productive_types

    def _get_clipboard_content(self) -> Dict:
        """Get current clipboard content"""
        try:
            result = subprocess.run(
                ['xclip', '-selection', 'clipboard', '-o'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0:
                content = result.stdout.strip()
                if content:
                    # Check if it's different from last
                    is_new = content != self.last_clipboard
                    self.last_clipboard = content

                    return {
                        'content': content,
                        'length': len(content),
                        'is_new': is_new,
                        'type': self._classify_content(content)
                    }

        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return {
            'content': None,
            'length': 0,
            'is_new': False,
            'type': None
        }

    def _classify_content(self, content: str) -> str:
        """Classify clipboard content type"""
        if not content:
            return None

        content_lower = content.lower()
        lines = content.split('\n')

        # Check for code
        if any(line.strip().endswith(('{', '}', ':', ';')) for line in lines[:5]):
            return 'code'

        # Check for URLs
        if content.startswith(('http://', 'https://')):
            return 'url'

        # Check for error messages
        error_keywords = ['error', 'exception', 'failed', 'traceback', 'stack trace']
        if any(keyword in content_lower for keyword in error_keywords):
            return 'error'

        # Check for questions
        if content.endswith('?'):
            return 'question'

        # Check for lists/tasks
        if any(line.strip().startswith(('-', '*', '1.', '2.')) for line in lines):
            return 'list'

        # Check for emotional/mood content
        mood_keywords = ['feel', 'feeling', 'mood', 'tired', 'energetic', 'stressed', 'happy']
        if any(keyword in content_lower for keyword in mood_keywords):
            return 'mood_related'

        return 'text'

    def _get_recent_applications(self) -> List[str]:
        """Get list of recent applications from history"""
        return self.app_history[-5:] if self.app_history else []

    def _get_current_directory(self) -> Dict:
        """Get current working directory information"""
        try:
            cwd = os.getcwd()
            return {
                'path': cwd,
                'basename': os.path.basename(cwd),
                'is_home': cwd == os.path.expanduser('~'),
                'is_project': self._is_project_directory(cwd)
            }
        except Exception:
            return {
                'path': None,
                'basename': None,
                'is_home': False,
                'is_project': False
            }

    def _is_project_directory(self, path: str) -> bool:
        """Check if current directory looks like a project"""
        project_indicators = [
            'package.json', 'requirements.txt', 'Cargo.toml', 'pyproject.toml',
            'Gemfile', 'go.mod', 'composer.json', '.git', 'Makefile'
        ]

        for indicator in project_indicators:
            if os.path.exists(os.path.join(path, indicator)):
                return True

        return False

    def _get_environment_state(self) -> Dict:
        """Get general environment state"""
        state = {
            'desktop_environment': self._detect_desktop_environment(),
            'has_active_notifications': self._check_notifications(),
            'system_load': self._get_system_load()
        }

        return state

    def _detect_desktop_environment(self) -> str:
        """Detect desktop environment"""
        desktop = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()

        if 'gnome' in desktop:
            return 'gnome'
        elif 'kde' in desktop:
            return 'kde'
        elif 'ubuntu' in desktop:
            return 'ubuntu'
        elif 'pop' in desktop:
            return 'pop_os'
        else:
            return 'unknown'

    def _check_notifications(self) -> bool:
        """Check if there are active notifications"""
        # Simplified check - could be enhanced with actual notification monitoring
        return False

    def _get_system_load(self) -> Dict:
        """Get system load information"""
        try:
            result = subprocess.run(['uptime'], capture_output=True, text=True)
            if result.returncode == 0:
                # Parse load average from uptime output
                output = result.stdout
                if 'load average:' in output:
                    load_part = output.split('load average:')[1].strip()
                    loads = [float(x) for x in load_part.split(',')]
                    return {
                        '1min': loads[0],
                        '5min': loads[1],
                        '15min': loads[2],
                        'is_high': loads[0] > 2.0
                    }
        except Exception:
            pass

        return {
            '1min': None,
            '5min': None,
            '15min': None,
            'is_high': False
        }

    def _update_histories(self, context: Dict):
        """Update internal histories with new context"""
        # Update app history
        if 'active_window' in context:
            app_title = context['active_window']['title']
            if not self.app_history or self.app_history[-1] != app_title:
                self.app_history.append(app_title)
                if len(self.app_history) > self.max_history:
                    self.app_history.pop(0)

        # Update clipboard history periodically
        if context['clipboard_content']['is_new']:
            self.clipboard_history.append({
                'content': context['clipboard_content']['content'],
                'timestamp': context['timestamp'],
                'type': context['clipboard_content']['type']
            })
            if len(self.clipboard_history) > self.max_history:
                self.clipboard_history.pop(0)

    def get_context_summary(self) -> str:
        """Get human-readable summary of current context"""
        context = self.collect_all_context()

        summary_parts = []

        # Time context
        time_part = context['time_context']
        summary_parts.append(f"Current time: {time_part['day_part']} (hour {time_part['hour']})")

        # Active window
        if context['active_window']['title'] != 'Unknown':
            summary_parts.append(f"Active: {context['active_window']['type']} window")

        # Clipboard
        if context['clipboard_content']['content']:
            clip_type = context['clipboard_content']['type'] or 'text'
            summary_parts.append(f"Clipboard contains {clip_type}")

        # Environment
        env = context['environment_state']
        if env['system_load']['is_high']:
            summary_parts.append("System load is high")

        return " | ".join(summary_parts)