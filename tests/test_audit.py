import unittest
import os
import ast
import re

class TestCodeAudit(unittest.TestCase):
    ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    def get_all_py_files(self):
        py_files = []
        for root, dirs, files in os.walk(self.ROOT_DIR):
            if 'env' in root or 'venv' in root or '.git' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    py_files.append(os.path.join(root, file))
        return py_files

    def test_mandatory_files_exist(self):
        mandatory_files = [
            'config.py',
            'utils.py',
            'Saham.py',
            'pages_analysis.py',
            'pages_ara_arb.py',
            'pages_calculators.py',
            'pages_compound.py',
            'pages_scraper.py',
            'pages_screener.py',
            'pages_trade_planner.py',
            'pages_warrant.py',
            'pwa_setup.py',
            'tests/test_financial_logic.py',
            'requirements.txt',
            'README.md'
        ]
        results = []
        for f in mandatory_files:
            path = os.path.join(self.ROOT_DIR, f)
            exists = os.path.exists(path)
            if not exists:
                results.append(f)
        
        self.assertEqual(len(results), 0, f"Missing mandatory files: {results}")

    def test_legacy_files_removed(self):
        legacy_files = ['Saham.old.py']
        for f in legacy_files:
            path = os.path.join(self.ROOT_DIR, f)
            self.assertFalse(os.path.exists(path), f"Legacy file {f} MUST be removed.")

    def test_no_hardcoded_secrets(self):
        # Allow-list for known non-secret keys if necessary
        # Regex to find assignments to variables looks like SECRET or KEY with string value
        secret_pattern = re.compile(r'(API_KEY|SECRET|PASSWORD|TOKEN)\s*=\s*[\'"][^\'"]+[\'"]')
        
        py_files = self.get_all_py_files()
        found_secrets = []
        
        for file_path in py_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Check for pattern
                if secret_pattern.search(content):
                    # verify it's not 'os.getenv' or similar
                    found_secrets.append(file_path)
        
        self.assertEqual(len(found_secrets), 0, f"Potential hardcoded secrets found in: {found_secrets}")

    def test_syntax_validity(self):
        py_files = self.get_all_py_files()
        syntax_errors = []
        
        for file_path in py_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            try:
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append(f"{file_path}: {e}")
                
        self.assertEqual(len(syntax_errors), 0, f"Syntax errors found: {syntax_errors}")

    def test_no_dead_code_utils(self):
        # Specific check for logic removed from utils
        utils_path = os.path.join(self.ROOT_DIR, 'utils.py')
        if os.path.exists(utils_path):
            with open(utils_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.assertNotIn("def calculate_next_price", content, "Dead code calculate_next_price still in utils.py")

if __name__ == '__main__':
    unittest.main()
