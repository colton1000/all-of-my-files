import subprocess
import sys

PACKAGES = [
    "requests",
    "numpy",
    "pillow",
    "flask",
    "rich",
    "pytest",
    "pandas",
    "scipy",
    "colorama",
    "pyYAML",
    "streamlit",
    "psutil",
    "setuptools",
    "pygame",
]


def build_pip_command(package: str) -> list[str]:
    """Build a shell-independent pip command."""
    return [sys.executable, "-m", "pip", "install", package]


def install_packages(package_list: list[str]) -> None:
    """Install each requested package and stop on the first failure."""
    for package in package_list:
        print(f"\nInstalling {package}...")
        result = subprocess.run(build_pip_command(package), check=False)
        if result.returncode != 0:
            raise SystemExit(f"Installation failed for {package}")


if __name__ == "__main__":
    install_packages(PACKAGES)
    print("\nAll installations complete!")

