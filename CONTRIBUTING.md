# Contributing to Obsidian Vault Search for Claude

Thank you for your interest in contributing! This project makes Claude more powerful for Obsidian users.

## Getting Started

### Prerequisites
- Python 3.8 or higher
- [ripgrep](https://github.com/BurntSushi/ripgrep) installed
- An Obsidian vault for testing

### Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kpetrovsky/kp-ripgrep-mcp.git
   cd kp-ripgrep-mcp
   ```

2. **Install in development mode:**
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up your test vault:**
   ```bash
   export OBSIDIAN_VAULT_PATH="/path/to/your/test/vault"
   ```

## Development Workflow

### Code Style
We use `black` and `isort` for consistent formatting:

```bash
# Format code
black src/ tests/ --line-length 100
isort src/ tests/ --profile black --line-length 100
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run specific test
python3 tests/test_smart_context.py

# Run with verbose output
pytest tests/ -v
```

### Testing with Claude Desktop
1. Update your `claude_desktop_config.json` to point to your development version
2. Restart Claude Desktop
3. Test the new functionality

## What to Contribute

### High-Impact Areas
- **Search Performance**: Optimizations for large vaults
- **New Search Types**: Additional ways to explore knowledge graphs
- **Error Handling**: Better error messages and recovery
- **Documentation**: Examples, guides, and use cases

### Feature Ideas
- **Semantic Search**: Integration with embedding models
- **Graph Analysis**: Find clusters, orphaned sections, centrality
- **Template Recognition**: Identify and search note templates
- **Metadata Extraction**: Enhanced frontmatter analysis

## Contribution Guidelines

### Bug Reports
Include:
- Your Obsidian vault structure (anonymized)
- The search query that failed
- Expected vs actual results
- Error messages if any

### Feature Requests
Include:
- **Use Case**: What Obsidian workflow would this improve?
- **Examples**: Show how Claude would use this feature
- **Context**: How does this relate to PKM best practices?

### Pull Requests
1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-search`
3. **Add tests** for your changes
4. **Update documentation** if needed
5. **Submit pull request** with clear description

### Code Standards
- **Clear function names**: Describe what the search does
- **Comprehensive docstrings**: Include examples and parameter descriptions
- **Error handling**: Graceful failures with helpful messages
- **Performance conscious**: Consider impact on large vaults

## Project Structure

```
src/rgrep_mcp/
├── __init__.py
├── config.py          # Configuration management
├── ripgrep.py         # Core ripgrep wrapper with smart context
└── server.py          # MCP server tools and API

tests/
├── test_smart_context.py      # Smart context functionality
├── test_recent_notes_fixes.py # Date validation and limits
└── test_*.py                  # Other test suites

test_vault/           # Test data for development
```

## Smart Context System

The smart context feature is our key differentiator. When extending it:

- **Frontmatter**: Should return property names, not values
- **Content**: Should return the most relevant heading
- **Performance**: Context detection adds file I/O - optimize carefully
- **Accuracy**: False context is worse than no context

## Release Process

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** with new features
3. **Run full test suite**
4. **Test with real Obsidian vaults**
5. **Create GitHub release** with release notes

## Questions?

- **GitHub Issues**: For bugs, features, and discussions
- **Discussions**: For general questions about usage
- **Code Review**: All contributions get reviewed for quality and correctness

## Recognition

Contributors will be:
- Listed in release notes
- Credited in documentation
- Invited to help shape the project roadmap

Thank you for helping make Obsidian + Claude more powerful! 🚀