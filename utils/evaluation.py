import json
import re
import os


def is_complex_formula(formula, MIN_COMPLEXITY):
    complexity_indicators = [
        r'\\sum',   # Summation
        r'\\int',   # Integral
        r'\\frac',  # Fractions
        r'\\sqrt',  # Square roots
        r'[A-Za-z]+\(',  # Functions like sin(), cos(), exp(), etc.
        r'[0-9]+[A-Za-z]+',  # Variables like x1, y2, etc.
        r'[\\\+\-\*/\^=]',  # Operators like +, -, *, /, ^, =
        r'[\(\)]'  # Parentheses
    ]

    complexity_score = 0
    for pattern in complexity_indicators:
        if re.search(pattern, formula):
            complexity_score += 1

    return complexity_score >= MIN_COMPLEXITY


def load_formula_mapping(mapping_file):
    with open(mapping_file, 'r') as file:
        return json.load(file)


def extract_placeholders(text):
    return re.findall(r'__MATH_\d+__', text)


def replace_placeholders_with_formulas(text, formula_mapping):
    placeholders = extract_placeholders(text)
    complex_formulas = []
    available_formulas = []
    MIN_COMPLEXITY = 2

    for placeholder in placeholders:
        if placeholder in formula_mapping:
            formula = formula_mapping[placeholder]
            available_formulas.append(formula)

            if is_complex_formula(formula, MIN_COMPLEXITY):
                if len(complex_formulas) < 4:
                    complex_formulas.append(formula)

        if len(complex_formulas) == 4:
            break

    while len(complex_formulas) < 4 and available_formulas:
        formula = available_formulas.pop(0)

        if is_complex_formula(formula, MIN_COMPLEXITY=1):
            complex_formulas.append(formula)

    return list(complex_formulas)


def read_wikitext_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()


def process_article(file_path, formula_mapping):
    text = read_wikitext_file(file_path)
    formulas = replace_placeholders_with_formulas(text, formula_mapping)

    return formulas


def save_to_json(file_name, data):
    with open(file_name, 'w') as json_file:
        json.dump(data, json_file, indent=4)


def process_all_articles(articles_dir, formula_mapping, output_file):
    processed_articles = []

    for filename in os.listdir(articles_dir):
        if filename.endswith(".txt"):
            article_path = os.path.join(articles_dir, filename)
            formulas = process_article(article_path, formula_mapping)

            processed_articles.append({
                'article_id': filename,
                'formulas': formulas
            })
    save_to_json(output_file, processed_articles)


if __name__ == "__main__":
    articles_dir = 'data/parsed_placeholder_articles/'
    formula_mapping_file = 'data/math_blocks.json'
    output_file = 'data/evaluation/evaluation_formulas.json'

    formula_mapping = load_formula_mapping(formula_mapping_file)

    process_all_articles(articles_dir, formula_mapping, output_file)
    print(f"Processed articles saved to {output_file}")
