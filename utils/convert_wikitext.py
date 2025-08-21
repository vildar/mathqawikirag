import os
import subprocess
from pylatexenc.latex2text import LatexNodes2Text
import re
import mwparserfromhell

INPUT_FOLDER = "data/cleaned_articles/"
OUTPUT_FOLDER = "data/plaintext_articles/"
PLACEHOLDER_FOLDER = "data/placeholder_articles/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(PLACEHOLDER_FOLDER, exist_ok=True)

# --- Allowed math templates ---
ALLOWED_TEMPLATES = [
    "abs", "dimanalysis", "equation box 1", "equationnote", "equationref",
    "math", "math proof", "mvar", "pi", "radic", "sfrac", "frac", "cfrac",
    "sqrt", "sub", "sup", "val", "var", "vec", "binom", "over", "underline",
    "overline", "text", "bold", "italic"
]

MATH_ENVIRONMENTS = ["align", "align*", "equation", "eqnarray", "eqnarray*"]

# --- Template -> LaTeX mapping ---
TEMPLATE_LATEX_MAP = {
    "abs": r"\left|{content}\right|",
    "dimanalysis": r"{content}",
    "equation box 1": r"{content}",
    "equationnote": r"{content}",
    "equationref": r"{content}",
    "math": r"{content}",
    "math proof": r"{content}",
    "mvar": r"{content}",
    "pi": r"\pi",
    "radic": r"\sqrt{{{content}}}",
    "sfrac": r"\frac{{{numerator}}}{{{denominator}}}",
    "frac": r"\frac{{{numerator}}}{{{denominator}}}",
    "cfrac": r"\cfrac{{{numerator}}}{{{denominator}}}",
    "sqrt": r"\sqrt{{{content}}}",
    "sub": r"{base}_{{{sub}}}",
    "sup": r"{base}^{{{sup}}}",
    "val": r"{content}",
    "var": r"{content}",
    "vec": r"\vec{{{content}}}",
    "binom": r"\binom{{{n}}}{{{k}}}",
    "over": r"{numerator} / {denominator}",
    "underline": r"\underline{{{content}}}",
    "overline": r"\overline{{{content}}}",
    "text": r"\text{{{content}}}",
    "bold": r"\mathbf{{{content}}}",
    "italic": r"\mathit{{{content}}}"
}


def flatten_multiline_environments(latex_expr: str) -> str:
    for env in MATH_ENVIRONMENTS:
        pattern = re.compile(
            rf'\\begin{{{env}}}(.*?)\\end{{{env}}}', re.DOTALL)

        def repl(m):
            lines = [line.strip()
                     for line in m.group(1).split(r"\\") if line.strip()]
            return ' ; '.join(lines)
        latex_expr = pattern.sub(repl, latex_expr)
    return latex_expr


def convert_latex_to_text(latex_expr: str) -> str:
    latex_expr = flatten_multiline_environments(latex_expr)
    return LatexNodes2Text().latex_to_text(latex_expr).strip()


def template_to_latex(template):
    """Recursively convert a template to LaTeX, and handle nested templates at the lowest level."""
    name = str(template.name).strip().lower()

    # If template is not allowed, return as-is
    if name not in ALLOWED_TEMPLATES:
        return str(template)

    # Process parameters recursively
    param_values = {}
    for i, param in enumerate(template.params):
        value = str(param.value).strip()

        # Clean HTML sup/sub if present
        value = re.sub(r'<sup>(.*?)</sup>', r'^{\1}', value)
        value = re.sub(r'<sub>(.*?)</sub>', r'_{\1}', value)

        # Recursively convert nested templates
        try:
            nested_templates = mwparserfromhell.parse(value).filter_templates()
            if nested_templates:
                # Convert all nested templates
                for nt in nested_templates:
                    value = value.replace(str(nt), template_to_latex(nt))
        except Exception:
            pass

        # At lowest level: check if value itself contains a key from TEMPLATE_LATEX_MAP
        # and convert it if possible
        for key in TEMPLATE_LATEX_MAP.keys():
            # simple check for {{key|...}} inside value
            pattern = re.compile(
                rf'{{{{\s*{re.escape(key)}\s*\|(.+?)}}}}', re.DOTALL)

            def repl(m):
                inner_value = m.group(1)
                # Wrap as template and convert
                pseudo_template = mwparserfromhell.parse(
                    f"{{{{{key}|{inner_value}}}}}").filter_templates()[0]
                return template_to_latex(pseudo_template)
            value = pattern.sub(repl, value)

        # Assign parameter names based on template type
        if name in ["sfrac", "frac", "cfrac"]:
            if i == 0:
                param_values["numerator"] = value
            elif i == 1:
                param_values["denominator"] = value
        elif name in ["sub", "sup"]:
            if i == 0:
                param_values["base"] = value
            elif i == 1:
                param_values[name] = value
        elif name in ["binom"]:
            if i == 0:
                param_values["n"] = value
            elif i == 1:
                param_values["k"] = value
        else:
            param_values["content"] = value

    # Finally, format using the template map
    return TEMPLATE_LATEX_MAP[name].format(**param_values)


def extract_math_blocks(text):
    wikicode = mwparserfromhell.parse(text)
    math_blocks = []

    def process_nodes(wikicode_obj):
        for node in list(wikicode_obj.nodes):  # iterate over a copy
            if isinstance(node, mwparserfromhell.nodes.Tag) and node.tag.lower() == 'math':
                index = len(math_blocks)
                math_blocks.append(str(node.contents).strip())
                wikicode_obj.replace(node, f"__MATH_{index}__")
            elif isinstance(node, mwparserfromhell.nodes.Template):
                name = str(node.name).strip().lower()
                if name in ALLOWED_TEMPLATES:
                    index = len(math_blocks)
                    latex_content = template_to_latex(node)
                    math_blocks.append(latex_content)
                    wikicode_obj.replace(node, f"__MATH_{index}__")
            # Recurse if node has child Wikicode
            if hasattr(node, 'contents') and isinstance(node.contents, mwparserfromhell.wikicode.Wikicode):
                process_nodes(node.contents)

    process_nodes(wikicode)
    return str(wikicode), math_blocks


def pandoc_convert_to_plaintext(input_path, output_path):
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

    text_with_placeholders, math_blocks = extract_math_blocks(original_text)

    placeholder_path = os.path.join(
        PLACEHOLDER_FOLDER, os.path.basename(filepath) + ".nomath")
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(text_with_placeholders)

    plaintext_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".txt")
    pandoc_convert_to_plaintext(placeholder_path, plaintext_path)

    with open(plaintext_path, 'r', encoding='utf-8') as f:
        plain_text = f.read()

    converted_blocks = [convert_latex_to_text(m) for m in math_blocks]
    for i, conv in enumerate(converted_blocks):
        plain_text = plain_text.replace(f"__MATH_{i}__", conv)

    final_output_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".final.txt")
    with open(final_output_path, 'w', encoding='utf-8') as f:
        f.write(plain_text)

    print(f"Finished {filepath}, output at {final_output_path}")


def main():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".wiki"):
            process_file(os.path.join(INPUT_FOLDER, filename))


if __name__ == "__main__":
    main()
