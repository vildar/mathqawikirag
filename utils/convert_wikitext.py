import re
import subprocess
import os

# Folder containing your 25 wikitext files
INPUT_FOLDER = "data/cleaned_articles/"
OUTPUT_FOLDER = "data/plaintext_articles/"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Regex to match <math ...>...</math> including attributes (non-greedy)
# MATH_REGEX = re.compile(r'<math[^>]*?>(.+?)</math>', re.DOTALL)
MATH_REGEX = re.compile(r'<math[^>]*?>.*?</math>', re.DOTALL)


def extract_math_blocks(text):
    math_blocks = []

    def replacer(match):
        math_blocks.append(match.group(1).strip())
        return f"__MATH_{len(math_blocks)-1}__"
    new_text = MATH_REGEX.sub(replacer, text)
    return new_text, math_blocks


def latex_to_asciimath(latex):
    # Use pandoc to convert LaTeX math to asciimath
    # echo latex | pandoc -f latex -t asciimath
    process = subprocess.run(
        ['pandoc', '-f', 'latex', '-t', 'asciimath'],
        input=latex.encode('utf-8'),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode != 0:
        print(
            f"Error converting LaTeX math: {latex}\n{process.stderr.decode()}")
        return latex  # fallback: original latex
    return process.stdout.decode('utf-8').strip()


def pandoc_convert_to_plaintext(input_path, output_path):
    # Convert math-stripped wikitext to plaintext using pandoc
    # pandoc -f mediawiki -t plain input -o output
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

    # Save intermediate math-stripped file
    math_stripped_path = filepath + ".nomath"
    with open(math_stripped_path, 'w', encoding='utf-8') as f:
        f.write(text_no_math)

    # Step 2: Convert stripped file to plaintext
    plaintext_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".txt")
    pandoc_convert_to_plaintext(math_stripped_path, plaintext_path)

    # Read converted plaintext
    with open(plaintext_path, 'r', encoding='utf-8') as f:
        plain_text = f.read()

    # Step 3: Convert each LaTeX math to ASCII math
    ascii_math_blocks = [latex_to_asciimath(m) for m in math_blocks]

    # Step 4: Replace placeholders with ascii math
    for i, ascii_math in enumerate(ascii_math_blocks):
        placeholder = f"__MATH_{i}__"
        plain_text = plain_text.replace(placeholder, ascii_math)

    # Save final output with math inserted
    final_output_path = os.path.join(
        OUTPUT_FOLDER, os.path.basename(filepath) + ".final.txt")
    with open(final_output_path, 'w', encoding='utf-8') as f:
        f.write(plain_text)

    # Clean up intermediate no-math file if you want
    os.remove(math_stripped_path)

    print(f"Finished {filepath}, output at {final_output_path}")


def main():
    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith(".wiki"):
            process_file(os.path.join(INPUT_FOLDER, filename))
        break


if __name__ == "__main__":
    main()
