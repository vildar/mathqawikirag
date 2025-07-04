import requests

articles = [
    "Acceleration", "Angular_acceleration", "Angular_frequency", "Angular_momentum",
    "Angular_velocity", "Center_of_mass", "Centrifugal_force", "Centripetal_force",
    "Circular_motion", "Coriolis_force", "Equations_of_motion", "Force", "Frequency",
    "Harmonic_oscillator", "Jerk_(physics)", "Mass", "Moment_of_inertia", "Momentum",
    "Motion", "Newton%27s_laws_of_motion", "Rotation", "Speed", "Torque", "Velocity", "Work_(physics)"
]


def fetch_article_text(title):
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": True,
        "titles": title,
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    # Extract the page's content
    page = next(iter(data["query"]["pages"].values()))
    return page.get("extract", "No content found.")


def save_to_text_file(title, content):
    # Replace spaces and special characters in file names
    title_filename = title.replace(" ", "_").replace("%27", "'")
    with open(f"wikipedia_articles/{title_filename}.txt", "w", encoding="utf-8") as file:
        file.write(content)


for article in articles:
    print(f"Downloading {article}...")
    article_content = fetch_article_text(article)
    save_to_text_file(article, article_content)

print("Download complete!")
