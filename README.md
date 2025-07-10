# Obsidian Vault Search for Claude

This MCP server enables Claude to search file content using ripgrep - with extra features for Obsidian. It understands Obsidian-specific elements like wiki links, frontmatter properties, and provides intelligent context about where matches are found.

## Available Tools

### `rg_search_notes`
Search for text content within your notes with flexible scope options.
- Search all content, only frontmatter, or only note content
- Get smart context showing which frontmatter property or heading contains each match
- Filter by folder and control result limits

### `rg_search_links` 
Find and analyze links throughout your vault.
- Discover wiki links (`[[Note Title]]`), markdown links, and external URLs
- Filter links by URL patterns or title patterns
- Useful for finding broken links or analyzing your knowledge graph connections

### `rg_search_backlinks`
Find all notes that link to a specific target note.
- Identify which notes reference a particular topic or note
- Understand the context around each backlink reference
- Discover how ideas connect across your vault

### `rg_search_recent_notes`
Find notes modified within specific date ranges.
- Search by modification date using YYYY-MM-DD format
- Useful for reviewing recent work or finding notes from specific time periods
- Combine with other searches to find recent notes about specific topics

### `rg_search_orphaned_notes`
Identify notes that have no incoming or outgoing links.
- Find isolated notes that might need better integration
- Discover forgotten content that could be connected to your knowledge graph
- Useful for vault maintenance and organization

## Obsidian-Specific Capabilities

### Smart Context Detection
When matches are found, Claude receives intelligent context:
- **Frontmatter matches**: Shows the property name (e.g., `tags`, `project`, `status`)
- **Content matches**: Shows the nearest heading (e.g., `## Project Ideas`, `### Meeting Notes`)
- **Nested properties**: Handles complex YAML structures in frontmatter

### Link Understanding
- **Wiki Links**: `[[Note Title]]` and `[[Note Title|Display Text]]`
- **Markdown Links**: `[Display Text](note-file.md)` and external URLs
- **Frontmatter Links**: Links within YAML properties and lists

### File Organization
- **Folder Filtering**: Limit searches to specific directories
- **Date-Based Discovery**: Find files by modification time
- **Vault Structure**: Understands Obsidian's file organization patterns

## Additional Parameters

Most search tools support these common parameters:

### Search Behavior
- **`case_sensitive`**: `true` or `false` (default: false)
- **`folder`**: Limit search to specific folder (e.g., "Daily Notes", "Projects/Active")
- **`max_results`**: Number of results to return (1-100, default: 15, automatically capped)
- **`smart_context`**: Include context detection (default: true, set to false for faster searches)

### Search Scope (for `rg_search_notes`)
- **`search_scope`**: 
  - `"all"` - Search everything (default)
  - `"content_only"` - Skip frontmatter, search only note content
  - `"frontmatter_only"` - Search only YAML frontmatter properties

### Date Filtering (for `rg_search_recent_notes`)
- **`start_date`**: Start date in YYYY-MM-DD format (e.g., "2024-01-15")
- **`end_date`**: End date in YYYY-MM-DD format (e.g., "2024-01-31")

### Link Filtering (for `rg_search_links`)
- **`link_type`**: `"all"`, `"wiki_links"`, `"markdown_links"`, or `"external_urls"`
- **`url_pattern`**: Regex pattern to filter URLs
- **`title_pattern`**: Regex pattern to filter link titles

## Installation

### Prerequisites
- Python 3.8 or higher
- [ripgrep](https://github.com/BurntSushi/ripgrep) installed and available in PATH
- An Obsidian vault

### Install ripgrep

**Windows:**
```powershell
# Using winget (recommended)
winget install BurntSushi.ripgrep.MSVC

# Using chocolatey
choco install ripgrep

# Using scoop
scoop install ripgrep
```

**macOS:**
```bash
brew install ripgrep
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install ripgrep
```

### Install the MCP Server
```bash
# Clone the repository
git clone https://github.com/kpetrovsky/kp-ripgrep-mcp.git
cd kp-ripgrep-mcp

# Install the package
pip install -e .
```

### Configure Claude Desktop

Add this configuration to Claude Desktop:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "obsidian-search": {
      "command": "python",
      "args": ["-m", "rgrep_mcp.server"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/your/obsidian/vault"
      }
    }
  }
}
```

Replace `/path/to/your/obsidian/vault` with your actual vault path.

### Alternative Configuration

**Environment Variable (all platforms):**
```bash
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"
```

**Configuration File:**
Create `~/.rgrep-mcp.json`:
```json
{
  "vault_path": "/path/to/your/obsidian/vault",
  "default_case_sensitive": false,
  "default_result_limit": 15
}
```

## Troubleshooting

### "ripgrep (rg) is not installed or not in PATH"
**Verify ripgrep installation:**
```bash
rg --version
```
If this command fails, reinstall ripgrep using the instructions above.

### "No vault path configured" or "Vault path does not exist"
- Ensure `OBSIDIAN_VAULT_PATH` environment variable is set correctly
- Verify the path points to your Obsidian vault directory (contains .md files)
- Use absolute paths, not relative paths
- On Windows, use forward slashes or escape backslashes in JSON: `"C:/Users/Name/Vault"` or `"C:\\Users\\Name\\Vault"`

### Claude isn't finding expected results
- **Verify search terms**: Check that the content actually exists in your notes
- **Check scope**: Try `"search_scope": "all"` first, then narrow down
- **Test with simple queries**: Start with basic text searches before using complex patterns
- **Check folder restrictions**: If using the `folder` parameter, ensure it contains the expected notes

### Performance issues with large vaults
- **Use folder filtering**: Limit searches to specific directories when possible
- **Reduce max_results**: Start with smaller limits (5-10) for faster responses
- **Disable smart_context**: Set `"smart_context": false` for faster searches when context isn't needed
- **Be specific**: More targeted search terms are faster than broad queries

### Date format errors
Use YYYY-MM-DD format for dates:
- ✅ "2024-01-15"
- ✅ "2024-12-31" 
- ❌ "01/15/2024"
- ❌ "Jan 15, 2024"

### Permission issues
- Ensure Claude Desktop has permission to access your vault directory
- On macOS, you may need to grant Full Disk Access to Claude Desktop in System Preferences

## Example Usage

Ask Claude:
- "Find all notes containing 'machine learning' in my Research folder"
- "Show me notes I modified last week"
- "What notes link to my 'Project Ideas' note?"
- "Find notes with 'productivity' in the tags property"
- "Search for 'meeting' only in note content, not frontmatter"

## License

MIT License - see LICENSE file for details.