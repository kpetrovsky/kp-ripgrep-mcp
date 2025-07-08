"""Ripgrep wrapper functions and Obsidian pattern matching."""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import yaml
import platform


class RipgrepWrapper:
    """Wrapper for ripgrep with Obsidian-specific patterns and functionality."""
    
    # Obsidian-specific patterns
    PATTERNS = {
        'wiki_links': r'\[\[([^\]]+)\]\]',
        'markdown_links': r'\[([^\]]*)\]\(([^)]+)\)',
        'frontmatter_links_quoted': r'"?\[\[([^\]]+)\]\]"?',
        'frontmatter_links_in_quotes': r'"([^"]*\[\[[^\]]+\]\][^"]*)"',
        'external_urls': r'https?://[^\s\)\"\']+',
        'tags': r'#[A-Za-z][A-Za-z0-9/_-]*',
        'frontmatter_block': r'^---\n(.*?)\n---',
        'headers': r'^#{1,6}\s+(.+)'
    }
    
    def __init__(self, vault_path: str):
        """Initialize with vault path."""
        self.vault_path = Path(vault_path)
        
        # Check if ripgrep is available
        rg_commands = ['rg', 'rg.exe']
        self.rg_command = None
        
        for cmd in rg_commands:
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, check=True, text=True, encoding='utf-8', errors='replace')
                self.rg_command = cmd
                print(f"Found ripgrep: {cmd} - {result.stdout.split()[1]}", file=sys.stderr)
                break
            except (subprocess.CalledProcessError, FileNotFoundError):
                continue
        
        if not self.rg_command:
            raise RuntimeError(
                "ripgrep (rg) is not installed or not in PATH. "
                "Please install ripgrep and ensure it's available in your PATH. "
                "On Windows, try 'winget install BurntSushi.ripgrep.MSVC'"
            )
    
    def _convert_path_for_rg(self, path: str) -> str:
        """Convert path format for ripgrep based on OS and ripgrep version."""
        # If we're on WSL and using rg.exe (Windows ripgrep), convert WSL paths to Windows paths
        if (platform.system() == "Linux" and 
            ("Microsoft" in platform.release() or "microsoft" in platform.release() or "WSL" in platform.release()) and 
            self.rg_command and self.rg_command.endswith('.exe')):
            try:
                # Use wslpath to convert WSL path to Windows path
                result = subprocess.run(['wslpath', '-w', path], 
                                      capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
                return result.stdout.strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                # If wslpath fails, fall back to original path
                pass
        return path
    
    def _build_rg_command(
        self,
        pattern: str,
        case_sensitive: bool = False,
        folder: Optional[str] = None,
        file_types: Optional[List[str]] = None,
        max_count: int = 15,
        context_lines: int = 1,
        json_output: bool = True
    ) -> List[str]:
        """Build ripgrep command with specified options."""
        cmd = [self.rg_command]
        
        # Basic options
        if not case_sensitive:
            cmd.append('--ignore-case')
        
        if json_output:
            cmd.append('--json')
        
        # Note: --context with --json can cause issues, and --max-count is per-file
        # For better compatibility, use simpler parameters
        cmd.extend(['--max-count', str(max_count)])
        
        # File type filtering
        if file_types:
            for file_type in file_types:
                cmd.extend(['--type', file_type])
        else:
            # Default to markdown files for Obsidian
            cmd.extend(['--glob', '*.md'])
        
        # Exclude Obsidian config directory
        cmd.extend(['--glob', '!.obsidian/**'])
        
        # Sort by modification time (newest first)
        cmd.extend(['--sortr', 'modified'])
        
        # Add pattern
        cmd.append(pattern)
        
        # Add search path
        search_path = self.vault_path
        if folder:
            search_path = self.vault_path / folder
        cmd.append(self._convert_path_for_rg(str(search_path)))
        
        return cmd
    
    def _parse_rg_json_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse ripgrep JSON output into structured results."""
        results = []
        
        if not output:
            return results
        
        for line in output.strip().split('\n'):
            if not line:
                continue
            
            try:
                data = json.loads(line)
                if data.get('type') == 'match':
                    match_data = data.get('data', {})
                    file_path = match_data.get('path', {}).get('text', '')
                    # Convert absolute path back to relative path
                    try:
                        if file_path.startswith(str(self.vault_path)):
                            relative_path = str(Path(file_path).relative_to(self.vault_path))
                        else:
                            # Handle Windows paths in WSL
                            vault_path_win = self._convert_path_for_rg(str(self.vault_path)).replace('\\', '/')
                            file_path_normalized = file_path.replace('\\', '/')
                            if vault_path_win and file_path_normalized.startswith(vault_path_win):
                                relative_path = file_path_normalized[len(vault_path_win):].lstrip('/')
                            else:
                                relative_path = Path(file_path).name
                    except ValueError:
                        relative_path = Path(file_path).name
                    
                    results.append({
                        'file': relative_path,
                        'line_number': match_data.get('line_number'),
                        'text': match_data.get('lines', {}).get('text', '') or '',
                        'match_start': match_data.get('submatches', [{}])[0].get('start', 0),
                        'match_end': match_data.get('submatches', [{}])[0].get('end', 0),
                    })
            except (json.JSONDecodeError, KeyError):
                continue
        
        return results
    
    def search_content(
        self,
        query: str,
        case_sensitive: bool = False,
        folder: Optional[str] = None,
        max_results: int = 15,
        smart_context: bool = True
    ) -> List[Dict[str, Any]]:
        """Search for content in markdown files."""
        cmd = self._build_rg_command(
            pattern=query,
            case_sensitive=case_sensitive,
            folder=folder,
            max_count=max_results
        )
        
        try:
            print(f"DEBUG: Executing ripgrep command: {' '.join(cmd)}", file=sys.stderr)
            print(f"DEBUG: Working directory: {os.getcwd()}", file=sys.stderr)
            print(f"DEBUG: Vault path exists: {Path(self.vault_path).exists()}", file=sys.stderr)
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            print(f"DEBUG: Command return code: {result.returncode}", file=sys.stderr)
            print(f"DEBUG: stdout length: {len(result.stdout) if result.stdout else 0}", file=sys.stderr)
            
            if result.stderr:
                print(f"DEBUG: stderr: {result.stderr}", file=sys.stderr)
            
            if result.returncode == 0:
                if not result.stdout:
                    print("DEBUG: No stdout from ripgrep despite return code 0", file=sys.stderr)
                    return []
                
                parsed_results = self._parse_rg_json_output(result.stdout)
                print(f"DEBUG: Parsed {len(parsed_results)} results", file=sys.stderr)
                
                # Add smart context if enabled
                if smart_context:
                    parsed_results = self._add_smart_context(parsed_results)
                
                return parsed_results
            else:
                print(f"DEBUG: Command failed with return code {result.returncode}", file=sys.stderr)
                if result.stderr:
                    print(f"DEBUG: Error details: {result.stderr}", file=sys.stderr)
            return []
        except subprocess.SubprocessError as e:
            print(f"DEBUG: SubprocessError: {e}", file=sys.stderr)
            return []
        except Exception as e:
            print(f"DEBUG: Unexpected error: {e}", file=sys.stderr)
            return []
    
    def search_frontmatter_only(
        self,
        query: str,
        case_sensitive: bool = False,
        folder: Optional[str] = None,
        max_results: int = 15,
        smart_context: bool = True
    ) -> List[Dict[str, Any]]:
        """Search only in frontmatter sections."""
        # Use simpler approach: search for the query and filter results to frontmatter sections
        # This is more reliable than complex regex patterns
        
        cmd = self._build_rg_command(
            pattern=query,
            case_sensitive=case_sensitive,
            folder=folder,
            max_count=max_results * 3  # Get more results to filter
        )
        # Add --pcre2 for better regex support
        cmd.append('--pcre2')
        
        try:
            print(f"DEBUG: Executing ripgrep frontmatter command: {' '.join(cmd)}", file=sys.stderr)
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            print(f"DEBUG: Frontmatter return code: {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(f"DEBUG: Frontmatter stderr: {result.stderr}", file=sys.stderr)
            if result.returncode == 0:
                all_results = self._parse_rg_json_output(result.stdout)
                # Filter to only results within frontmatter sections
                frontmatter_results = self._filter_frontmatter_results(all_results)
                print(f"DEBUG: Frontmatter filtered to {len(frontmatter_results)} results", file=sys.stderr)
                
                # Add smart context if enabled
                if smart_context:
                    frontmatter_results = self._add_smart_context(frontmatter_results)
                
                return frontmatter_results[:max_results]
            return []
        except subprocess.SubprocessError as e:
            print(f"DEBUG: Frontmatter SubprocessError: {e}", file=sys.stderr)
            return []
    
    def search_content_only(
        self,
        query: str,
        case_sensitive: bool = False,
        folder: Optional[str] = None,
        max_results: int = 15,
        smart_context: bool = True
    ) -> List[Dict[str, Any]]:
        """Search only in content (excluding frontmatter)."""
        # Use simpler approach: search for the query and filter results to content sections
        # This is more reliable than complex regex patterns
        
        cmd = self._build_rg_command(
            pattern=query,
            case_sensitive=case_sensitive,
            folder=folder,
            max_count=max_results * 3  # Get more results to filter
        )
        # Add --pcre2 for better regex support
        cmd.append('--pcre2')
        
        try:
            print(f"DEBUG: Executing ripgrep content-only command: {' '.join(cmd)}", file=sys.stderr)
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            print(f"DEBUG: Content-only return code: {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(f"DEBUG: Content-only stderr: {result.stderr}", file=sys.stderr)
            if result.returncode == 0:
                all_results = self._parse_rg_json_output(result.stdout)
                # Filter to only results outside frontmatter sections
                content_results = self._filter_content_results(all_results)
                print(f"DEBUG: Content-only filtered to {len(content_results)} results", file=sys.stderr)
                
                # Add smart context if enabled
                if smart_context:
                    content_results = self._add_smart_context(content_results)
                
                return content_results[:max_results]
            return []
        except subprocess.SubprocessError as e:
            print(f"DEBUG: Content-only SubprocessError: {e}", file=sys.stderr)
            return []
    
    def _filter_frontmatter_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter results to only include those within frontmatter sections."""
        frontmatter_results = []
        
        for result in results:
            try:
                file_path = self.vault_path / result['file']
                if not file_path.exists():
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                line_num = result['line_number']
                # Check if this line is within a frontmatter block
                if self._is_line_in_frontmatter(lines, line_num):
                    frontmatter_results.append(result)
                    
            except (IOError, KeyError):
                continue
                
        return frontmatter_results
    
    def _filter_content_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter results to only include those outside frontmatter sections."""
        content_results = []
        
        for result in results:
            try:
                file_path = self.vault_path / result['file']
                if not file_path.exists():
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                line_num = result['line_number']
                # Check if this line is NOT within a frontmatter block
                if not self._is_line_in_frontmatter(lines, line_num):
                    content_results.append(result)
                    
            except (IOError, KeyError):
                continue
                
        return content_results
    
    def _is_line_in_frontmatter(self, lines: List[str], line_num: int) -> bool:
        """Check if a specific line number is within a frontmatter block."""
        if not lines or line_num < 1 or line_num > len(lines):
            return False
            
        # Check if the file starts with frontmatter
        if not lines[0].strip().startswith('---'):
            return False
            
        # Find the end of frontmatter block
        frontmatter_end = None
        for i, line in enumerate(lines[1:], 1):  # Start from line 2 (index 1)
            if line.strip() == '---':
                frontmatter_end = i + 1  # Line numbers are 1-based
                break
                
        if frontmatter_end is None:
            return False
            
        # Check if our line is within the frontmatter block (lines 1 to frontmatter_end)
        return 1 <= line_num <= frontmatter_end
    
    def _add_smart_context(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Add smart context to search results based on location (frontmatter property or content heading)."""
        enhanced_results = []
        
        for result in results:
            enhanced_result = result.copy()
            
            try:
                file_path = self.vault_path / result['file']
                if not file_path.exists():
                    enhanced_results.append(enhanced_result)
                    continue
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                line_num = result['line_number']
                
                # Check if this is in frontmatter
                if self._is_line_in_frontmatter(lines, line_num):
                    # Get frontmatter property context
                    property_context = self._get_frontmatter_property_context(lines, line_num)
                    if property_context:
                        enhanced_result['smart_context'] = property_context
                else:
                    # Get content heading context
                    heading_context = self._get_content_heading_context(lines, line_num)
                    if heading_context:
                        enhanced_result['smart_context'] = heading_context
                        
            except (IOError, KeyError):
                # If we can't read the file or parse it, just use the original result
                pass
                
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def _get_frontmatter_property_context(self, lines: List[str], line_num: int) -> Optional[str]:
        """Get the frontmatter property name for a given line number."""
        
        if not lines or line_num < 1 or line_num > len(lines):
            return None
        
        # Parse the frontmatter as YAML to understand the structure
        try:
            # Find frontmatter boundaries
            if not lines[0].strip().startswith('---'):
                return None
            
            frontmatter_end = None
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == '---':
                    frontmatter_end = i + 1
                    break
            
            if frontmatter_end is None:
                return None
            
            
            # Just find the property context for this line
            result = self._find_property_context_for_line(lines, line_num, frontmatter_end)
            return result
            
        except Exception as e:
            pass
        
        return None
    
    def _find_property_context_for_line(self, lines: List[str], line_num: int, frontmatter_end: int) -> Optional[str]:
        """Find the property context for a specific line in frontmatter."""
        if line_num < 1 or line_num > len(lines):
            return None
        
        # Work backwards from the target line to find the property name
        target_line = lines[line_num - 1]
        target_indent = len(target_line) - len(target_line.lstrip())
        
        # Check if the target line itself is a property definition
        if ':' in target_line and not target_line.strip().endswith(':'):
            # This line contains a colon and is not just a property header
            # Extract property name (everything before the colon)
            property_name = target_line.split(':')[0].strip()
            if property_name and not property_name.startswith('-'):  # Not a list item
                return property_name
        
        # Look backwards for a property definition at a lower indent level
        for i in range(line_num - 2, 0, -1):  # Go backwards from line before target
            line = lines[i]
            if line.strip() == '':  # Skip empty lines
                continue
            
            line_indent = len(line) - len(line.lstrip())
            
            # If this line has lower indentation and contains a colon, it's a parent property
            if line_indent < target_indent and ':' in line:
                # Extract property name (everything before the colon)
                property_name = line.split(':')[0].strip()
                if property_name:
                    return property_name
        
        return None
    
    def _get_content_heading_context(self, lines: List[str], line_num: int) -> Optional[str]:
        """Get the heading context for a given line number in content."""
        if not lines or line_num < 1 or line_num > len(lines):
            return None
        
        # Find the most recent heading before this line
        for i in range(line_num - 1, -1, -1):  # Go backwards from target line
            line = lines[i].strip()
            if line.startswith('#'):
                # Extract heading text (remove # symbols and strip)
                heading_text = line.lstrip('#').strip()
                if heading_text:
                    return heading_text
        
        return None
    
    def find_links(
        self,
        link_type: str = 'all',
        url_pattern: Optional[str] = None,
        title_pattern: Optional[str] = None,
        case_sensitive: bool = False,
        folder: Optional[str] = None,
        max_results: int = 15
    ) -> List[Dict[str, Any]]:
        """Find links of specified type with optional filtering."""
        patterns = []
        
        if link_type in ('all', 'wiki_links'):
            patterns.append(self.PATTERNS['wiki_links'])
        if link_type in ('all', 'markdown_links'):
            patterns.append(self.PATTERNS['markdown_links'])
        if link_type in ('all', 'external_urls'):
            patterns.append(self.PATTERNS['external_urls'])
        
        if not patterns:
            return []
        
        # Combine patterns with OR
        combined_pattern = '|'.join(f'({p})' for p in patterns)
        
        cmd = self._build_rg_command(
            pattern=combined_pattern,
            case_sensitive=case_sensitive,
            folder=folder,
            max_count=max_results
        )
        
        try:
            print(f"DEBUG: Executing ripgrep find_links command: {' '.join(cmd)}", file=sys.stderr)
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
            print(f"DEBUG: Find_links return code: {result.returncode}", file=sys.stderr)
            if result.stderr:
                print(f"DEBUG: Find_links stderr: {result.stderr}", file=sys.stderr)
            if result.returncode == 0:
                matches = self._parse_rg_json_output(result.stdout)
                print(f"DEBUG: Find_links parsed {len(matches)} raw matches", file=sys.stderr)
                processed = self._process_link_matches(matches, url_pattern, title_pattern)
                print(f"DEBUG: Find_links processed {len(processed)} link matches", file=sys.stderr)
                return processed
            return []
        except subprocess.SubprocessError as e:
            print(f"DEBUG: Find_links SubprocessError: {e}", file=sys.stderr)
            return []
    
    def _process_link_matches(
        self,
        matches: List[Dict[str, Any]],
        url_pattern: Optional[str] = None,
        title_pattern: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Process link matches and apply additional filtering."""
        processed = []
        
        for match in matches:
            text = match.get('text', '') or ''
            
            # Extract different types of links
            wiki_links = re.findall(self.PATTERNS['wiki_links'], text)
            markdown_links = re.findall(self.PATTERNS['markdown_links'], text)
            external_urls = re.findall(self.PATTERNS['external_urls'], text)
            
            # Process each type
            for link in wiki_links:
                if self._matches_filters(link, link, url_pattern, title_pattern):
                    processed.append({
                        'file': match['file'],
                        'line_number': match['line_number'],
                        'link_type': 'wiki_link',
                        'title': link,
                        'url': link,
                        'context': (text or '').strip()
                    })
            
            for title, url in markdown_links:
                if self._matches_filters(url, title, url_pattern, title_pattern):
                    processed.append({
                        'file': match['file'],
                        'line_number': match['line_number'],
                        'link_type': 'markdown_link',
                        'title': title,
                        'url': url,
                        'context': (text or '').strip()
                    })
            
            for url in external_urls:
                if self._matches_filters(url, url, url_pattern, title_pattern):
                    processed.append({
                        'file': match['file'],
                        'line_number': match['line_number'],
                        'link_type': 'external_url',
                        'title': url,
                        'url': url,
                        'context': (text or '').strip()
                    })
        
        return processed
    
    def _matches_filters(
        self,
        url: str,
        title: str,
        url_pattern: Optional[str],
        title_pattern: Optional[str]
    ) -> bool:
        """Check if link matches the provided filters."""
        if url_pattern and not re.search(url_pattern, url, re.IGNORECASE):
            return False
        if title_pattern and not re.search(title_pattern, title, re.IGNORECASE):
            return False
        return True
    
    def _make_json_serializable(self, obj: Any) -> Any:
        """Convert objects to JSON-serializable format."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {key: self._make_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._make_json_serializable(item) for item in obj]
        else:
            return obj
    
    def get_file_frontmatter(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Extract frontmatter from a specific file."""
        full_path = self.vault_path / file_path
        
        if not full_path.exists():
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Match frontmatter block
            match = re.match(self.PATTERNS['frontmatter_block'], content, re.DOTALL)
            if match:
                frontmatter_text = match.group(1)
                frontmatter_data = yaml.safe_load(frontmatter_text)
                return self._make_json_serializable(frontmatter_data)
            
        except (IOError, yaml.YAMLError):
            pass
        
        return None
    
    def get_files_by_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        folder: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get files modified within a date range."""
        search_path = self.vault_path
        if folder:
            search_path = self.vault_path / folder
        
        files = []
        for file_path in search_path.rglob('*.md'):
            if file_path.name.startswith('.'):
                continue
            
            try:
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                mdate = mtime.date()
                
                # Check date range
                if start_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                    if mdate < start:
                        continue
                
                if end_date:
                    end = datetime.strptime(end_date, '%Y-%m-%d').date()
                    if mdate > end:
                        continue
                
                files.append({
                    'file': str(file_path.relative_to(self.vault_path)),
                    'modified_date': mdate.isoformat(),
                    'modified_time': mtime.isoformat()
                })
                
            except (OSError, ValueError):
                continue
        
        # Sort by modification date (newest first)
        files.sort(key=lambda x: x['modified_date'], reverse=True)
        return files