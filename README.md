# rgrep-mcp

MCP server for efficient Obsidian vault search using ripgrep. This server enables Claude Desktop and other MCP clients to perform advanced searches through Obsidian vaults with high performance and Obsidian-specific intelligence.

## Features

- **Fast Content Search**: Leverages ripgrep for high-performance text search
- **Obsidian-Aware**: Understands wiki links, markdown links, frontmatter, and tags
- **Flexible Filtering**: Search by scope (all/content/frontmatter), folder, date range
- **Link Analysis**: Find and filter links with regex patterns
- **Relationship Discovery**: Find backlinks and orphaned notes
- **Frontmatter Intelligence**: Parse and query YAML frontmatter properties
- **Token-Efficient**: Returns structured, LLM-optimized results

## Prerequisites

- Python 3.8 or higher
- [ripgrep](https://github.com/BurntSushi/ripgrep) installed and available in PATH
- An Obsidian vault

### Installing ripgrep

**macOS:**
```bash
brew install ripgrep
```

**Ubuntu/Debian:**
```bash
sudo apt install ripgrep
```

**Windows:**
```bash
# Using chocolatey
choco install ripgrep

# Using scoop
scoop install ripgrep
```

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd rgrep-mcp
```

2. Install the package:
```bash
pip install -e .
```

## Configuration

Configure the server by setting your Obsidian vault path. Choose one of these methods:

### Method 1: Environment Variable (Recommended)
```bash
export OBSIDIAN_VAULT_PATH="/path/to/your/obsidian/vault"
```

### Method 2: Configuration File
Create a file at one of these locations:
- `rgrep-mcp-config.json` (in current directory)
- `~/.config/rgrep-mcp/config.json`
- `~/.rgrep-mcp.json`

```json
{
  "vault_path": "/path/to/your/obsidian/vault",
  "default_case_sensitive": false,
  "default_result_limit": 15
}
```

### Additional Environment Variables
- `RGREP_MCP_CASE_SENSITIVE`: Set to "true" to make searches case-sensitive by default
- `RGREP_MCP_RESULT_LIMIT`: Set default result limit (default: 15)

## Usage with Claude Desktop

Add the server to your Claude Desktop configuration:

### macOS
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rgrep-mcp": {
      "command": "python",
      "args": ["-m", "rgrep_mcp.server"],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/your/obsidian/vault"
      }
    }
  }
}
```

### Windows
Edit `%APPDATA%/Claude/claude_desktop_config.json` with the same structure.

## Available Tools

### 1. `rg_search_notes`
Search through notes with scope filtering.

**Parameters:**
- `query` (required): Search pattern (supports regex)
- `search_scope`: "all" | "content_only" | "frontmatter_only" (default: "all")
- `case_sensitive`: Boolean (default: false)
- `folder`: Optional folder to limit search
- `max_results`: Integer (default: 15)

**Example:**
```json
{
  "query": "machine learning",
  "search_scope": "content_only",
  "folder": "Research",
  "max_results": 10
}
```

### 2. `rg_search_frontmatter`
Query and analyze frontmatter properties.

**Parameters:**
- `action` (required): "list_properties" | "search_property_values" | "validate_property_types"
- `property_names`: Array of property names to search
- `property_value`: Value to search for in properties
- Common parameters: `case_sensitive`, `folder`, `max_results`

**Examples:**
```json
// List all properties
{
  "action": "list_properties"
}

// Search for specific tag
{
  "action": "search_property_values",
  "property_names": ["tags"],
  "property_value": "research"
}
```

### 3. `rg_search_links`
Extract and filter all links.

**Parameters:**
- `link_type`: "all" | "wiki_links" | "markdown_links" | "external_urls" (default: "all")
- `url_pattern`: Regex to filter URLs
- `title_pattern`: Regex to filter link titles
- Common parameters: `case_sensitive`, `folder`, `max_results`

**Example:**
```json
{
  "link_type": "external_urls",
  "url_pattern": "github\\.com"
}
```

### 4. `rg_search_backlinks`
Find all notes linking to a specific note.

**Parameters:**
- `target_note` (required): Note to find backlinks for
- Common parameters: `case_sensitive`, `folder`, `max_results`

**Example:**
```json
{
  "target_note": "Important Concepts.md"
}
```

### 5. `rg_search_orphaned_notes`
Identify notes with no incoming or outgoing links.

**Parameters:**
- Common parameters: `case_sensitive`, `folder`, `max_results`

### 6. `rg_search_recent_notes`
Find notes modified within a date range.

**Parameters:**
- `start_date`: Start date (YYYY-MM-DD format)
- `end_date`: End date (YYYY-MM-DD format)
- Common parameters: `folder`, `max_results`

**Example:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

## Troubleshooting

### "ripgrep (rg) is not installed or not in PATH"
Make sure ripgrep is installed and accessible from your command line:
```bash
rg --version
```

### "No vault path configured"
Set the `OBSIDIAN_VAULT_PATH` environment variable or create a configuration file.

### "Vault path does not exist"
Verify the path points to your actual Obsidian vault directory.

### Performance Issues
- Use the `folder` parameter to limit search scope
- Reduce `max_results` for large vaults
- Use more specific search patterns

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black src/
isort src/
```

## License

MIT License - see LICENSE file for details.