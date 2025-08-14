import re
from sympy.parsing.latex import parse_latex
from sympy.printing import pretty


def _compact(s: str) -> str:
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s+([,.;:])', r'\1', s)
    s = re.sub(r'([(\[{])\s+', r'\1', s)
    s = re.sub(r'\s+([)\]}])', r'\1', s)
    return s.strip()


_MATHY_CHARS = r'[\s\w\-=+\/*^.,;:⋅ΔδμνπθλωΩαβγ¯]'


def _looks_like_stacked_ascii(block: str) -> bool:
    b = block.strip()
    if not b or b.count('\n') < 2:
        return False
    return re.fullmatch(_MATHY_CHARS + r'+', b, flags=re.UNICODE) is not None


def latex_to_ascii(latex: str) -> str:
    r"""Convert LaTeX inside {\displaystyle ...} to normalized ASCII/Unicode."""
    latex = re.sub(r'^\{\s*\\?displaystyle\s*', '', latex)
    latex = re.sub(r'\}$', '', latex)
    try:
        expr = parse_latex(latex)
        return pretty(expr, use_unicode=True)
    except Exception:
        # If SymPy fails, just compact the raw LaTeX as fallback
        return _compact(latex)


def clean_wiki_math(text: str) -> str:
    # Pass 1: Parentheses with LaTeX inside
    paren_pat = re.compile(
        r'\((?:(?!\)).)*?\{\s*\\?displaystyle.*?\)', re.DOTALL)

    def _fix_paren(m: re.Match) -> str:
        chunk = m.group(0)
        disp = re.search(r'\{\s*\\?displaystyle.*?\}', chunk, re.DOTALL)
        if not disp:
            return _compact(chunk)
        lead = chunk[:disp.start()]
        latex = disp.group(0)
        tail = chunk[disp.end():]

        dbl = re.search(r'\n\s*\n', lead)
        if dbl:
            lead = lead[:dbl.start()]

        lead = _compact(lead)
        latex = latex_to_ascii(latex)
        tail = _compact(tail)

        out = f"{lead} {latex}{tail}"
        out = out.strip()
        if not out.startswith('('):
            out = '(' + out
        if not out.endswith(')'):
            out = out + ')'
        return out

    text = paren_pat.sub(_fix_paren, text)

    # Pass 2: Standalone LaTeX blocks
    disp_pat = re.compile(r'\{\s*\\?displaystyle.*?\}', re.DOTALL)
    parts = []
    last = 0
    for m in disp_pat.finditer(text):
        s, e = m.span()
        b = text.rfind('\n\n', 0, s)
        b = (b + 2) if b != -1 else last
        pre = text[b:s]

        parts.append(text[last:b])

        if 0 < len(pre.strip()) < 800 and _looks_like_stacked_ascii(pre):
            pass
        else:
            parts.append(_compact(pre))

        parts.append(' ' + latex_to_ascii(m.group(0)))
        last = e

    parts.append(text[last:])
    return ''.join(parts)


# Example usage
articles = [
    "Acceleration", "Angular_acceleration", "Angular_frequency", "Angular_momentum",
    "Angular_velocity", "Center_of_mass", "Centrifugal_force", "Centripetal_force",
    "Circular_motion", "Coriolis_force", "Equations_of_motion", "Force", "Frequency",
    "Harmonic_oscillator", "Jerk_(physics)", "Mass", "Moment_of_inertia", "Momentum",
    "Motion", r"Newton's_laws_of_motion", "Rotation", "Speed", "Torque", "Velocity", "Work_(physics)"
]

for article in articles:
    with open(f"wikipedia_articles/{article}.txt", "r", encoding="utf-8") as file:
        cleaned = clean_wiki_math(file.read())
    with open(f"data/cleaned_articles/{article}.txt", "w", encoding="utf-8") as cleaned_file:
        cleaned_file.write(cleaned)
