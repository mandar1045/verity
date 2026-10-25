from __future__ import annotations

import socket

import pytest

from backend.app.services.links import extract_links, inspect_links, levenshtein


def verdict(text: str) -> tuple[str, str, str | None]:
    found = inspect_links(text)
    assert found, f"no link found in {text!r}"
    f = found[0].finding
    return f.verdict, f.domain, f.lookalike_of


@pytest.mark.parametrize(
    ("text", "expected", "domain"),
    [
        ("Check https://vtop.vit.ac.in/exams", "OK", "vtop.vit.ac.in"),
        ("Visit www.onlinesbi.sbi for netbanking", "OK", "www.onlinesbi.sbi"),
        ("Update KYC at sbi-kyc-verify.xyz/update", "DANGEROUS", "sbi-kyc-verify.xyz"),
        ("Login at http://vit-ac.in/login", "DANGEROUS", "vit-ac.in"),
        ("Go to hxxp://paytm-cashback[.]online now", "DANGEROUS", "paytm-cashback.online"),
        ("Open http://103.21.44.9/upi", "DANGEROUS", "103.21.44.9"),
        ("Visit https://xn--sbi-yqa.com", "DANGEROUS", "xn--sbi-yqa.com"),
        ("Claim at bit.ly/3xYzA1", "SUSPICIOUS", "bit.ly"),
        ("Offers at https://mega-deals.top/today", "SUSPICIOUS", "mega-deals.top"),
        ("See https://a8f3k2j9x7q1w5e4r6t8y0.example.com", "SUSPICIOUS", "a8f3k2j9x7q1w5e4r6t8y0.example.com"),
        ("Login https://sbi.co.in.secure-login.top", "DANGEROUS", "sbi.co.in.secure-login.top"),
        ("[https://hdfcbank.com](https://hdfc-verify.click/x)", "DANGEROUS", "hdfc-verify.click"),
    ],
)
def test_link_verdicts(text: str, expected: str, domain: str) -> None:
    v, d, _ = verdict(text)
    assert (v, d) == (expected, domain)


def test_lookalike_target_is_reported() -> None:
    assert verdict("Login at https://hdfcbnk.com")[2] == "hdfcbank.com"


def test_html_anchor_display_mismatch() -> None:
    f = inspect_links('<a href="http://refund-help.icu/x">www.icicibank.com</a>')[0].finding
    assert f.verdict == "DANGEROUS"
    assert any("actually opens" in r for r in f.reasons)


def test_vpa_and_email_are_not_links() -> None:
    assert extract_links("Pay to canteen@upi or mail exam.cell@vit.ac.in or pay.me@ybl") == []


def test_amounts_and_abbreviations_are_not_links() -> None:
    assert extract_links("Rs.500 debited from a/c no. 1234 on 24.10.2026, e.g. canteen") == []


def test_every_verdict_has_reasons() -> None:
    for lk in inspect_links("a.com bit.ly/x sbi-help.xyz https://vit.ac.in"):
        assert lk.finding.reasons


def test_no_network_access(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_: object, **__: object) -> None:
        raise AssertionError("link inspector tried to use the network")

    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    inspect_links("Visit https://totally-new-domain-xyz.top and sbi-kyc.xyz")


def test_levenshtein() -> None:
    assert levenshtein("vit-ac.in", "vit.ac.in") == 1
    assert levenshtein("kitten", "sitting") == 3
