# Changelog

All notable changes to the Obsidian Vault Search for Claude project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-10

### Added - Smart Context (Major Feature)
- **Smart Context Detection**: Claude now receives intelligent context about where matches are found
  - **Frontmatter Properties**: Shows property names (e.g., "tags", "mentioned_projects", "assigned_to") 
  - **Content Headings**: Shows the nearest heading (e.g., "## Project Ideas", "### Team Members")
  - **Nested YAML Support**: Handles complex frontmatter structures and returns immediate property names
- **smart_context Parameter**: Available on all search functions (default: true)
  - Set to `false` to disable context detection for faster searches
  - Provides property names for frontmatter matches and headings for content matches

### Added - Search Improvements  
- **Newest-First Sorting**: All search results now return most recently modified files first
- **Enhanced Date Validation**: Clear error messages for invalid date formats with examples
- **Comprehensive Parameter Documentation**: All functions now clearly document parameter limits and behavior

### Added - Tools and Functionality
- **rg_search_notes**: Search with scope filtering (all/content_only/frontmatter_only)
- **rg_search_links**: Find and filter wiki links, markdown links, and external URLs
- **rg_search_backlinks**: Discover notes linking to a specific target note  
- **rg_search_recent_notes**: Find notes modified within date ranges with validation
- **rg_search_orphaned_notes**: Identify notes with no incoming or outgoing links

### Fixed - Robustness and Reliability
- **Unicode Support**: Fixed encoding issues that caused 0 results with special characters
- **Max Results Handling**: Proper global limiting (ripgrep's --max-count is per-file)
- **Error Handling**: Comprehensive validation with user-friendly error messages
- **Search Scope Accuracy**: Fixed frontmatter_only and content_only searches that were returning 0 results

### Technical Improvements
- **PCRE2 Support**: Advanced regex patterns now work correctly in search scopes
- **Intelligent Filtering**: Replaced complex regex with simple search + post-filtering for reliability
- **Path Compatibility**: WSL path conversion for Windows ripgrep executable

### Documentation
- **User-Focused README**: Completely rewritten for Obsidian users rather than developers
- **Quick Start Guide**: Simple setup instructions with real examples
- **Smart Context Examples**: Clear demonstrations of the context-aware search feature
- **Comprehensive Troubleshooting**: Common issues and solutions

### Development
- **Comprehensive Test Suite**: Full test coverage for smart context, date validation, and max results
- **Code Organization**: Tests moved to dedicated directory, debug code removed
- **Production Ready**: Clean error handling and minimal logging for production use

## [0.1.0] - Initial Development

### Added - Foundation
- Basic ripgrep integration for Obsidian vault search
- MCP server implementation with FastMCP
- Configuration system with environment variables and config files
- Core search functionality for note content

---

## Migration Notes

### From 0.x to 1.0
- **Smart Context**: New feature enabled by default - no breaking changes
- **Result Ordering**: Results now sorted newest-first (may change result order)
- **Error Messages**: Improved error messages for invalid dates (better user experience)
- **File Organization**: Tests moved to `tests/` directory (development only)

### For Users
- **No Action Required**: Existing configurations continue to work
- **New Features Available**: Smart context works automatically with existing queries
- **Better Performance**: More reliable search with improved error handling