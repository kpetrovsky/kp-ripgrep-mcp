"""MCP server for Obsidian vault search using ripgrep - FastMCP version."""

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

from .config import Config
from .ripgrep import RipgrepWrapper


# Initialize configuration and ripgrep wrapper globally
try:
    print("Loading configuration...", file=sys.stderr)
    config = Config()
    print(f"Vault path: {config.vault_path}", file=sys.stderr)
    
    print("Validating configuration...", file=sys.stderr)
    config.validate()
    
    print("Initializing ripgrep wrapper...", file=sys.stderr)
    rg = RipgrepWrapper(config.vault_path)
    print("Setup complete!", file=sys.stderr)
    print(f"Ripgrep command: {rg.rg_command}", file=sys.stderr)
    
    # Test basic functionality
    print("Testing basic search functionality...", file=sys.stderr)
    test_results = rg.search_content("test", max_results=1)
    print(f"Test search returned {len(test_results)} results", file=sys.stderr)
    
except Exception as e:
    print(f"CRITICAL ERROR during setup: {e}", file=sys.stderr)
    print("Configuration details:", file=sys.stderr)
    print(f"  OBSIDIAN_VAULT_PATH env var: {os.getenv('OBSIDIAN_VAULT_PATH')}", file=sys.stderr)
    print(f"  Current working directory: {os.getcwd()}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.exit(1)

# Create FastMCP server
mcp = FastMCP("rgrep-mcp")


@mcp.tool()
def rg_search_notes(
    query: str,
    search_scope: str = "all",
    case_sensitive: bool = False,
    folder: Optional[str] = None,
    max_results: int = 15,
    smart_context: bool = True
) -> str:
    """Search through notes with scope filtering.
    
    Args:
        query: Search pattern (supports regex)
        search_scope: Where to search - "all", "content_only", or "frontmatter_only"
        case_sensitive: Whether search should be case sensitive
        folder: Optional folder to limit search scope
        max_results: Maximum number of results to return (minimum: 1, maximum: 100, capped automatically)
        smart_context: Whether to include smart context (frontmatter property names, content headings)
    
    Returns:
        JSON string with search results
    """
    try:
        # Validate inputs
        if search_scope not in ["all", "content_only", "frontmatter_only"]:
            return json.dumps({"error": "Invalid search_scope. Use: all, content_only, or frontmatter_only"})
        
        if max_results < 1 or max_results > 100:
            max_results = min(max(max_results, 1), 100)
        
        # Perform search based on scope  
        # Use a higher per-file limit to get enough results, then limit globally
        per_file_limit = min(max_results * 2, 50)  # Get extra results but cap at reasonable limit
        
        if search_scope == "all":
            results = rg.search_content(query, case_sensitive, folder, per_file_limit, smart_context)
        elif search_scope == "content_only":
            results = rg.search_content_only(query, case_sensitive, folder, per_file_limit, smart_context)
        elif search_scope == "frontmatter_only":
            results = rg.search_frontmatter_only(query, case_sensitive, folder, per_file_limit, smart_context)
        
        # Format results for LLM consumption
        formatted_results = {
            "query": query,
            "search_scope": search_scope,
            "total_matches": len(results),
            "results": []
        }
        
        # Limit results to max_results (since ripgrep --max-count is per-file)
        limited_results = results[:max_results] if results else []
        
        for result in limited_results:
            formatted_result = {
                "file": result['file'],
                "line_number": result['line_number'],
                "snippet": (result.get('text', '') or '').strip()
            }
            
            # Add smart context if available
            if 'smart_context' in result:
                formatted_result['smart_context'] = result['smart_context']
            formatted_results["results"].append(formatted_result)
        
        # Update total_matches to reflect actual returned results
        formatted_results["total_matches"] = len(limited_results)
        
        return json.dumps(formatted_results, indent=2)
        
    except Exception as e:
        print(f"Error in rg_search_notes: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return json.dumps({
            "error": str(e),
            "query": query,
            "vault_path": str(rg.vault_path) if 'rg' in locals() else "unknown",
            "debug_info": "Check stderr logs for detailed error information"
        })


@mcp.tool()
def rg_search_links(
    link_type: str = "all",
    url_pattern: Optional[str] = None,
    title_pattern: Optional[str] = None,
    case_sensitive: bool = False,
    folder: Optional[str] = None,
    max_results: int = 15
) -> str:
    """Extract and filter all links (wiki, markdown, external).
    
    Args:
        link_type: Type of links - "all", "wiki_links", "markdown_links", or "external_urls"
        url_pattern: Optional regex to filter URLs
        title_pattern: Optional regex to filter link titles
        case_sensitive: Whether search should be case sensitive
        folder: Optional folder to limit search scope
        max_results: Maximum number of results to return (minimum: 1, maximum: 100, capped automatically)
    
    Returns:
        JSON string with link search results
    """
    try:
        # Validate inputs
        valid_link_types = ["all", "wiki_links", "markdown_links", "external_urls"]
        if link_type not in valid_link_types:
            return json.dumps({"error": f"Invalid link_type. Use: {', '.join(valid_link_types)}"})
        
        if max_results < 1 or max_results > 100:
            max_results = min(max(max_results, 1), 100)
        
        # Use a higher per-file limit to get enough results, then limit globally
        per_file_limit = min(max_results * 2, 50)  # Get extra results but cap at reasonable limit
        
        results = rg.find_links(
            link_type=link_type,
            url_pattern=url_pattern,
            title_pattern=title_pattern,
            case_sensitive=case_sensitive,
            folder=folder,
            max_results=per_file_limit
        )
        
        # Limit results to max_results (since ripgrep --max-count is per-file)
        limited_results = results[:max_results] if results else []
        
        formatted_result = {
            "link_type": link_type,
            "filters": {
                "url_pattern": url_pattern,
                "title_pattern": title_pattern
            },
            "total_matches": len(limited_results),
            "results": limited_results
        }
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        print(f"Error in rg_search_links: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})


@mcp.tool()
def rg_search_backlinks(
    target_note: str,
    case_sensitive: bool = False,
    folder: Optional[str] = None,
    max_results: int = 15,
    smart_context: bool = True
) -> str:
    """Find all notes linking to a specific note.
    
    Args:
        target_note: Note to find backlinks for (relative to vault root)
        case_sensitive: Whether search should be case sensitive
        folder: Optional folder to limit search scope
        max_results: Maximum number of results to return (minimum: 1, maximum: 100, capped automatically)
        smart_context: Whether to include smart context (frontmatter property names, content headings)
    
    Returns:
        JSON string with backlink results
    """
    try:
        if max_results < 1 or max_results > 100:
            max_results = min(max(max_results, 1), 100)
        
        # Create patterns for both wiki links and markdown links
        note_name = target_note.replace('.md', '')
        wiki_pattern = rf'\[\[.*{re.escape(note_name)}.*\]\]'
        markdown_pattern = rf'\[.*\]\(.*{re.escape(target_note)}.*\)'
        combined_pattern = f'({wiki_pattern})|({markdown_pattern})'
        
        results = rg.search_content(
            query=combined_pattern,
            case_sensitive=case_sensitive,
            folder=folder,
            max_results=max_results * 2,  # Get more results to filter out self-references
            smart_context=smart_context
        )
        
        formatted_result = {
            "target_note": target_note,
            "total_backlinks": 0,
            "backlinks": []
        }
        
        backlinks_count = 0
        for result in results:
            if result['file'] != target_note and backlinks_count < max_results:  # Don't include self-references
                backlink_result = {
                    "file": result['file'],
                    "line_number": result['line_number'],
                    "context": (result.get('text', '') or '').strip()
                }
                
                # Add smart context if available
                if 'smart_context' in result:
                    backlink_result['smart_context'] = result['smart_context']
                
                formatted_result["backlinks"].append(backlink_result)
                backlinks_count += 1
        
        formatted_result["total_backlinks"] = len(formatted_result["backlinks"])
        
        return json.dumps(formatted_result, indent=2)
        
    except Exception as e:
        print(f"Error in rg_search_backlinks: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})


@mcp.tool()
def rg_search_recent_notes(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    folder: Optional[str] = None,
    max_results: int = 15
) -> str:
    """Find notes modified within date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (e.g., "2024-01-15")
        end_date: End date in YYYY-MM-DD format (e.g., "2024-01-31")
        folder: Optional folder to limit search scope
        max_results: Maximum number of results to return (minimum: 1, maximum: 100, capped automatically)
    
    Returns:
        JSON string with recent notes results
    """
    try:
        if max_results < 1 or max_results > 100:
            max_results = min(max(max_results, 1), 100)
        
        # Validate date formats if provided
        if start_date is not None:
            try:
                from datetime import datetime
                datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return json.dumps({
                    "error": f"Invalid start_date format: '{start_date}'. Expected YYYY-MM-DD format (e.g., '2024-01-15')"
                })
        
        if end_date is not None:
            try:
                from datetime import datetime
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return json.dumps({
                    "error": f"Invalid end_date format: '{end_date}'. Expected YYYY-MM-DD format (e.g., '2024-01-31')"
                })
        
        files = rg.get_files_by_date_range(
            start_date=start_date,
            end_date=end_date,
            folder=folder
        )
        
        # Limit results
        limited_files = files[:max_results]
        
        result = {
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_files": len(limited_files),
            "files": limited_files
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        print(f"Error in rg_search_recent_notes: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})


@mcp.tool()
def rg_search_orphaned_notes(
    case_sensitive: bool = False,
    folder: Optional[str] = None,
    max_results: int = 15
) -> str:
    """Identify notes with no incoming or outgoing links.
    
    Args:
        case_sensitive: Whether search should be case sensitive
        folder: Optional folder to limit search scope
        max_results: Maximum number of results to return (minimum: 1, maximum: 100, capped automatically)
    
    Returns:
        JSON string with orphaned notes results
    """
    try:
        if max_results < 1 or max_results > 100:
            max_results = min(max(max_results, 1), 100)
        
        # Get all markdown files
        files = rg.get_files_by_date_range(folder=folder)
        orphaned = []
        
        for file_info in files:
            file_path = file_info['file']
            note_name = file_path.replace('.md', '')
            
            # Check if file has outgoing links
            outgoing_links = rg.find_links(folder=folder, max_results=1000)
            has_outgoing = any(link['file'] == file_path for link in outgoing_links)
            
            # Check if file has incoming links (backlinks)
            wiki_pattern = rf'\[\[.*{re.escape(note_name)}.*\]\]'
            markdown_pattern = rf'\[.*\]\(.*{re.escape(file_path)}.*\)'
            combined_pattern = f'({wiki_pattern})|({markdown_pattern})'
            
            backlinks = rg.search_content(query=combined_pattern, max_results=1)
            has_incoming = len(backlinks) > 0 and backlinks[0]['file'] != file_path
            
            if not has_outgoing and not has_incoming:
                orphaned.append({
                    "file": file_path,
                    "modified_date": file_info['modified_date']
                })
                
                if len(orphaned) >= max_results:
                    break
        
        result = {
            "total_orphaned": len(orphaned),
            "orphaned_notes": orphaned
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        print(f"Error in rg_search_orphaned_notes: {e}", file=sys.stderr)
        return json.dumps({"error": str(e)})


def main():
    """Entry point for the FastMCP server."""
    print("Starting rgrep-mcp FastMCP server...", file=sys.stderr)
    mcp.run()


if __name__ == "__main__":
    main()