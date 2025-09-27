from pylatexenc.latex2text import LatexNodes2Text
from pylatexenc.macrospec import MacroSpec, LatexContextDb

# Define how to render \frac


def render_frac(n, **kwargs):
    if len(n.nodeargd.argnlist) == 2:
        numerator = LatexNodes2Text().nodelist_to_text(n.nodeargd.argnlist[0])
        denominator = LatexNodes2Text().nodelist_to_text(
            n.nodeargd.argnlist[1])
        return f"({numerator})/({denominator})"
    return "\\frac"


# Create a custom LaTeX context with support for \frac
context = LatexContextDb()
context.add_context_category('custom', macros=[
    MacroSpec('frac', argspec='{}{}')
])
context.set_macro_rendering('frac', render_frac)

# Converter with the custom context
converter = LatexNodes2Text(latex_context=context)

# List of articles
articles = [
    # "Acceleration", "Angular_acceleration", "Angular_frequency", "Angular_momentum",
    # "Angular_velocity", "Center_of_mass", "Centrifugal_force", "Centripetal_force",
    "Circular_motion", "Coriolis_force", "Equations_of_motion", "Force", "Frequency",
    "Harmonic_oscillator", "Jerk_(physics)", "Mass", "Moment_of_inertia", "Momentum",
    "Motion", r"Newton's_laws_of_motion", "Rotation", "Speed", "Torque", "Velocity", "Work_(physics)"
]

# Process each article
for article in articles:
    with open(f"data/cleaned_articles/{article}.txt", "r", encoding="utf-8") as file:
        latex = file.read()
        text = converter.latex_to_text(latex)
    with open(f"data/cleaned_articles/{article}.txt", "w", encoding="utf-8") as cleaned_file:
        cleaned_file.write(text)
    print(f"Finished {article}")
