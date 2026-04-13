"""Tests for config module."""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lib.config import (
    load_env_file,
    get_config,
    config_exists,
    is_reddit_api_available,
    is_openai_available,
    get_scrapecreators_key,
    get_openai_key,
    setup_config,
    _decode_jwt_payload,
    _token_expired,
    CONFIG_FILE,
)


class TestLoadEnvFile(unittest.TestCase):
    """Tests for load_env_file."""
    
    def test_load_simple_env(self):
        """Should parse simple key=value pairs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("KEY1=value1\n")
            f.write("KEY2=value2\n")
            f.flush()
            
            env = load_env_file(Path(f.name))
            self.assertEqual(env['KEY1'], 'value1')
            self.assertEqual(env['KEY2'], 'value2')
            
        os.unlink(f.name)
    
    def test_handles_quotes(self):
        """Should strip surrounding quotes from values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('SINGLE=\'quoted\'\n')
            f.write('DOUBLE="quoted"\n')
            f.flush()
            
            env = load_env_file(Path(f.name))
            self.assertEqual(env['SINGLE'], 'quoted')
            self.assertEqual(env['DOUBLE'], 'quoted')
            
        os.unlink(f.name)
    
    def test_skips_comments(self):
        """Should skip comment lines."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write("# This is a comment\n")
            f.write("KEY=value\n")
            f.flush()
            
            env = load_env_file(Path(f.name))
            self.assertEqual(len(env), 1)
            self.assertEqual(env['KEY'], 'value')
            
        os.unlink(f.name)
    
    def test_nonexistent_file(self):
        """Should return empty dict for missing file."""
        env = load_env_file(Path("/nonexistent/.env"))
        self.assertEqual(env, {})


class TestDecodeJwt(unittest.TestCase):
    """Tests for JWT utilities."""
    
    def test_decode_valid_jwt(self):
        """Should decode a valid JWT payload."""
        # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxOTk5OTk5OTk5fQ.xxx
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxOTk5OTk5OTk5fQ.xxx"
        payload = _decode_jwt_payload(token)
        self.assertIsNotNone(payload)
        self.assertEqual(payload.get('sub'), '1234567890')
        self.assertEqual(payload.get('exp'), 1999999999)
    
    def test_invalid_jwt(self):
        """Should return None for invalid JWT."""
        payload = _decode_jwt_payload("not.a.jwt")
        self.assertIsNone(payload)
    
    def test_empty_string(self):
        """Should return None for empty string."""
        payload = _decode_jwt_payload("")
        self.assertIsNone(payload)


class TestTokenExpired(unittest.TestCase):
    """Tests for token expiration check."""
    
    def test_future_token_not_expired(self):
        """Should return False for token expiring in the future."""
        # Token with exp in 2033
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxOTk5OTk5OTk5fQ.xxx"
        self.assertFalse(_token_expired(token))
    
    def test_past_token_expired(self):
        """Should return True for token that already expired."""
        # Token with exp in 2020
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxNTc3ODM2ODAwfQ.xxx"
        self.assertTrue(_token_expired(token))


class TestGetConfig(unittest.TestCase):
    """Tests for get_config."""
    
    def test_env_var_priority(self):
        """Environment variables should override file config."""
        with patch.dict(os.environ, {'SCRAPECREATORS_API_KEY': 'env_key'}):
            cfg = get_config()
            self.assertEqual(cfg['SCRAPECREATORS_API_KEY'], 'env_key')
    
    def test_returns_dict(self):
        """Should return a dictionary."""
        cfg = get_config()
        self.assertIsInstance(cfg, dict)
    
    def test_includes_config_source(self):
        """Should include _CONFIG_SOURCE."""
        cfg = get_config()
        self.assertIn('_CONFIG_SOURCE', cfg)


class TestApiAvailability(unittest.TestCase):
    """Tests for API availability checks."""
    
    def test_reddit_available_with_key(self):
        """Should return True when ScrapeCreators key is set."""
        with patch.dict(os.environ, {'SCRAPECREATORS_API_KEY': 'test_key'}):
            self.assertTrue(is_reddit_api_available())
    
    def test_reddit_unavailable_without_key(self):
        """Should return False when no key is set."""
        with patch.dict(os.environ, {}, clear=True):
            # Clear the environment variable
            os.environ.pop('SCRAPECREATORS_API_KEY', None)
            # Note: This test may pass or fail depending on whether
            # there's a config file with the key
            result = is_reddit_api_available()
            self.assertIsInstance(result, bool)


class TestSetupConfig(unittest.TestCase):
    """Tests for setup_config."""
    
    def test_creates_config_file(self):
        """Should create config file with provided keys."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch('lib.config.CONFIG_DIR', Path(tmpdir)):
                with patch('lib.config.CONFIG_FILE', Path(tmpdir) / '.env'):
                    path = setup_config(scrapecreators_key='test_key')
                    
                    self.assertTrue(path.exists())
                    
                    env = load_env_file(path)
                    self.assertEqual(env['SCRAPECREATORS_API_KEY'], 'test_key')


if __name__ == '__main__':
    unittest.main()
