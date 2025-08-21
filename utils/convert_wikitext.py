import re
import subprocess
import os

INPUT_FOLDER = "data/cleaned_articles/"
OUTPUT_FOLDER = "data/plaintext_articles/"
PLACEHOLDER_FOLDER = "data/placeholder_articles/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PLACEHOLDER_FOLDER, exist_ok=True)

# Allowed templates
ALLOWED_TEMPLATES = [
    "abs", "dimanalysis", "equation box 1", "equationnote", "equationref",
    "math", "math proof", "mvar", "pi", "radic", "sfrac", "sqrt", "sub",
    "sup", "val", "var", "vec"
]

# Multi-line math environments
MATH_ENVIRONMENTS = ["align", "align*", "equation", "eqnarray"]

# Regex for <math>...</math>
MATH_TAG_REGEX = re.compile(r'<math[^>]*?>(.*?)</math>', re.DOTALL)

# Regex for allowed templates
TEMPLATE_REGEX = re.compile(
    r'{{\s*(' + '|'.join(re.escape(t)
                         for t in ALLOWED_TEMPLATES) + r')\s*\|([^}]*)}}',
    re.IGNORECASE
)


def extract_math_blocks(text):
    """
    Replace <math> tags and allowed templates with placeholders,
    and collect their content for normalization.
    """
    math_blocks = []

    # Replace <math> tags
    def math_tag_replacer(match):
        math_blocks.append(match.group(1).strip())
        return f"__MATH_{len(math_blocks)-1}__"

    text = MATH_TAG_REGEX.sub(math_tag_replacer, text)

    # Replace allowed templates
    def template_replacer(match):
        content = match.group(2).strip()
        math_blocks.append(content)
        return f"__MATH_{len(math_blocks)-1}__"

    text = TEMPLATE_REGEX.sub(template_replacer, text)

    return text, math_blocks


def normalize_latex(latex_expr: str) -> str:
    """
    Normalize LaTeX expressions:
    - Split multi-line environments
    - Replace common LaTeX commands with simpler notation
    """
    # Handle multi-line environments
    for env in MATH_ENVIRONMENTS:
        if latex_expr.startswith(f"\\begin{{{env}}}"):
            inner = re.sub(
                rf'\\begin{{{env}}}|\\end{{{env}}}', '', latex_expr, flags=re.DOTALL)
            parts = [p.strip() for p in inner.split(r"\\") if p.strip()]
            latex_expr = ' ; '.join(parts)

    # Lightweight replacements
    replacements = [
        (r'\\frac{(.+?)}{(.+?)}', r'(\1)/(\2)'),
        (r'\\cdot|\\times', '*'),
        (r'\\dot{(.+?)}', r"\1'"),
        (r'\\ddot{(.+?)}', r"\1''"),
        (r'\\boldsymbol{(.+?)}', r"\1"),
        (r'\\mathbf{(.+?)}', r"\1"),
        (r'\\[a-zA-Z]+', ''),  # remove remaining LaTeX commands
    ]

    for pat, repl in replacements:
        latex_expr = re.sub(pat, repl, latex_expr)

    return latex_expr.strip()


def pandoc_convert_to_plaintext(input_path, output_path):
    """Convert placeholder article to plain text using pandoc."""
    result = subprocess.run(
        ['pandoc', '-f', 'mediawiki', '-t', 'plain', input_path, '-o', output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print(
            f"Pandoc conversion failed for {input_path}:\n{result.stderr.decode()}")


def process_file(filepath):
    print(f"Processing {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        original_text = f.read()

    # Step 1: Extract math blocks and replace with placeholders
    text_with_placeholders, math_blocks = extract_math_blocks(original_text)

    # Save intermediate placeholder file
    placeholder_path = os.path.join(
        PLACEHOLDER_FOLDER, os.path.basename(filepath) + ".nomath"
    )
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(text_with_placeholders)

    # Step 2: Convert placeholder file to plaintext
    plaintext_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".txt"
    )
    pandoc_convert_to_plaintext(placeholder_path, plaintext_path)

    # Read converted plaintext
    with open(plaintext_path, 'r', encoding='utf-8') as f:
        plain_text = f.read()

    # Step 3: Normalize LaTeX math blocks
    normalized_blocks = [normalize_latex(m) for m in math_blocks]

    # Step 4: Replace placeholders with normalized LaTeX
    for i, norm in enumerate(normalized_blocks):
        placeholder = f"__MATH_{i}__"
        plain_text = plain_text.replace(placeholder, norm)

    # Save final output
    final_output_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".final.txt"
    )
    with open(final_output_path, 'w', encoding='utf-8') as f:
        f.write(plain_text)

    print(f"Finished {filepath}, output at {final_output_path}")


def main():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".wiki"):
            process_file(os.path.join(INPUT_FOLDER, filename))


if __name__ == "__main__":
    main()
