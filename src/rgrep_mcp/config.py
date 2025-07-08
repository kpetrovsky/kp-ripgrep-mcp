"""Configuration management for rgrep-mcp server."""

import json
import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration for the rgrep-mcp server."""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration from file or environment."""
        self.vault_path: Optional[str] = None
        self.default_case_sensitive: bool = False
        self.default_result_limit: int = 15
        
        # Try to load from config file
        if config_path and Path(config_path).exists():
            self._load_from_file(config_path)
        else:
            # Try default config locations
            self._load_from_default_locations()
        
        # Override with environment variables if set
        self._load_from_env()
    
    def _load_from_file(self, config_path: str) -> None:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            self.vault_path = config_data.get('vault_path')
            self.default_case_sensitive = config_data.get('default_case_sensitive', False)
            self.default_result_limit = config_data.get('default_result_limit', 15)
        except (json.JSONDecodeError, FileNotFoundError):
            pass  # Use defaults
    
    def _load_from_default_locations(self) -> None:
        """Try to load config from default locations."""
        config_locations = [
            'rgrep-mcp-config.json',
            os.path.expanduser('~/.config/rgrep-mcp/config.json'),
            os.path.expanduser('~/.rgrep-mcp.json'),
        ]
        
        for location in config_locations:
            if Path(location).exists():
                self._load_from_file(location)
                break
    
    def _load_from_env(self) -> None:
        """Load configuration from environment variables."""
        if vault_path := os.getenv('OBSIDIAN_VAULT_PATH'):
            self.vault_path = vault_path
        
        if case_sensitive := os.getenv('RGREP_MCP_CASE_SENSITIVE'):
            self.default_case_sensitive = case_sensitive.lower() in ('true', '1', 'yes')
        
        if result_limit := os.getenv('RGREP_MCP_RESULT_LIMIT'):
            try:
                self.default_result_limit = int(result_limit)
            except ValueError:
                pass
    
    def validate(self) -> None:
        """Validate configuration and raise ValueError if invalid."""
        if not self.vault_path:
            raise ValueError(
                "No vault path configured. Set OBSIDIAN_VAULT_PATH environment variable "
                "or create a config file with 'vault_path' setting."
            )
        
        vault_path = Path(self.vault_path)
        if not vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")
        
        if not vault_path.is_dir():
            raise ValueError(f"Vault path is not a directory: {self.vault_path}")