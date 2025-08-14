import requests

articles = [
    "Acceleration", "Angular_acceleration", "Angular_frequency", "Angular_momentum",
    "Angular_velocity", "Center_of_mass", "Centrifugal_force", "Centripetal_force",
    "Circular_motion", "Coriolis_force", "Equations_of_motion", "Force", "Frequency",
    "Harmonic_oscillator", "Jerk_(physics)", "Mass", "Moment_of_inertia", "Momentum",
    "Motion", r"Newton's_laws_of_motion", "Rotation", "Speed", "Torque", "Velocity", "Work_(physics)"
]


def fetch_article_text(title):
    url = f"https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "titles": title,
        "format": "json"
    }

    response = requests.get(url, params=params)
    data = response.json()

    pages = data.get("query", {}).get("pages", {})
    page = next(iter(pages.values()))

    if "revisions" not in page:
        print(f"Page '{title}' not found or has no revisions.")
        return

    wiki_text = page["revisions"][0]["slots"]["main"]["*"]

    return wiki_text or "No content found."


def save_to_text_file(title, content):
    with open(f"wikipedia_articles/{title}.wiki", "w", encoding="utf-8") as file:
        file.write(content)


for article in articles:
    print(f"Downloading {article}...")
    article_content = fetch_article_text(article)
    save_to_text_file(article, article_content)

print("Download complete!")
