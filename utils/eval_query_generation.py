import json
import random

with open("data/evaluation/evaluation_formulas_labelled.json", "r") as f:
    formulas = json.load(f)

templates = [
    "What is the formula for {name}?",
    "Define the formula of {name}.",
    "State the equation of {name}.",
    "Give the mathematical expression of {name}.",
    "How is {name} expressed mathematically?",
    "What is the relationship for {name}?"
]

queries = {}

for article in formulas:
    for formula in article["formulas"]:
        formula_name = formula["name"]
        gt_formula = formula["formula"]
        question = random.choice(templates).format(name=formula_name)
        queries[question] = gt_formula

with open("data/evaluation/evaluation_queries.json", "w") as f:
    json.dump(queries, f, indent=4)

print(f"Generated {len(queries)} queries in queries.json")
