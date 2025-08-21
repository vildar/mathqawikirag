import re
import subprocess
import os

INPUT_FOLDER = "data/cleaned_articles/"
OUTPUT_FOLDER = "data/plaintext_articles/"
PLACEHOLDER_FOLDER = "data/placeholder_articles/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PLACEHOLDER_FOLDER, exist_ok=True)

# Match <math> ... </math>
MATH_REGEX = re.compile(r'<math[^>]*?>(.*?)</math>', re.DOTALL)

# Common math environments that LaTeXML chokes on
MATH_ENVIRONMENTS = ["align", "align*", "equation", "eqnarray"]


def extract_math_blocks(text):
    """Replace <math> blocks with placeholders and collect LaTeX."""
    math_blocks = []

    def replacer(match):
        math_blocks.append(match.group(1).strip())
        return f"__MATH_{len(math_blocks)-1}__"

    new_text = MATH_REGEX.sub(replacer, text)
    return new_text, math_blocks


def normalize_latex_expr(expr: str) -> list[str]:
    """Split multi-line math environments into individual LaTeX expressions."""
    for env in MATH_ENVIRONMENTS:
        if expr.strip().startswith(f"\\begin{{{env}}}"):
            inner = re.sub(
                rf"\\begin{{{env}}}|\\end{{{env}}}", "", expr, flags=re.DOTALL)
            parts = [p.strip() for p in inner.split(r"\\\\") if p.strip()]
            return parts
    return [expr.strip()]


def latex_to_mathml(latex: str) -> str:
    """Convert LaTeX math to MathML using latexmlmath (via stdin)."""
    try:
        result = subprocess.run(
            # "-" = read TeX from stdin, write MathML to stdout
            ['latexmlmath', '-'],
            input=latex.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode != 0:
            raise RuntimeError(result.stderr.decode())
        return result.stdout.decode('utf-8').strip()
    except Exception as e:
        print(f"[LaTeXML error] LaTeX: {latex}\n{e}")
        return ""  # empty triggers fallback


def mathml_to_speech(mathml: str) -> str:
    """Use Speech Rule Engine to verbalize MathML."""
    if not mathml.strip():
        return ""  # avoid passing empty
    try:
        process = subprocess.run(
            ['sre'],
            input=mathml.encode('utf-8'),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if process.returncode != 0:
            raise RuntimeError(process.stderr.decode())
        return process.stdout.decode('utf-8').strip()
    except Exception as e:
        print(f"[SRE error] MathML failed\n{e}")
        return ""


def fallback_verbalizer(latex: str) -> str:
    """Heuristic fallback when LaTeXML+SRE fails."""
    # Simple regex-based heuristics
    replacements = [
        (r'\\frac{(.+?)}{(.+?)}', r'fraction \1 over \2'),
        (r'\\dot{(.+?)}', r'first derivative of \1'),
        (r'\\ddot{(.+?)}', r'second derivative of \1'),
        (r'\\boldsymbol{(.+?)}', r'bold \1'),
        (r'\\mathbf{(.+?)}', r'bold \1'),
        (r'\\alpha', 'alpha'),
        (r'\\omega', 'omega'),
        (r'\\zeta', 'zeta'),
    ]
    text = latex
    for pat, repl in replacements:
        text = re.sub(pat, repl, text)
    # Final cleanup
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # strip leftover commands
    return f"[MATH: {text.strip()}]"


def verbalize_latex_math(latex_expr: str) -> str:
    """Pipeline: LaTeX → MathML → Speech, with fallback + normalization."""
    pieces = normalize_latex_expr(latex_expr)
    speeches = []
    for piece in pieces:
        mathml = latex_to_mathml(piece)
        speech = mathml_to_speech(mathml)
        if not speech:  # fallback if failure
            speech = fallback_verbalizer(piece)
        speeches.append(speech)
    return " ; ".join(speeches)


def pandoc_convert_to_plaintext(input_path, output_path):
    """Convert math-stripped wikitext to plaintext using pandoc."""
    result = subprocess.run(
        ['pandoc', '-f', 'mediawiki', '-t', 'plain', input_path, '-o', output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print(
            f"Pandoc conversion failed for {input_path}:\n{result.stderr.decode()}")


def process_file(filepath):
    print(f"Processing {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        original_text = f.read()

    # Step 1: Extract math blocks & replace with placeholders
    text_no_math, math_blocks = extract_math_blocks(original_text)

    # Save intermediate placeholder article
    placeholder_path = os.path.join(
        PLACEHOLDER_FOLDER, os.path.basename(filepath) + ".nomath")
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(text_no_math)

    # Step 2: Convert placeholder article to plaintext
    plaintext_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".txt")
    pandoc_convert_to_plaintext(placeholder_path, plaintext_path)

    # Read converted plaintext
    with open(plaintext_path, 'r', encoding='utf-8') as f:
        plain_text = f.read()

    # Step 3: Convert each LaTeX math to verbalized natural language
    verbalized_math_blocks = [verbalize_latex_math(m) for m in math_blocks]

    # Step 4: Replace placeholders with verbalized math
    for i, speech in enumerate(verbalized_math_blocks):
        placeholder = f"__MATH_{i}__"
        plain_text = plain_text.replace(placeholder, speech)

    # Save final output with verbalized math inserted
    final_output_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".final.txt")
    with open(final_output_path, 'w', encoding='utf-8') as f:
        f.write(plain_text)

    print(f"Finished {filepath}, output at {final_output_path}")


def main():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".wiki"):
            process_file(os.path.join(INPUT_FOLDER, filename))
            break  # remove this to process all files


if __name__ == "__main__":
    main()
