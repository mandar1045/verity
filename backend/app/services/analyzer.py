"""Message analysis pipeline: links -> rules -> model -> fusion -> explanation."""

from __future__ import annotations

import re
import unicodedata
import uuid

from backend.app.services.explain import explain_message
from backend.app.services.links import inspect_links
from backend.app.services.polish import polish
from backend.app.services.registry import Registry
from backend.app.services.rules import Hit, RuleContext, build_signal, infer_scam_type, rule_score, run_rules
from backend.app.services.scoring import score_message
from contracts.schemas import AnalyzeMessageRequest, MessageAnalysis, Signal, label_for

MODEL_SIGNAL_MIN_PROB = 0.5
TYPE_MIN_CONFIDENCE = 0.45
MAX_MODEL_EVIDENCE = 4


def _is_word_char(ch: str) -> bool:
    return ch.isalnum() or unicodedata.category(ch) in ("Mn", "Mc") or ch in "'’-"


def _expand(text: str, start: int, end: int) -> tuple[int, int]:
    """Grow a char n-gram match to whole words so the highlight reads naturally."""
    while start > 0 and _is_word_char(text[start - 1]):
        start -= 1
    while end < len(text) and _is_word_char(text[end]):
        end += 1
    while start < end and not _is_word_char(text[start]):
        start += 1
    while end > start and not _is_word_char(text[end - 1]):
        end -= 1
    return start, end


def model_text_signal(ctx: RuleContext, prob: float, ngrams: list[dict[str, object]]) -> Signal | None:
    """Evidence = the model's top n-grams found in the text (links excluded: the link inspector owns them)."""
    if prob < MODEL_SIGNAL_MIN_PROB:
        return None
    links = [(lk.start, lk.end) for lk in ctx.links]
    hits: list[Hit] = []
    for g in ngrams:
        m = re.search(re.escape(str(g["ngram"])), ctx.text, re.I)
        if not m:
            continue
        s, e = _expand(ctx.text, m.start(), m.end())
        in_link = any(ls <= s < le for ls, le in links)
        if e > s and not in_link and not any(h.start <= s < h.end or s <= h.start < e for h in hits):
            hits.append(Hit(s, e, ctx.text[s:e], prob))
        if len(hits) == MAX_MODEL_EVIDENCE:
            break
    return build_signal("MODEL_TEXT", prob, hits, ctx) if hits else None


def _scam_type(reg: Registry, text: str, signals: list[Signal]) -> str | None:
    rule_type = infer_scam_type(text, signals)
    if reg.message_model is None:
        return rule_type
    model_type, confidence = reg.message_model.scam_type(text)
    return model_type if confidence >= TYPE_MIN_CONFIDENCE or rule_type is None else rule_type


def analyze_message(req: AnalyzeMessageRequest, reg: Registry) -> MessageAnalysis:
    links = inspect_links(req.text)
    ctx = RuleContext(req.text, req.channel, req.sender, links, req.lang_out)
    signals = run_rules(ctx)
    r_score = rule_score(signals)
    prob: float | None = None
    if reg.message_model is not None:
        pred = reg.message_model.predict(req.text)
        prob = pred["prob"]
        mt = model_text_signal(ctx, prob, pred["top_ngrams"])
        if mt:
            signals.append(mt)
    findings = [lk.finding for lk in links]
    score = score_message(prob, r_score, signals, findings, reg.fusion)
    label = label_for(score)
    scam_type = _scam_type(reg, req.text, signals) if label != "SAFE" else None
    explanation, steps = explain_message(label, signals, scam_type, req.lang_out)
    source = "template"
    if req.polish:
        explanation, source = polish(explanation, [s.title for s in signals], req.lang_out)
    return MessageAnalysis(
        id=uuid.uuid4(), risk_score=score, label=label, scam_type=scam_type,
        model_prob=round(prob or 0.0, 4), rule_score=r_score,
        signals=sorted(signals, key=lambda s: (s.code == "MODEL_TEXT", -s.weight)), links=findings,
        explanation=explanation, next_steps=steps, explanation_source=source,  # type: ignore[arg-type]
    )
