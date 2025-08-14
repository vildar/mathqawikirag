import re

# Helper: compact spaces inside a tiny chunk (no paragraph shaping!)


def _compact(s: str) -> str:
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\s+([,.;:])', r'\1', s)         # no space before punctuation
    # no space right after opening bracket
    s = re.sub(r'([(\[{])\s+', r'\1', s)
    # no space right before closing bracket
    s = re.sub(r'\s+([)\]}])', r'\1', s)
    return s.strip()


# Heuristic: does a block look like the stacked ASCII “formula” (lots of newlines, only mathy chars)?
_MATHY_CHARS = r'[\s\w\-=+\/*^.,;:⋅ΔδμνπθλωΩαβγ¯]'


def _looks_like_stacked_ascii(block: str) -> bool:
    b = block.strip()
    if not b or b.count('\n') < 2:
        return False
    return re.fullmatch(_MATHY_CHARS + r'+', b, flags=re.UNICODE) is not None


def clean_wiki_math(text: str) -> str:
    # --- Pass 1: Parentheses that contain a {\displaystyle ...} block ---
    # Keep the short inline text at the start of the parentheses, drop any stacked ASCII in-between,
    # and compact the LaTeX block + trailing bits.
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

        # In the lead, keep only the part before any blank-line block (that’s where the stacked ASCII begins)
        dbl = re.search(r'\n\s*\n', lead)
        if dbl:
            lead = lead[:dbl.start()]

        lead = _compact(lead)
        latex = _compact(latex)
        tail = _compact(tail)

        out = f"{lead} {latex}{tail}"
        out = out.strip()
        if not out.startswith('('):
            out = '(' + out
        if not out.endswith(')'):
            out = out + ')'
        return out

    text = paren_pat.sub(_fix_paren, text)

    # --- Pass 2: Standalone LaTeX blocks. Optionally drop a stacked ASCII block right before them. ---
    disp_pat = re.compile(r'\{\s*\\?displaystyle.*?\}', re.DOTALL)
    parts = []
    last = 0
    for m in disp_pat.finditer(text):
        s, e = m.span()
        # previous paragraph boundary
        b = text.rfind('\n\n', 0, s)
        b = (b + 2) if b != -1 else last
        pre = text[b:s]

        parts.append(text[last:b])

        if 0 < len(pre.strip()) < 800 and _looks_like_stacked_ascii(pre):
            # Drop the stacked ASCII entirely
            pass
        else:
            # Keep prose or non-stacked content, but compact it lightly
            parts.append(_compact(pre))

        # Always compact inside the LaTeX block
        parts.append(' ' + _compact(m.group(0)))
        last = e

    parts.append(text[last:])
    return ''.join(parts)


articles = [
    "Acceleration", "Angular_acceleration", "Angular_frequency", "Angular_momentum",
    "Angular_velocity", "Center_of_mass", "Centrifugal_force", "Centripetal_force",
    "Circular_motion", "Coriolis_force", "Equations_of_motion", "Force", "Frequency",
    "Harmonic_oscillator", "Jerk_(physics)", "Mass", "Moment_of_inertia", "Momentum",
    "Motion", "Newton's_laws_of_motion", "Rotation", "Speed", "Torque", "Velocity", "Work_(physics)"
]

for article in articles:
    with open(f"wikipedia_articles/{article}.txt", "r") as file:
        cleaned = clean_wiki_math(file.read())
        with open(f"data/cleaned_articles/{article}.txt", "w") as cleaned_file:
            cleaned_file.write(cleaned)
