import unittest
import ast
import os
from typing import Union
import sys

if __name__ in ("__main__", "test_visast"):
    # Hack to allow us to import visast from the parent dir if this script is invoked directly.
    # Or, invoked by python -m unittest from within the tests/ folder
    p = os.path.dirname(os.path.abspath(__file__)) + '/..'
    sys.path.insert(1, p)

from visast import generate, visualise

class TestVisAST(unittest.TestCase):
    aSTURL = "https://gist.githubusercontent.com/JamesPhillipsUK/f3498b07d94a5a4e4ea4d3060c0af907/raw/a8eca1ef2d096bb652b3a1009d3bcb0f09f31af5/helloworld.py"
    aSTScript = '''
""" helloworld.py

A simple Hello World python script.

Authors: Jesse Phillips <james@jamesphillipsuk.com>

"""


def main():
    """ main.  Our entrypoint for the script.

    """
    print("\\nHello, World!\\n")


if __name__ == "__main__":
    main()
'''

    def testGenerateFromURLOne(self) -> None:
        remoteAST = generate.fromURL(self.aSTURL)
        self.assertIsInstance(remoteAST, ast.AST, "generate.fromURL should generate an AST")

    def testGenerateFromStringOne(self) -> None:
        aST = generate.fromString(self.aSTScript)
        self.assertIsInstance(aST, ast.AST, "generate.fromString should generate an AST")

    def testGenerateFromURLTwo(self) -> None:
        aST = ast.parse(self.aSTScript)
        remoteAST = generate.fromURL(self.aSTURL)
        self.assertTrue(self.compare_ast(aST, remoteAST), "AST from URL should be correct")

    def testGenerateFromStringTwo(self) -> None:
        defaultAST = ast.parse(self.aSTScript)
        generatedAST = generate.fromString(self.aSTScript)
        self.assertTrue(self.compare_ast(defaultAST, generatedAST), "AST from string should be correct")

    def testGenerateFrompathOne(self) -> None:
        import tempfile
        import urllib.request
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            remote = urllib.request.urlopen(self.aSTURL).read()
            tmp.write(remote)
            tmp.close()

            aST = generate.fromPath(tmp.name)
            os.unlink(tmp.name)
        self.assertIsInstance(aST, ast.AST, "generate.fromPath should generate an AST")

    def testVisualizationPyvis(self) -> None:
        aST = generate.fromString(self.aSTScript)
        visualise.graph(aST, really_show=True, plotter="pyvis") # could change this to False if it gets annoying

    def testVisualizationMatplotlib(self) -> None:
        aST = generate.fromString(self.aSTScript)
        visualise.graph(aST, really_show=True) # can change this to False if it gets annoying, or True to check with more certainty

    def compare_ast(self, node1: Union[ast.AST, ast.expr, list[ast.expr]], node2: Union[ast.AST, ast.expr, list[ast.expr]], ignore_args: bool =False) -> bool:
        """
        Function for comparing ASTs.
        Copy of Jonathan Biemond's answer to https://stackoverflow.com/questions/76352198/how-to-compare-two-python-asts-ignoring-arguments
        Compare two AST nodes for equality."""
        from itertools import zip_longest
        if type(node1) is not type(node2):
            return False

        if isinstance(node1, ast.AST):
            for k, v in vars(node1).items():
                if k in {"lineno", "end_lineno", "col_offset", "end_col_offset", "ctx"}:
                    continue
                if ignore_args and k == "args":
                    continue
                if not self.compare_ast(v, getattr(node2, k), ignore_args):
                    return False
            return True

        elif isinstance(node1, list) and isinstance(node2, list):
            return all(self.compare_ast(n1, n2, ignore_args) for n1, n2 in zip_longest(node1, node2))
        else:
            return node1 == node2 #type: ignore[comparison-overlap] #Not sure about this one...

if __name__ == "__main__":
    unittest.main()
