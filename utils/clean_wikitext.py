import mwparserfromhell
import re
import os


def clean_wiki_text(wikitext, allowed_templates, sections_to_remove, namespace_prefixes):
    wikicode = mwparserfromhell.parse(wikitext)

    new_nodes = []
    for node in wikicode.nodes:
        if isinstance(node, mwparserfromhell.nodes.template.Template):
            template_name = str(node.name).strip().lower()
            if template_name in allowed_templates:
                new_nodes.append(node)
        elif isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
            title = str(node.title).strip().lower()
            if not any(title.startswith(prefix) for prefix in namespace_prefixes):
                new_nodes.append(node)
        elif isinstance(node, mwparserfromhell.nodes.tag.Tag):
            if node.tag.lower() not in ["ref", "gallery", "timeline"]:
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    wikicode.nodes[:] = new_nodes

    sections_to_remove_lower = {s.lower() for s in sections_to_remove}
    for section in wikicode.get_sections(include_lead=True, include_headings=True):
        headings = section.filter_headings()
        if headings and headings[0].title.strip().lower() in sections_to_remove_lower:
            wikicode.remove(section)
        else:
            # Also remove empty sections
            content_nodes = [n for n in section.nodes if not isinstance(
                n, mwparserfromhell.nodes.heading.Heading)]
            if not any(str(n).strip() for n in content_nodes):
                wikicode.remove(section)

    cleaned_text = str(wikicode).strip()
    cleaned_text = re.sub(r'(==+.*?==+)\n{2,}', r'\1\n\n', cleaned_text)
    return cleaned_text


allowed_templates = [
    "abs", "dimanalysis", "equation box 1", "equationnote", "equationref",
    "math", "math proof", "mvar", "pi", "radic", "sfrac", "frac", "cfrac",
    "sqrt", "sub", "sup", "val", "var", "vec", "binom", "over", "underline",
    "overline", "text", "bold", "italic"
]

sections_to_remove = [
    "Conversions", "See also", "External links", "References", "Notes",
    "Further reading", "Bibliography", "Sources", "Footnotes", "Citations",
    "Related articles", "Links", "Navigation", "History", "Appendix"
]

namespace_prefixes = [
    "file:", "image:", "category:", "template:", "user:",
    "wikipedia:", "help:", "portal:", "draft:", "module:",
    "special:", "media:", "mediawiki:", "talk:"
]

os.makedirs('data/cleaned_articles', exist_ok=True)

with os.scandir('wikipedia_articles') as entries:
    for entry in entries:
        if entry.is_file() and entry.name.endswith('.wiki'):
            with open(entry.path, 'r', encoding="utf-8") as file:
                text = file.read()

            cleaned_text = clean_wiki_text(
                text, allowed_templates, sections_to_remove, namespace_prefixes)

            with open(f"data/cleaned_articles/{entry.name}", 'w', encoding='utf-8') as cleaned_file:
                cleaned_file.write(cleaned_text)
