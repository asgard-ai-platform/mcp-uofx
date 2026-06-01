import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def test_package_imports():
    import mcp_uofx.server  # noqa: F401
    import mcp_uofx.sse_server  # noqa: F401
    import mcp_uofx.login  # noqa: F401


if __name__ == "__main__":
    test_package_imports()
    print("import checks passed")
