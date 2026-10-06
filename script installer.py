import subprocess
import time

# List of packages you want to install
packages = [
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
    "Streamlit",
    "psutil",
    "GPUtil",
    "setuptools",
    "pygame"
]

def install_packages(package_list):
    for pkg in package_list:
        print(f"\nInstalling {pkg}...")
        
        # Open cmd and run pip install
        subprocess.run(
            f'cmd /c "pip install {pkg}"',
            shell=True
        )
        
        time.sleep(1)  # small delay between installs

if __name__ == "__main__":
    install_packages(packages)

    print("\nAll installations complete!")



