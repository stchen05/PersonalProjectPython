from pathlib import Path
import re
import numpy as np


def _num_with_suffix_to_float(s: str) -> float:
    """Convert a numeric string with optional k/M suffix to float.

    Examples:
    - '1.2k' -> 1200.0
    - '3M' -> 3000000.0
    - '500' -> 500.0
    """
    if not isinstance(s, str):
        return np.nan
    s = s.strip()
    if s == "":
        return np.nan
    m = re.match(r"^([0-9]*\.?[0-9]+)\s*([kKmM]?)$", s)
    if not m:
        try:
            return float(s)
        except Exception:
            return np.nan
    num = float(m.group(1))
    suf = m.group(2).lower()
    if suf == 'k':
        num *= 1_000
    elif suf == 'm':
        num *= 1_000_000
    return num


def parse_price(s: str) -> float:
    """Parse a price string into a float USD-equivalent (best-effort).

    - Handles commas and $ signs
    - Handles ranges like "$12,000-$15,000" by returning the midpoint
    - Handles shorthand suffixes like 'k' and 'M'
    - Returns numpy.nan on failure
    """
    if not isinstance(s, str):
        return np.nan
    s = s.strip()
    if s == "":
        return np.nan

    # remove common currency symbols but keep digits, dots, minus and suffix letters
    s_clean = re.sub(r"[,\$£€]", "", s)

    # If range separated by '-', try to parse endpoints
    if '-' in s_clean:
        parts = [p.strip() for p in s_clean.split('-') if p.strip() != ""]
        vals = []
        for p in parts:
            # extract first token that looks like a number with optional suffix
            m = re.search(r"([0-9]*\.?[0-9]+\s*[kKmM]?)", p)
            if m:
                vals.append(_num_with_suffix_to_float(m.group(1).replace(' ', '')))
        if vals:
            return float(sum(vals) / len(vals))
        return np.nan

    # otherwise extract first numeric token (with optional suffix)
    m = re.search(r"([0-9]*\.?[0-9]+\s*[kKmM]?)", s_clean)
    if not m:
        return np.nan
    return float(_num_with_suffix_to_float(m.group(1).replace(' ', '')))


def extract_number(s: str) -> float:
    """Extract numeric value(s) from a string and return their mean.

    Handles numbers with commas and optional k/M suffixes. If no numeric
    content is found returns np.nan.
    """
    if not isinstance(s, str):
        return np.nan
    s = s.strip()
    if s == "":
        return np.nan

    # remove commas
    s_no_comma = s.replace(',', ' ')
    # find all numeric tokens possibly with k/M suffix
    matches = re.findall(r"([0-9]*\.?[0-9]+\s*[kKmM]?)", s_no_comma)
    if not matches:
        return np.nan
    vals = []
    for tok in matches:
        v = _num_with_suffix_to_float(tok.replace(' ', ''))
        if not np.isnan(v):
            vals.append(v)
    if not vals:
        return np.nan
    return float(sum(vals) / len(vals))
