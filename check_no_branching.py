
import ast
import sys
import glob

BANNED_NODE_TYPES = (
    ast.For,
    ast.AsyncFor,
    ast.If,
    ast.While,
    ast.IfExp,       
)


def find_violations(path):
    tree = ast.parse(open(path, encoding="utf-8").read(), filename=path)
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, BANNED_NODE_TYPES):
            violations.append((path, node.lineno, type(node).__name__))
        if isinstance(node, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
            for generator in node.generators:
                if generator.ifs:
                    violations.append((path, node.lineno, "Comprehension-if"))
    return violations


def main():
    import os
    project_dir = os.path.dirname(os.path.abspath(__file__))
    self_path = os.path.abspath(__file__)
    files = sorted(
        f for f in glob.glob(os.path.join(project_dir, "*.py"))
        if os.path.abspath(f) != self_path
    )
    all_violations = []
    for f in files:
        all_violations.extend(find_violations(f))
    if all_violations:
        print("VIOLATIONS FOUND:")
        for path, lineno, kind in all_violations:
            print(f"  {path}:{lineno}  {kind}")
        sys.exit(1)
    print(f"Clean: {len(files)} files checked, zero for/if/while/elif/ternary found.")


if __name__ == "__main__":
    main()
