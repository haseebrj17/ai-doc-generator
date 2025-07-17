"""
Test runner script for the documentation generator.
Run this script to execute all tests with coverage reporting.
"""

import sys
import subprocess
from pathlib import Path


def run_tests():
    """Run all tests with coverage reporting."""
    # Get the project root
    project_root = Path(__file__).parent.parent.parent

    # Test command with coverage
    test_command = [
        sys.executable, "-m", "pytest",
        "-v",  # Verbose output
        "--cov=scripts.documentation",  # Coverage for the documentation module
        "--cov-report=html",  # HTML coverage report
        "--cov-report=term-missing",  # Terminal report with missing lines
        "--cov-report=xml",  # XML report for CI/CD
        "--tb=short",  # Shorter traceback format
        "tests/documentation/",  # Test directory
    ]

    # Add color if terminal supports it
    if sys.stdout.isatty():
        test_command.append("--color=yes")

    print("Running documentation generator tests...")
    print(f"Command: {' '.join(test_command)}")
    print("-" * 60)

    # Run the tests
    result = subprocess.run(test_command, cwd=project_root)

    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("\n📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests())