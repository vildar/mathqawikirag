import mwparserfromhell
import os

# Example usage
# articles = [
#     "Acceleration", "Angular_acceleration", "Angular_frequency", "Angular_momentum",
#     "Angular_velocity", "Center_of_mass", "Centrifugal_force", "Centripetal_force",
#     "Circular_motion", "Coriolis_force", "Equations_of_motion", "Force", "Frequency",
#     "Harmonic_oscillator", "Jerk_(physics)", "Mass", "Moment_of_inertia", "Momentum",
#     "Motion", r"Newton's_laws_of_motion", "Rotation", "Speed", "Torque", "Velocity", "Work_(physics)"
# ]

# for article in articles:
#     with open(f"wikipedia_articles/{article}.txt", "r", encoding="utf-8") as file:
#         cleaned = clean_wiki_math(file.read())
#     with open(f"data/cleaned_articles/{article}.txt", "w", encoding="utf-8") as cleaned_file:
#         cleaned_file.write(cleaned)


def extract_unique_templates(folder_path):
    unique_templates = set()

    for filename in os.listdir(folder_path):
        if filename.endswith(".wiki"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                wikitext = f.read()
            wikicode = mwparserfromhell.parse(wikitext)
            templates = wikicode.filter_templates()
            for template in templates:
                name = str(template.name).strip().lower()
                unique_templates.add(name)

    return sorted(unique_templates)


templates = extract_unique_templates('data/cleaned_articles')

with open('data/unique_templates.txt', "w") as file:
    for name in sorted(templates):
        file.write(name + "\n")
