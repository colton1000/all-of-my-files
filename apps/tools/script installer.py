import argparse
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


def install_packages(package_list: list[str], dry_run: bool = False, upgrade: bool = False) -> None:
    """Install each requested package and stop on the first failure."""
    for package in package_list:
        command = build_pip_command(package)
        if upgrade:
            command.insert(-1, "--upgrade")
        if dry_run:
            print(f"Would run: {' '.join(command)}")
            continue
        print(f"\nInstalling {package}...")
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            raise SystemExit(f"Installation failed for {package}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install common Python packages with the active interpreter.")
    parser.add_argument("--list", action="store_true", help="list available package names and exit")
    parser.add_argument("--only", nargs="+", choices=PACKAGES, help="install only the selected package(s)")
    parser.add_argument("--dry-run", action="store_true", help="show pip commands without installing")
    parser.add_argument("--upgrade", action="store_true", help="upgrade selected packages if already installed")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.list:
        print("Available packages:")
        print("\n".join(f"  {package}" for package in PACKAGES))
        raise SystemExit(0)
    selected_packages = args.only or PACKAGES
    install_packages(selected_packages, dry_run=args.dry_run, upgrade=args.upgrade)
    print("\nDry run complete." if args.dry_run else "\nAll installations complete!")
