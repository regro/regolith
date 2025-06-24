"""Unit tests for __version__.py."""

import regolith  # noqa


def test_package_version():
    """Ensure the package version is defined and not set to the initial
    placeholder."""
    assert hasattr(regolith, "__version__")
    assert regolith.__version__ != "0.0.0"
