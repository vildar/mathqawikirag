from pylatexenc.latex2text import LatexNodes2Text

with open("data/cleaned_articles/Acceleration.txt", "r") as file:
    latex = file.read()

text = LatexNodes2Text().latex_to_text(latex)
with open("data/cleaned_articles/Acceleration_latex2text.txt", "w") as file:
    file.write(text)
