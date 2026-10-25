"""Link inspector. Extracts URLs from text and judges them.

Hard rule: this module NEVER fetches, opens or resolves a URL. It only parses
strings. tldextract runs in offline mode against its bundled suffix list.
"""

from __future__ import annotations

import ipaddress
import re
from dataclasses import dataclass, field
from functools import lru_cache

import tldextract

from contracts.schemas import LinkFinding

_EXTRACT = tldextract.TLDExtract(suffix_list_urls=(), cache_dir=None)

ALLOWLIST: tuple[str, ...] = (
    "vit.ac.in", "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "npci.org.in", "bhimupi.org.in", "paytm.com", "phonepe.com",
    "pay.google.com", "gov.in",
)
# Other official domains that legit messages use. Treated like the allowlist.
KNOWN_OFFICIAL: tuple[str, ...] = (
    "rbi.org.in", "amazon.in", "amazon.com", "flipkart.com", "irctc.co.in", "swiggy.com",
    "zomato.com", "myntra.com", "airtel.in", "jio.com", "kotak.com",
    "bluedart.com", "delhivery.com", "bescom.co.in", "google.com", "youtube.com",
)
BRANDS: dict[str, tuple[str, ...]] = {
    "sbi": ("sbi.co.in", "onlinesbi.sbi"), "hdfc": ("hdfcbank.com",),
    "icici": ("icicibank.com",), "axis": ("axisbank.com",), "npci": ("npci.org.in",),
    "bhim": ("bhimupi.org.in",), "upi": ("npci.org.in", "bhimupi.org.in"),
    "paytm": ("paytm.com",), "phonepe": ("phonepe.com",), "gpay": ("pay.google.com",),
    "googlepay": ("pay.google.com",), "vit": ("vit.ac.in",), "vtop": ("vit.ac.in",),
    "rbi": ("rbi.org.in",), "amazon": ("amazon.in",), "flipkart": ("flipkart.com",),
    "irctc": ("irctc.co.in",), "kyc": ("gov.in",), "aadhaar": ("uidai.gov.in",),
    "incometax": ("incometax.gov.in",), "kotak": ("kotak.com",),
}
SHORTENERS = frozenset({
    "bit.ly", "bitly.com", "tinyurl.com", "t.co", "goo.gl", "is.gd", "cutt.ly",
    "rb.gy", "shorturl.at", "tiny.cc", "ow.ly", "s.id", "rebrand.ly", "t.ly",
    "v.gd", "shorte.st", "bit.do", "tinu.be",
})
RISKY_TLDS = frozenset({
    "xyz", "top", "click", "icu", "buzz", "online", "link", "live", "site",
    "shop", "club", "rest", "cfd", "sbs", "info", "work", "support", "help",
})
COMMON_TLDS = frozenset({
    "com", "in", "net", "org", "co", "io", "me", "ly", "gl", "gd", "at", "cc",
    "id", "be", "do", "app", "dev", "ai", "us", "uk", "edu", "gov", "sbi",
})

_SCHEME_URL = re.compile(r"\b(?:h(?:tt|xx)ps?|ftp)\s*(?::|\[:\])//(?:\[\.\]|\(\.\)|\[dot\]|[^\s<>\"'\)\]])+", re.I)
_LABEL = r"[a-z0-9¡-￿](?:[a-z0-9¡-￿-]{0,61}[a-z0-9¡-￿])?"
_DOT = r"(?:\.|\[\.\]|\(\.\)|\[dot\])"
_BARE_URL = re.compile(
    rf"(?<![@\w.\-/])(?:{_LABEL}{_DOT})+(?:[a-z]{{2,24}}|xn--[a-z0-9-]+)(?::\d{{2,5}})?(?:/[^\s<>\"']*)?",
    re.I,
)
_MD_LINK = re.compile(r"\[([^\]\n]{1,200})\]\(([^)\s]{4,500})\)")
_HTML_LINK = re.compile(r"<a\s[^>]*?href\s*=\s*[\"']([^\"']{4,500})[\"'][^>]*>(.*?)</a>", re.I | re.S)
_TRAILING = ".,;:!?)]}'\"…।"


@dataclass
class LinkSpan:
    raw: str
    start: int
    end: int
    display: str | None = None


@dataclass
class LinkResult:
    finding: LinkFinding
    start: int
    end: int
    kinds: set[str] = field(default_factory=set)  # lookalike | danger | shortener | suspicious


def deobfuscate(raw: str) -> str:
    s = re.sub(r"^hxxp", "http", raw.strip(), flags=re.I)
    s = re.sub(r"\[\.\]|\(\.\)|\[dot\]", ".", s, flags=re.I)
    return s.replace("[:]", ":")


def _overlaps(start: int, end: int, taken: list[tuple[int, int]]) -> bool:
    return any(start < e and end > s for s, e in taken)


def _strip_trailing(text: str, start: int, end: int) -> int:
    while end > start and text[end - 1] in _TRAILING:
        end -= 1
    return end


def extract_links(text: str) -> list[LinkSpan]:
    """Find URLs (with or without scheme, obfuscated, markdown or HTML anchors)."""
    spans: list[LinkSpan] = []
    taken: list[tuple[int, int]] = []
    for m in _MD_LINK.finditer(text):
        spans.append(LinkSpan(m.group(2), m.start(), m.end(), m.group(1)))
        taken.append((m.start(), m.end()))
    for m in _HTML_LINK.finditer(text):
        display = re.sub(r"<[^>]+>", "", m.group(2)).strip() or None
        spans.append(LinkSpan(m.group(1), m.start(), m.end(), display))
        taken.append((m.start(), m.end()))
    for pattern in (_SCHEME_URL, _BARE_URL):
        for m in pattern.finditer(text):
            end = _strip_trailing(text, m.start(), m.end())
            if end <= m.start() or _overlaps(m.start(), end, taken):
                continue
            raw = text[m.start():end]
            if end < len(text) and text[end] == "@":
                continue  # an email address or UPI handle, not a link
            if pattern is _BARE_URL and not _plausible_bare(raw):
                continue
            spans.append(LinkSpan(raw, m.start(), end))
            taken.append((m.start(), end))
    return sorted(spans, key=lambda s: s.start)


def _plausible_bare(raw: str) -> bool:
    host = host_of(raw)
    ext = _EXTRACT(host)
    if not ext.suffix or not ext.domain:
        return False
    last = ext.suffix.rsplit(".", 1)[-1]
    return host.startswith("www.") or "/" in raw or last in COMMON_TLDS | RISKY_TLDS


def host_of(raw: str) -> str:
    s = deobfuscate(raw)
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", s, flags=re.I)
    s = re.split(r"[/?#]", s, maxsplit=1)[0]
    s = s.rsplit("@", 1)[-1]
    s = re.sub(r":\d+$", "", s)
    return s.strip(".").lower()


def _has_userinfo(raw: str) -> bool:
    s = re.sub(r"^[a-z][a-z0-9+.-]*://", "", deobfuscate(raw), flags=re.I)
    return "@" in re.split(r"[/?#]", s, maxsplit=1)[0]


def _matches(host: str, domain: str) -> bool:
    return host == domain or host.endswith("." + domain)


def official_domain(host: str) -> str | None:
    for d in ALLOWLIST + KNOWN_OFFICIAL:
        if _matches(host, d):
            return d
    return None


def registered(host: str) -> str:
    ext = _EXTRACT(host)
    return f"{ext.domain}.{ext.suffix}" if ext.domain and ext.suffix else host


@lru_cache(maxsize=4096)
def levenshtein(a: str, b: str) -> int:
    if len(a) < len(b):
        a, b = b, a
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def lookalike_target(host: str) -> str | None:
    """Return the official domain this host imitates by spelling, if any."""
    reg = registered(host)
    label = _EXTRACT(host).domain
    for official in ALLOWLIST + KNOWN_OFFICIAL:
        if _matches(host, official):
            return None
        if levenshtein(reg, official) == 1 or levenshtein(host, official) == 1:
            return official
        off_label = _EXTRACT(official).domain
        dist = levenshtein(label, off_label)
        if label != off_label and len(off_label) >= 4 and (dist == 1 or (dist == 2 and len(off_label) >= 6)):
            return official
    return None


def brand_misuse(host: str) -> tuple[str, str] | None:
    """Return (brand, official domain) when a brand name sits inside a non-official host."""
    tokens = [t for t in re.split(r"[.\-_]", host) if t]
    for brand, officials in BRANDS.items():
        for tok in tokens:
            exact = tok == brand or re.fullmatch(rf"{brand}\d+", tok)
            loose = len(brand) >= 5 and brand in tok
            if exact or loose:
                return brand, officials[0]
    return None


def _is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


def _random_subdomain(host: str) -> bool:
    sub = _EXTRACT(host).subdomain
    labels = [lab for lab in sub.split(".") if lab and lab != "www"]
    long_label = any(len(lab) >= 20 or sum(c.isdigit() for c in lab) >= 5 for lab in labels)
    return long_label or len(labels) >= 4


def _display_mismatch(display: str | None, host: str) -> str | None:
    if not display:
        return None
    m = _BARE_URL.search(display) or _SCHEME_URL.search(display)
    if not m:
        return None
    shown = host_of(m.group(0))
    return shown if registered(shown) != registered(host) else None


def _structural_checks(raw: str, host: str, reasons: list[str], kinds: set[str]) -> None:
    if _has_userinfo(raw):
        reasons.append(f"Text before '@' is a disguise. The link really opens {host}.")
        kinds.add("danger")
    if _is_ip(host):
        reasons.append("Points to a raw IP address instead of a named website.")
        kinds.add("danger")
    if "xn--" in host or not host.isascii():
        reasons.append("Uses look-alike foreign characters (punycode) in the address.")
        kinds.add("danger")


def _brand_checks(host: str, reasons: list[str], kinds: set[str]) -> str | None:
    target = lookalike_target(host)
    if target:
        reasons.append(f"Looks like {target} but is spelled differently.")
        kinds.add("lookalike")
    misuse = brand_misuse(host)
    if misuse:
        brand, official = misuse
        reasons.append(f"Uses the name '{brand.upper()}' but is not an official site (official: {official}).")
        kinds.add("lookalike")
        target = target or official
    return target


def _reputation_checks(host: str, reasons: list[str], kinds: set[str]) -> None:
    reg = registered(host)
    tld = reg.rsplit(".", 1)[-1]
    if reg in SHORTENERS or host in SHORTENERS:
        reasons.append("Short link that hides the real destination.")
        kinds.add("shortener")
    if tld in RISKY_TLDS:
        reasons.append(f"'.{tld}' addresses are cheap to register and common in scams.")
        kinds.add("suspicious")
    if _random_subdomain(host):
        reasons.append("Very long or random-looking sub-address.")
        kinds.add("suspicious")


def judge_link(span: LinkSpan) -> LinkResult:
    host = host_of(span.raw)
    reasons: list[str] = []
    kinds: set[str] = set()
    _structural_checks(span.raw, host, reasons, kinds)
    shown = _display_mismatch(span.display, host)
    if shown:
        reasons.append(f"The link text shows {shown} but it actually opens {host}.")
        kinds.add("danger")
    official = official_domain(host) if not kinds else None
    lookalike_of: str | None = None
    if official:
        reasons.append(f"Official domain ({official}).")
    else:
        lookalike_of = _brand_checks(host, reasons, kinds)
        _reputation_checks(host, reasons, kinds)
    if kinds & {"danger", "lookalike"}:
        verdict = "DANGEROUS"
    elif kinds:
        verdict = "SUSPICIOUS"
    else:
        verdict = "OK"
        if not official:
            reasons.append("No known risk pattern, but not an official domain we recognise.")
    finding = LinkFinding(raw=span.raw, domain=host, verdict=verdict, reasons=reasons, lookalike_of=lookalike_of)
    return LinkResult(finding=finding, start=span.start, end=span.end, kinds=kinds)


def inspect_links(text: str) -> list[LinkResult]:
    return [judge_link(s) for s in extract_links(text)]
