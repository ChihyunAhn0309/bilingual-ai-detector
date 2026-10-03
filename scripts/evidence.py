"""Anchor a whole-document evidence ledger to unchanged UTF-8 text and render local HTML."""
import argparse
from html import escape
import json
from pathlib import Path
import re
import sys

from detector import read_text, text_hash, ensure_new_output, write_json, valid_probability

DIMENSIONS = ("structure", "reasoning_specificity", "voice_consistency", "rhythm_repetition",
              "language_features", "citations_provenance")
DIMENSION_LABELS = dict(zip(DIMENSIONS, ("구조와 전개", "논증과 구체성", "목소리의 일관성",
                                      "리듬과 반복", "언어별 특성", "출처와 작성 이력")))


def paragraphs(text):
    spans = []
    cursor = 0
    for m in list(re.finditer(r"(?:\r?\n)[ \t]*(?:\r?\n)+", text)) + [None]:
        end = m.start() if m else len(text)
        start = cursor
        while start < end and text[start].isspace():
            start += 1
        while end > start and text[end - 1].isspace():
            end -= 1
        if start < end:
            spans.append({"id": f"P{len(spans)+1}", "start": start, "end": end,
                          "line": text.count("\n", 0, start) + 1, "text": text[start:end]})
        cursor = m.end() if m else len(text)
    return spans


def anchor(text, start, end, quote):
    if type(start) is not int or type(end) is not int or not 0 <= start < end <= len(text):
        raise ValueError("Span requires valid zero-based Unicode codepoint [start,end) offsets")
    if not isinstance(quote, str) or text[start:end] != quote:
        raise ValueError("Quoted evidence does not exactly match original at its offsets")
    return {"start": start, "end": end, "quote": quote,
            "line": text.count("\n", 0, start) + 1,
            "column": start - text.rfind("\n", 0, start),
            "paragraph_ids": [p["id"] for p in paragraphs(text) if p["start"] < end and start < p["end"]]}


def unique_match(text, quote):
    if not isinstance(quote, str) or not quote:
        return {"mapping": "unavailable"}
    first = text.find(quote)
    if first < 0:
        return {"mapping": "not_found"}
    if text.find(quote, first + 1) >= 0:
        return {"mapping": "ambiguous_repeated_quote"}
    return {"mapping": "exact_unique_match", **anchor(text, first, first + len(quote), quote)}


def provider_highlights(text, raw):
    docs = raw.get("documents") if isinstance(raw, dict) else None
    if not isinstance(docs, list) or len(docs) != 1 or not isinstance(docs[0], dict):
        raise ValueError("Expected exactly one GPTZero document")
    sentences = docs[0].get("sentences", [])
    if not isinstance(sentences, list):
        raise ValueError("Invalid sentences list")
    result = []
    for i, sentence in enumerate(sentences):
        if not isinstance(sentence, dict):
            raise ValueError("Invalid sentence entry")
        quote = sentence.get("sentence", sentence.get("text"))
        score = sentence.get("generated_prob")
        if score is not None and not valid_probability(score):
            raise ValueError("Invalid provider sentence score")
        result.append({"provider_sentence_index": i, "provider_sentence_text": quote,
                       "provider_generated_prob": score,
                       "provider_highlight_sentence_for_ai": sentence.get("highlight_sentence_for_ai"),
                       **unique_match(text, quote)})
    return {"text_sha256": text_hash(text), "input_binding": "unverified_import",
            "interpretation": "Exact quote matches locate reported sentences; they do not authenticate a scan or explain its internal features.",
            "sentences": result}


def require_string(obj, key):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Missing nonempty field: {key}")
    return value


def validate_ledger(text, ledger):
    if not isinstance(ledger, dict) or ledger.get("text_sha256") != text_hash(text):
        raise ValueError("Ledger text hash does not match the unchanged original")
    ps = paragraphs(text)
    ids, checked = set(), []
    findings = ledger.get("findings", [])
    if not isinstance(findings, list):
        raise ValueError("findings must be a list")
    for item in findings:
        if not isinstance(item, dict):
            raise ValueError("Finding must be an object")
        fid = require_string(item, "id")
        if fid in ids:
            raise ValueError("Duplicate finding id")
        ids.add(fid)
        if item.get("basis") not in ("style_observation", "provider_highlight", "local_occlusion", "local_feature_contribution", "documented_history"):
            raise ValueError("Unknown evidence basis")
        if item.get("direction") not in ("ai_like", "human_compatible", "neutral"):
            raise ValueError("Unknown evidence direction")
        if item.get("strength") not in ("weak", "moderate", "strong"):
            raise ValueError("Strength must be qualitative")
        for field in ("observation", "interpretation", "human_alternative", "discriminating_evidence"):
            require_string(item, field)
        if item["basis"] != "style_observation":
            require_string(item, "source_record")
        spans = item.get("spans")
        if not isinstance(spans, list) or not spans:
            raise ValueError("Every finding needs at least one exact source span")
        checked.append({**item, "spans": [anchor(text, s.get("start"), s.get("end"), s.get("quote")) for s in spans]})
    supplied_reviews = ledger.get("paragraph_reviews", [])
    if not isinstance(supplied_reviews, list):
        raise ValueError("paragraph_reviews must be a list")
    reviews = {}
    for review in supplied_reviews:
        pid = review.get("paragraph_id")
        if pid in reviews or pid not in {p["id"] for p in ps}:
            raise ValueError("Duplicate or unknown paragraph id")
        if review.get("status") not in ("reviewed", "excluded", "not_reviewed"):
            raise ValueError("Invalid paragraph review status")
        require_string(review, "assessment")
        links = review.get("finding_ids", [])
        if not isinstance(links, list) or not all(fid in ids for fid in links):
            raise ValueError("Paragraph links to an unknown finding")
        for fid in links:
            f = next(f for f in checked if f["id"] == fid)
            if not any(pid in s["paragraph_ids"] for s in f["spans"]):
                raise ValueError("Paragraph finding does not overlap that paragraph")
        # A ledger may describe the source, but cannot override indexed source coordinates/text.
        reviews[pid] = {key: review[key] for key in ("paragraph_id", "status", "assessment")}
        reviews[pid]["finding_ids"] = links
    dimensions = ledger.get("document_analysis", {})
    if not isinstance(dimensions, dict):
        raise ValueError("document_analysis must be an object")
    document_analysis = {}
    for name in DIMENSIONS:
        value = dimensions.get(name, "Not assessed / 미검토")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Document analysis entries must be nonempty strings")
        document_analysis[name] = value
    full_reviews = [{**p, **reviews.get(p["id"], {"paragraph_id": p["id"], "status": "not_reviewed",
                      "assessment": "Not reviewed / 미검토", "finding_ids": []})} for p in ps]
    reviewed = sum(r["status"] == "reviewed" for r in full_reviews)
    return {"schema_version": 2, "mode": "anchored_explanation", "text_sha256": text_hash(text),
            "offset_unit": "zero_based_unicode_codepoints_end_exclusive",
            "summary": require_string(ledger, "summary"), "document_analysis": document_analysis,
            "findings": checked, "paragraph_reviews": full_reviews,
            "coverage": {"paragraphs_total": len(ps), "paragraphs_reviewed": reviewed,
                         "paragraphs_excluded": sum(r["status"] == "excluded" for r in full_reviews),
                         "review_fraction": reviewed / len(ps) if ps else None},
            "authorship_probabilities": None,
            "validation_scope": "Exact quotes, hashes, locations, fields and review coverage. Semantic truth and authorship are not validated."}


def attach_model_result(text, report, result):
    if not isinstance(result, dict) or result.get("text_sha256") != text_hash(text):
        raise ValueError("Model result is not bound to this exact original text")
    mode = result.get("mode")
    if mode == "offline_korean_calibrated_classifier":
        probs = result.get("class_probabilities")
        labels = {"human", "ai"}
    elif mode == "offline_local_model":
        probs = result.get("document_class_probabilities")
        labels = {"human", "ai", "ai_edited", "humanized"}
        if probs is None:
            raise ValueError("Multi-window English scores cannot be attached as a whole-document probability")
    else:
        raise ValueError("Only the supported local model records can be attached automatically")
    if (not isinstance(probs, dict) or set(probs) != labels
            or not all(valid_probability(v) for v in probs.values()) or abs(sum(probs.values())-1) > 1e-4):
        raise ValueError("Invalid model class probabilities")
    report["measured_output"] = {"mode": mode, "model": result.get("model_id", result.get("model")),
        "measured_at_utc": result.get("measured_at_utc"),
        "class_probabilities": probs, "model_sha256": result.get("model_sha256", result.get("weight_sha256")),
        "calibration": result.get("calibration"), "applicability_cautions": result.get("applicability_cautions", []),
        "revision": result.get("revision"), "language_scope": result.get("language_scope"),
        "independently_calibrated_here": result.get("independently_calibrated_here"),
        "validation_status": result.get("validation_status"),
        "known_limitations": result.get("known_limitations", result.get("known_limits", [])),
        "semantics": "Model-estimated class probabilities, not verified writing history; exact input hash matched."}
    return report


def render_html(text, report):
    e = lambda value: escape(str(value), quote=True)
    colors = {"ai_like": "suspect", "human_compatible": "counter", "neutral": "neutral"}
    status_labels = {"reviewed": "검토 완료", "excluded": "검토 제외", "not_reviewed": "미검토"}
    basis_labels = {"style_observation": "문체 관찰", "provider_highlight": "제공된 탐지기 표시",
                    "local_occlusion": "로컬 모델 삭제 실험", "local_feature_contribution": "학습된 모델 특징 기여도",
                    "documented_history": "작성 이력 자료"}
    strength_labels = {"weak": "약함", "moderate": "중간", "strong": "강함"}
    blocks = []
    for p in report["paragraph_reviews"]:
        spans = [(s, f) for f in report["findings"] for s in f["spans"]
                 if s["start"] < p["end"] and p["start"] < s["end"]]
        bounds = sorted({p["start"], p["end"]} | {max(p["start"], s["start"]) for s, _ in spans}
                        | {min(p["end"], s["end"]) for s, _ in spans})
        marked = []
        for start, end in zip(bounds, bounds[1:]):
            matches = [f for s, f in spans if s["start"] < end and start < s["end"]]
            segment = e(text[start:end])
            if matches:
                directions = {f["direction"] for f in matches}
                cls = colors[next(iter(directions))] if len(directions) == 1 else "neutral"
                links = " · ".join(f["id"] for f in matches)
                segment = f'<mark class="{cls}" title="{e(links)}">{segment}</mark>'
            marked.append(segment)
        links = " ".join(f'<a href="#f-{e(fid)}">{e(fid)}</a>' for fid in p["finding_ids"])
        blocks.append(f'<article><h3>{e(p["id"])} · {p["line"]}행 · {status_labels[p["status"]]}</h3>'
                      f'<div class="original">{"".join(marked)}</div><p>{e(p["assessment"])} {links}</p></article>')
    details = []
    labels = [("observation", "관찰"), ("interpretation", "판단 이유"),
              ("human_alternative", "사람 글에서도 가능한 이유"), ("discriminating_evidence", "구별에 필요한 근거")]
    for f in report["findings"]:
        quotes = "".join(f'<blockquote>{s["line"]}행 {s["column"]}열: {e(s["quote"])}</blockquote>' for s in f["spans"])
        fields = "".join(f'<p><b>{label}</b> {e(f[key])}</p>' for key, label in labels)
        if f.get("source_record"):
            fields += f'<p><b>측정·출처 기록</b> {e(f["source_record"])}</p>'
        details.append(f'<article id="f-{e(f["id"])}"><h3>{e(f["id"])} · {basis_labels[f["basis"]]} · {strength_labels[f["strength"]]}</h3>{quotes}{fields}</article>')
    dimensions = "".join(f'<p><b>{e(DIMENSION_LABELS[k])}</b> {e(v)}</p>' for k, v in report["document_analysis"].items())
    measured = report.get("measured_output")
    measurement_html = '<p>AI/사람 분류 확률: 실제 모델 결과가 첨부되지 않음</p>'
    if measured:
        label_names = {"human": "사람", "ai": "AI", "ai_edited": "AI 교정", "humanized": "Humanized"}
        values = " · ".join(f'{label_names[k]} {v*100:.1f}%' for k,v in measured["class_probabilities"].items())
        measurement_html = f'<article><h2>모델이 추정한 분류 확률</h2><p><b>{values}</b></p><p>{e(measured["model"])}</p>'
        if measured["mode"] == "offline_local_model":
            measurement_html += '<p>영어 모델의 보정되지 않은 실험용 보조 점수입니다. 공개 36문서 pilot에서 사람 글 12개 중 3개를 오탐했으며, 높은 점수도 작성 이력을 보장하지 않습니다.</p>'
        elif measured.get("calibration"):
            measurement_html += '<p>별도 데이터로 보정한 값입니다. 기준 분포는 AI/사람 각 50%이며, 실제 작성 이력을 확정하는 확률은 아닙니다.</p>'
        for caution in measured.get("applicability_cautions", []):
            translated = {
                "Input length is outside the training 5th–95th percentile; probability reliability may differ.": "입력 길이가 학습 자료의 가운데 90% 범위를 벗어납니다. 이 길이에서는 확률 신뢰도가 달라질 수 있습니다.",
                "Genre is not explicitly within the evaluated essay/abstract/poetry scope; treat the numeric result as an extrapolation.": "평가한 에세이·초록·시 장르로 지정되지 않았습니다. 이 숫자는 검증 범위를 벗어난 추정입니다.",
                "Learned character-pattern coverage is below the training reference range.": "학습된 문자 패턴이 입력을 설명하는 비중이 학습 기준보다 낮습니다."
            }.get(caution, caution)
            measurement_html += f'<p>{e(translated)}</p>'
        measurement_html += '<p>문체 관찰, 모델 특징 기여도, 문단 삭제에 따른 점수 변화는 서로 다른 근거입니다. 숫자와 하이라이트는 작성 이력을 인증하지 않습니다.</p>'
        measurement_html += '</article>'
    return ('<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">'
            '<title>문서 근거 분석</title><style>body{max-width:1100px;margin:40px auto;padding:0 24px;background:#f7f7f4;'
            'color:#172b35;font:16px/1.7 system-ui;overflow-wrap:anywhere}article{background:white;padding:18px 24px;margin:18px 0;border:1px solid #ddd;'
            'border-radius:10px}.original{white-space:pre-wrap;overflow-wrap:anywhere}.suspect{background:#ffe0a3}'
            '.counter{background:#c9e8fa}.neutral{background:#e1e1e1}blockquote{border-left:3px solid #8c9da5;padding-left:16px;'
            'white-space:pre-wrap}h1,h2,h3{line-height:1.4}a{color:#245a96}</style><body>'
            '<h1>원문 전체 분석 · Evidence review</h1><p>노랑: AI 유사 관찰 · 파랑: 반대 근거 · 회색: 중립 관찰. 색은 작성 확률이 아닙니다.</p>'
            f'<p>{e(report["summary"])}</p><p>검토 문단: {report["coverage"]["paragraphs_reviewed"]} / '
            f'{report["coverage"]["paragraphs_total"]}</p>{measurement_html}'
            f'<h2>글 전반</h2>{dimensions}<h2>원문과 문단별 판단</h2>{"".join(blocks)}'
            f'<h2>구체적 근거와 대안 설명</h2>{"".join(details)}<p>SHA256: {e(report["text_sha256"])}</p></body></html>')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index"); index.add_argument("text"); index.add_argument("--out")
    val = sub.add_parser("validate"); val.add_argument("text"); val.add_argument("ledger")
    val.add_argument("--out"); val.add_argument("--html"); val.add_argument("--model-result")
    imp = sub.add_parser("import-highlights"); imp.add_argument("text"); imp.add_argument("response"); imp.add_argument("--out")
    args = parser.parse_args(argv)
    try:
        inputs = [args.text] + [getattr(args, k) for k in ("ledger", "response") if hasattr(args, k)]
        if getattr(args, "model_result", None):
            inputs.append(args.model_result)
        ensure_new_output(args.out, inputs)
        html_path = getattr(args, "html", None)
        if html_path:
            ensure_new_output(html_path, inputs + ([args.out] if args.out else []))
        text, _ = read_text(args.text)
        if args.command == "index":
            result = {"text_sha256": text_hash(text), "paragraphs": paragraphs(text)}
        elif args.command == "import-highlights":
            result = provider_highlights(text, json.loads(Path(args.response).read_text(encoding="utf-8-sig")))
        else:
            result = validate_ledger(text, json.loads(Path(args.ledger).read_text(encoding="utf-8-sig")))
            if args.model_result:
                result = attach_model_result(text, result, json.loads(Path(args.model_result).read_text(encoding="utf-8-sig")))
        if html_path:
            with Path(html_path).open("x", encoding="utf-8") as out:
                out.write(render_html(text, result))
        write_json(result, args.out)
        return 0
    except (ValueError, OSError, UnicodeError, TypeError, AttributeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
