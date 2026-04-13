"""Configuration management for Design Research.

Loads API keys and settings from multiple sources:
1. Environment variables (highest priority)
2. Per-project config (.claude/design-research.env)
3. Global config (~/.config/design-research/.env)

Supports Codex auth as fallback for OpenAI API access.
"""

import base64
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Literal

# Config locations
CONFIG_DIR = Path.home() / ".config" / "design-research"
CONFIG_FILE = CONFIG_DIR / ".env"
CODEX_AUTH_FILE = Path(os.environ.get("CODEX_AUTH_FILE", str(Path.home() / ".codex" / "auth.json")))

AuthSource = Literal["api_key", "codex", "none"]
AuthStatus = Literal["ok", "missing", "expired"]


@dataclass(frozen=True)
class OpenAIAuth:
    """OpenAI authentication state."""
    token: Optional[str]
    source: AuthSource
    status: AuthStatus


def _log(msg: str):
    """Log to stderr."""
    sys.stderr.write(f"[Design Research Config] {msg}\n")
    sys.stderr.flush()


def _check_file_permissions(path: Path) -> None:
    """Warn if a secrets file has overly permissive permissions."""
    try:
        mode = path.stat().st_mode
        if mode & 0o044:
            _log(f"WARNING: {path} is readable by other users. Run: chmod 600 {path}")
    except OSError:
        pass


def load_env_file(path: Path) -> Dict[str, str]:
    """Load environment variables from a .env file."""
    env = {}
    if not path or not path.exists():
        return env
    
    _check_file_permissions(path)
    
    with open(path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, _, value = line.partition('=')
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value and value[0] in ('"', "'") and value[-1] == value[0]:
                    value = value[1:-1]
                if key and value:
                    env[key] = value
    return env


def _decode_jwt_payload(token: str) -> Optional[Dict[str, Any]]:
    """Decode JWT payload without verification."""
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return None
        payload_b64 = parts[1]
        pad = "=" * (-len(payload_b64) % 4)
        decoded = base64.urlsafe_b64decode(payload_b64 + pad)
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return None


def _token_expired(token: str, leeway_seconds: int = 60) -> bool:
    """Check if JWT token is expired."""
    payload = _decode_jwt_payload(token)
    if not payload:
        return False
    exp = payload.get("exp")
    if not exp:
        return False
    return exp <= (time.time() + leeway_seconds)


def load_codex_auth() -> Dict[str, Any]:
    """Load Codex auth JSON."""
    if not CODEX_AUTH_FILE.exists():
        return {}
    try:
        with open(CODEX_AUTH_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def get_codex_access_token() -> tuple[Optional[str], AuthStatus]:
    """Get Codex access token from auth.json."""
    auth = load_codex_auth()
    token = None
    
    if isinstance(auth, dict):
        tokens = auth.get("tokens") or {}
        if isinstance(tokens, dict):
            token = tokens.get("access_token")
        if not token:
            token = auth.get("access_token")
    
    if not token:
        return None, "missing"
    if _token_expired(token):
        return None, "expired"
    return token, "ok"


def get_openai_auth(file_env: Dict[str, str]) -> OpenAIAuth:
    """Resolve OpenAI auth from API key or Codex login."""
    # Check for API key first
    api_key = os.environ.get('OPENAI_API_KEY') or file_env.get('OPENAI_API_KEY')
    if api_key:
        return OpenAIAuth(token=api_key, source="api_key", status="ok")
    
    # Fall back to Codex auth
    codex_token, codex_status = get_codex_access_token()
    if codex_token and codex_status == "ok":
        return OpenAIAuth(token=codex_token, source="codex", status="ok")
    
    return OpenAIAuth(token=None, source="none", status=codex_status)


def _find_project_env() -> Optional[Path]:
    """Find per-project .env by walking up from cwd."""
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        candidate = parent / '.claude' / 'design-research.env'
        if candidate.exists():
            return candidate
        if parent == Path.home() or parent == parent.parent:
            break
    return None


def get_config() -> Dict[str, Any]:
    """Load configuration from multiple sources.
    
    Priority (highest wins):
      1. Environment variables (os.environ)
      2. .claude/design-research.env (per-project config)
      3. ~/.config/design-research/.env (global config)
    """
    # Load from global config file
    file_env = load_env_file(CONFIG_FILE) if CONFIG_FILE.exists() else {}
    
    # Load from per-project config (overrides global)
    project_env_path = _find_project_env()
    project_env = load_env_file(project_env_path) if project_env_path else {}
    
    # Merge: project overrides global
    merged_env = {**file_env, **project_env}
    
    # Get OpenAI auth
    openai_auth = get_openai_auth(merged_env)
    
    # Build config
    config = {
        'OPENAI_API_KEY': openai_auth.token,
        'OPENAI_AUTH_SOURCE': openai_auth.source,
        'OPENAI_AUTH_STATUS': openai_auth.status,
    }
    
    # Additional keys we support
    keys = [
        ('SCRAPECREATORS_API_KEY', None),
    ]
    
    for key, default in keys:
        config[key] = os.environ.get(key) or merged_env.get(key, default)
    
    # Track config source
    if project_env_path:
        config['_CONFIG_SOURCE'] = f'project:{project_env_path}'
    elif CONFIG_FILE.exists():
        config['_CONFIG_SOURCE'] = f'global:{CONFIG_FILE}'
    else:
        config['_CONFIG_SOURCE'] = 'env_only'
    
    return config


def config_exists() -> bool:
    """Check if any configuration source exists."""
    if _find_project_env():
        return True
    return CONFIG_FILE.exists()


def is_reddit_api_available() -> bool:
    """Check if Reddit API (ScrapeCreators) is available."""
    config = get_config()
    return bool(config.get('SCRAPECREATORS_API_KEY'))


def is_openai_available() -> bool:
    """Check if OpenAI API is available."""
    config = get_config()
    return config.get('OPENAI_AUTH_STATUS') == 'ok'


def get_scrapecreators_key() -> Optional[str]:
    """Get ScrapeCreators API key if available."""
    config = get_config()
    return config.get('SCRAPECREATORS_API_KEY')


def get_openai_key() -> Optional[str]:
    """Get OpenAI API key if available."""
    config = get_config()
    return config.get('OPENAI_API_KEY')


def setup_config(scrapecreators_key: Optional[str] = None, openai_key: Optional[str] = None) -> Path:
    """Create or update the global config file.
    
    Returns the path to the config file.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load existing config
    existing = load_env_file(CONFIG_FILE) if CONFIG_FILE.exists() else {}
    
    # Update with new values
    if scrapecreators_key:
        existing['SCRAPECREATORS_API_KEY'] = scrapecreators_key
    if openai_key:
        existing['OPENAI_API_KEY'] = openai_key
    
    # Write config
    with open(CONFIG_FILE, 'w') as f:
        f.write("# Design Research configuration\n")
        f.write("# Get a ScrapeCreators key at https://scrapecreators.com (100 free credits)\n\n")
        for key, value in existing.items():
            f.write(f"{key}={value}\n")
    
    # Set secure permissions
    os.chmod(CONFIG_FILE, 0o600)
    
    return CONFIG_FILE


def print_config_status():
    """Print current configuration status."""
    config = get_config()
    
    print(f"Config source: {config.get('_CONFIG_SOURCE', 'none')}")
    print()
    
    # ScrapeCreators
    sc_key = config.get('SCRAPECREATORS_API_KEY')
    if sc_key:
        print(f"ScrapeCreators: ✓ configured ({sc_key[:8]}...)")
        print("  → Reddit API search enabled")
    else:
        print("ScrapeCreators: ✗ not configured")
        print("  → Reddit will use WebSearch fallback")
    
    print()
    
    # OpenAI
    openai_source = config.get('OPENAI_AUTH_SOURCE')
    openai_status = config.get('OPENAI_AUTH_STATUS')
    
    if openai_status == 'ok':
        if openai_source == 'api_key':
            print(f"OpenAI: ✓ API key configured")
        elif openai_source == 'codex':
            print(f"OpenAI: ✓ using Codex auth")
    elif openai_status == 'expired':
        print("OpenAI: ✗ Codex token expired (run `codex login`)")
    else:
        print("OpenAI: ✗ not configured")
    
    print()
    print(f"Global config: {CONFIG_FILE}")
    print(f"Project config: .claude/design-research.env")
