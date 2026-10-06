import importlib.util
import pathlib
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RefactorRegressionTests(unittest.TestCase):
    def test_ascii_clear_screen_uses_platform_safe_sequence(self):
        module = load_module("ascii_refactor", ROOT / "apps" / "python" / "ASCII V3.py")
        self.assertTrue(callable(module.clear_screen))
        self.assertEqual(module.clear_screen(), "\033[2J\033[H")

    def test_server_finds_html_in_the_applications_directory(self):
        module = load_module("frameforge_server", ROOT / "apps" / "server" / "frameforge_server.py")
        html = module.find_html(ROOT / "apps" / "html")
        self.assertTrue(html.is_file())
        self.assertIn("frameforge", html.name.lower())

    def test_script_installer_builds_platform_safe_command(self):
        module = load_module("script_installer", ROOT / "apps" / "tools" / "script installer.py")
        command = module.build_pip_command("requests")
        self.assertEqual(command, [sys.executable, "-m", "pip", "install", "requests"])


if __name__ == "__main__":
    unittest.main()
