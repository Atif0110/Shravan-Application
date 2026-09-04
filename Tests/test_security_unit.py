import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Backend"))

from security import is_safe_external_url


def test_rejects_local_urls():
    assert not is_safe_external_url("http://127.0.0.1:5000")
    assert not is_safe_external_url("http://localhost/admin")
    assert not is_safe_external_url("http://10.0.0.1")


def test_accepts_public_http_urls():
    assert is_safe_external_url("https://example.com/health")


def test_rejects_non_http_schemes():
    assert not is_safe_external_url("file:///etc/passwd")
    assert not is_safe_external_url("javascript:alert(1)")
