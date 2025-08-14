import mwparserfromhell
import re
import os


def clean_wiki_text(wikitext, allowed_templates, sections_to_remove, namespace_prefixes):
    wikicode = mwparserfromhell.parse(wikitext)

    new_nodes = []
    for node in wikicode.nodes:
        if isinstance(node, mwparserfromhell.nodes.template.Template):
            if node.name.strip().lower() in allowed_templates:
                new_nodes.append(node)
        elif isinstance(node, mwparserfromhell.nodes.wikilink.Wikilink):
            title = str(node.title).strip().lower()
            if not any(title.startswith(prefix) for prefix in namespace_prefixes):
                new_nodes.append(node)
        elif isinstance(node, mwparserfromhell.nodes.tag.Tag):
            if node.tag.lower() != "ref":
                new_nodes.append(node)
        else:
            new_nodes.append(node)
    wikicode.nodes[:] = new_nodes

    sections = list(wikicode.get_sections(
        include_lead=False, include_headings=True))
    for section in reversed(sections):
        headings = section.filter_headings()
        if not headings:
            continue
        heading = headings[0].title.strip().lower()
        if heading in [s.lower() for s in sections_to_remove]:
            wikicode.remove(section)
        else:
            break

    for section in reversed(wikicode.get_sections(include_lead=False, include_headings=True)):
        content_nodes = [node for node in section.nodes if not isinstance(
            node, mwparserfromhell.nodes.heading.Heading)]
        content_str = ''.join(str(node).strip()
                              for node in content_nodes).strip()
        if not content_str:
            wikicode.remove(section)

    cleaned_text = str(wikicode).strip()
    cleaned_text = re.sub(r'(==+.*?==+)\n{2,}', r'\1\n\n', cleaned_text)

    return cleaned_text


allowed_templates = [
    "abs",
    "dimanalysis",
    "equation box 1",
    "equationnote",
    "equationref",
    "math",
    "math proof",
    "mvar",
    "pi",
    "radic",
    "sfrac",
    "sqrt",
    "sub",
    "sup",
    "val",
    "var",
    "vec"
]
sections_to_remove = [
    "Conversions",
    "See also",
    "External links",
    "References",
    "Notes",
    "Further reading",
    "Bibliography",
    "Sources",
    "Footnotes",
    "Citations",
    "Related articles",
    "Links",
    "Navigation",
    "History",
    "Appendix"
]

namespace_prefixes = [
    "file:", "image:", "category:", "template:", "user:",
    "wikipedia:", "help:", "portal:", "draft:", "module:",
    "special:", "media:", "mediawiki:", "talk:"
]


with os.scandir('wikipedia_articles') as entries:
    for entry in entries:
        if entry.is_file() and entry.name.endswith('.wiki'):
            with open(entry.path, 'r', encoding="utf-8") as file:
                text = file.read()

            cleaned_text = clean_wiki_text(
                text, allowed_templates, sections_to_remove, namespace_prefixes)

            with open(f"data/cleaned_articles/{entry.name}", "w") as cleaned_file:
                cleaned_file.write(cleaned_text)
