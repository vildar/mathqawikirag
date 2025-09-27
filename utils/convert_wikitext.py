import os
import subprocess
from pylatexenc.latex2text import MacroTextSpec
from pylatexenc import latex2text
import re
import mwparserfromhell
import json

GLOBAL_MATH_COUNTER = 0
GLOBAL_MATH_MAP = {}
GLOBAL_MATH_JSON_PATH = "data/math_blocks.json"
INPUT_FOLDER = "data/cleaned_articles/"
OUTPUT_FOLDER = "data/plaintext_articles/"
PLACEHOLDER_FOLDER = "data/placeholder_articles/"
PARSED_PLACEHOLDER_FOLDER = "data/parsed_placeholder_articles/"

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

# Custom macro because it was struggling to figure out how to deal with \\frac


def frac_macro_repl(n, l2tobj):
    """
    n: node representing \frac
    l2tobj: LatexNodes2Text instance
    """
    args = [l2tobj.nodelist_to_text([arg]) for arg in n.nodeargd.argnlist]
    return f"({args[0]})/({args[1]})"


l2t_context_db = latex2text.get_default_latex_context_db()
l2t_context_db.add_context_category(
    'my-fractions',
    macros=[
        MacroTextSpec('frac', simplify_repl=frac_macro_repl)
    ]
)

# Create the converter using the custom context
latex_converter = latex2text.LatexNodes2Text(latex_context=l2t_context_db)


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
    return latex_converter.latex_to_text(latex_expr).strip()


def template_to_latex(template, prev_text=""):
    name = str(template.name).strip().lower()

    if name not in ALLOWED_TEMPLATES:
        return str(template)

    param_values = {}
    for i, param in enumerate(template.params):
        value = str(param.value).strip()
        value = re.sub(r'<sup>(.*?)</sup>', r'^{\1}', value)
        value = re.sub(r'<sub>(.*?)</sub>', r'_{\1}', value)

        # Recursively convert nested templates
        try:
            nested_templates = mwparserfromhell.parse(value).filter_templates()
            for nt in nested_templates:
                value = value.replace(str(nt), template_to_latex(nt))
        except Exception:
            pass

        # Assign parameters
        if name in ["sfrac", "frac", "cfrac"]:
            param_values["numerator" if i == 0 else "denominator"] = value
        elif name == "binom":
            param_values["n" if i == 0 else "k"] = value
        elif name in ["sub", "sup"]:
            if i == 0:
                param_values["base"] = value  # just use value if provided
            elif i == 1:
                param_values[name] = value
        else:
            param_values["content"] = value

    if name in ["sub", "sup"]:
        base = param_values.get("base", "")
        sub = param_values.get("sub", "")
        sup = param_values.get("sup", "")
        if base and (sub or sup):
            latex = TEMPLATE_LATEX_MAP[name].format(
                base=base, sub=sub, sup=sup)
        elif base:  # Only one argument, treat as sub/sup of previous token or just output
            if name == "sup":
                latex = f"^{{{base}}}"
            else:
                latex = f"_{{{base}}}"
        else:
            latex = ""
    else:
        latex = TEMPLATE_LATEX_MAP[name].format(
            base=param_values.get("base", ""),
            sub=param_values.get("sub", ""),
            sup=param_values.get("sup", ""),
            numerator=param_values.get("numerator", ""),
            denominator=param_values.get("denominator", ""),
            n=param_values.get("n", ""),
            k=param_values.get("k", ""),
            content=param_values.get("content", "")
        )

    return latex


def extract_math_blocks(text, start_index):
    wikicode = mwparserfromhell.parse(text)
    index_counter = start_index  # start from the given index

    def process_nodes(wikicode_obj):
        nonlocal index_counter
        for node in list(wikicode_obj.nodes):
            if isinstance(node, mwparserfromhell.nodes.Tag) and node.tag.lower() == 'math':
                placeholder = f"__MATH_{index_counter}__"
                readable = convert_latex_to_text(str(node.contents).strip())
                GLOBAL_MATH_MAP[placeholder] = readable
                wikicode_obj.replace(node, placeholder)
                index_counter += 1
            elif isinstance(node, mwparserfromhell.nodes.Template):
                name = str(node.name).strip().lower()
                if name in ALLOWED_TEMPLATES:
                    latex_content = template_to_latex(node)
                    readable = convert_latex_to_text(latex_content)
                    placeholder = f"__MATH_{index_counter}__"
                    GLOBAL_MATH_MAP[placeholder] = readable
                    wikicode_obj.replace(node, placeholder)
                    index_counter += 1
            if hasattr(node, 'contents') and isinstance(node.contents, mwparserfromhell.wikicode.Wikicode):
                process_nodes(node.contents)

    process_nodes(wikicode)
    return str(wikicode), index_counter


def pandoc_convert_to_plaintext(input_path, output_path):
    result = subprocess.run(
        ['pandoc', '-f', 'mediawiki', '-t', 'plain', input_path, '-o', output_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    if result.returncode != 0:
        print(
            f"Pandoc conversion failed for {input_path}:\n{result.stderr.decode()}")


def process_file(filepath):
    global GLOBAL_MATH_COUNTER

    print(f"Processing {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        original_text = f.read()

    # Replace math with placeholders and update global map
    text_with_placeholders, GLOBAL_MATH_COUNTER = extract_math_blocks(
        original_text, GLOBAL_MATH_COUNTER)

    # Save no-math placeholder file (optional)
    placeholder_path = os.path.join(
        PLACEHOLDER_FOLDER, os.path.basename(filepath) + ".nomath")
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(text_with_placeholders)

    # Convert placeholder text to plain text via pandoc
    plaintext_path = os.path.join(
        PARSED_PLACEHOLDER_FOLDER, os.path.basename(filepath) + ".txt")
    pandoc_convert_to_plaintext(placeholder_path, plaintext_path)

    with open(plaintext_path, 'r', encoding='utf-8') as f:
        plain_text = f.read()

    # Replace global math placeholders with converted text
    for placeholder, latex in GLOBAL_MATH_MAP.items():
        plain_text = plain_text.replace(
            placeholder, convert_latex_to_text(latex))

    final_output_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".txt")
    with open(final_output_path, 'w', encoding='utf-8') as f:
        f.write(plain_text)

    print(f"Finished {filepath}, output at {final_output_path}")


def main():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".wiki"):
            process_file(os.path.join(INPUT_FOLDER, filename))

    # Save the global math map to a single JSON file
    with open(GLOBAL_MATH_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(GLOBAL_MATH_MAP, f, indent=2, ensure_ascii=False)
    print(f"\nSaved global math block map to {GLOBAL_MATH_JSON_PATH}")


if __name__ == "__main__":
    main()
