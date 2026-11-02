"""Fast tests for the pipeline. Run: python -m pytest -q"""
import hashlib
import textwrap

import yaml

from pipeline import check_cycle, intake_issue, quality_gate, reconcile, triage_questions, validate
from pipeline.common import tokens


def write_manifest(tmp_path, typ, m, files=None):
    d = tmp_path / typ / m["id"]
    d.mkdir(parents=True)
    for name, text in (files or {}).items():
        (d / name).write_text(text, encoding="utf-8")
        m.setdefault("files", []).append({"path": name, "sha256": hashlib.sha256(text.encode()).hexdigest()})
    p = d / "manifest.yaml"
    p.write_text(yaml.safe_dump(m, allow_unicode=True), encoding="utf-8")
    return p, m


BASE = {"id": "SUB-2026-0001", "type": "data", "title": "Example county figures", "submitted_at": "2026-11-02",
        "summary": "EXAMPLE ONLY: fictitious figures used to test the pipeline.", "license": "public-domain",
        "provenance": [{"citation": "Example gazetteer (1990)", "url": "https://example.org/gazetteer", "page_ref": "p. 1"}]}


def test_registries_valid():
    assert validate.validate_registries() == []
    assert validate.validate_csvs() == []


def test_gate_passes_good_data(tmp_path):
    m = dict(BASE, claims=[{"measure": "starvation_deaths", "value": 1234, "unit": "person",
                            "geography": {"level": "county", "name": "Examplecounty", "province": "Henan"},
                            "period": {"start": 1960, "end": 1960, "label": "1960"}, "page_ref": "p. 1"}])
    p, m = write_manifest(tmp_path, "data", m)
    r = quality_gate.gate(p, m, set(), set(), set())
    assert r["status"] == "ready-for-review", r


def test_gate_flags_unsourced_claim_and_bad_unit(tmp_path):
    m = dict(BASE, claims=[{"measure": "excess_deaths", "value": 30000000, "unit": "million",
                            "geography": {"level": "national", "name": "China"}, "period": {"label": "1959-61"}}])
    p, m = write_manifest(tmp_path, "data", m)
    r = quality_gate.gate(p, m, set(), set(), set())
    issues = " ".join(r["gates"]["G2_verifiability"]["issues"])
    assert r["status"] == "needs-work" and "quote or page" in issues and "implausible" in issues


def test_gate_blocks_pii_in_testimony(tmp_path):
    m = dict(BASE, id="SUB-2026-0002", type="testimony",
             testimony={"consent": {"publish": True, "anonymized": True}, "narrator": {"relation": "firsthand"},
                        "events": {"province": "Anhui", "period": "1960"}})
    p, m = write_manifest(tmp_path, "testimony", m, {"testimony.md": "Call me at 13812345678."})
    r = quality_gate.gate(p, m, set(), set(), set())
    assert r["status"] == "needs-work"
    assert any("phone" in i for i in r["gates"]["G2_verifiability"]["issues"])


def test_gate_detects_nothing_new(tmp_path):
    p, m = write_manifest(tmp_path, "material", dict(BASE, type="material"))
    r = quality_gate.gate(p, m, {"https://example.org/gazetteer"}, set(), set())
    assert not r["gates"]["G3_novelty"]["pass"]


def test_intake_parses_claims():
    body = textwrap.dedent("""\
        ### Summary / 数据说明

        Provincial death rates from the 1988 compendium.

        ### Sources / 来源

        人口统计资料汇编 1949-1985 | https://example.org/t1 | Table 1

        ### Claims / 数字

        cdr | 68.58 | per_mille | province | Anhui | | 1960 | Table 1

        ### License or permission / 授权

        Public domain / 公有领域
        """)
    sec = intake_issue.parse_sections(body)
    claims = intake_issue.parse_claims(intake_issue.field(sec, "claims"))
    assert claims[0]["value"] == 68.58 and claims[0]["geography"]["name"] == "Anhui"
    prov = intake_issue.parse_provenance(intake_issue.field(sec, "sources"))
    assert prov[0]["url"] == "https://example.org/t1" and prov[0]["page_ref"] == "Table 1"


def claim(measure, value, unit="million", level="national", name="China", label="1959-61", s=1959, e=1961, cid="X", origin="registry"):
    return {"id": cid, "measure": measure, "value": value, "unit": unit, "geography": {"level": level, "name": name},
            "period": {"start": s, "end": e, "label": label}, "origin": origin}


def test_reconcile_classes():
    pool = [claim("excess_deaths", 30.0, cid="A"), claim("excess_deaths", 32.5, cid="B")]
    assert reconcile.classify(claim("excess_deaths", 31.0, cid="N", origin="SUB"), pool, 0.15)[0] == "consistent"
    assert reconcile.classify(claim("excess_deaths", 3.0, cid="N", origin="SUB"), pool, 0.15)[0] == "conflict"
    assert reconcile.classify(claim("starvation_deaths", 15.0, cid="N", origin="SUB"), pool, 0.15)[0] == "definitional"
    assert reconcile.classify(claim("excess_deaths", 1.0, level="province", name="四川", cid="N", origin="SUB"), pool, 0.15)[0] == "new_coverage"


def test_province_names_match_across_languages():
    a = reconcile.canon_place({"level": "province", "name": "四川省"})
    b = reconcile.canon_place({"level": "province", "name": "Sichuan"})
    assert a == b


def test_question_triage():
    assert triage_questions.triage("为什么1962年人口出现大幅增长？")["label"] == "question:duplicate"
    assert triage_questions.triage("What is the best pizza in Naples?")["label"] == "question:out-of-scope"
    assert triage_questions.triage("How many died in Tongwei county in 1959-61?")["label"] == "question:candidate"
    assert "四川" in "".join(tokens("四川的死亡人数"))


def test_v1_report_complete():
    assert check_cycle.main(["v1.0"]) == 0


def test_national_claims_judged_against_model_band():
    reconcile.MODEL_BAND = (22.0, 40.0)
    pool = [claim("excess_deaths", 3.0, cid="A"), claim("excess_deaths", 45.0, cid="B")]
    assert reconcile.classify(claim("excess_deaths", 10.0, name="全国", cid="N", origin="SUB"), pool, 0.15)[0] == "conflict"
    assert reconcile.classify(claim("excess_deaths", 30.0, name="中国", cid="N", origin="SUB"), pool, 0.15)[0] == "consistent"


def test_period_ranges_and_versions():
    from pipeline.common import parse_years, vkey
    assert parse_years("1959-61") == (1959, 1961)
    assert parse_years("1959年至1961年") == (1959, 1961)
    assert vkey("v1.10") > vkey("v1.9")
    c = intake_issue.parse_claims("excess_deaths | 1.2 | million | province | Hunan | | 1959-61 | p. 3")[0]
    assert (c["period"]["start"], c["period"]["end"]) == (1959, 1961) and c["page_ref"] == "p. 3"


def test_anonymous_only_when_checked():
    unchecked = "### Attribution / 署名\n\n- [ ] Credit me as anonymous in the repository\n"
    checked = unchecked.replace("[ ]", "[X]")
    f = lambda body: intake_issue.checked(intake_issue.field(intake_issue.parse_sections(body), "attribution"), "anonymous")
    assert not f(unchecked) and f(checked)
