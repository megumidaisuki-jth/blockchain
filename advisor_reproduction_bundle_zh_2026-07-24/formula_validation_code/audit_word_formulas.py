#!/usr/bin/env python3
"""Audit Markdown mathematics against editable Word OMML.

The script is intentionally independent of the manuscript builder.  It checks
formula coverage, numbering, encoding hygiene, and the critical OMML structures
that previously rendered correctly in Word but were semantically fragile when
exported or read through accessibility tools.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def math_text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.findall(f".//{{{M}}}t"))


def add_check(checks: list[dict], name: str, passed: bool, actual, expected) -> None:
    checks.append(
        {"name": name, "pass": bool(passed), "actual": actual, "expected": expected}
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", required=True, type=Path)
    parser.add_argument("--docx", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    md_text = args.md.read_text(encoding="utf-8")
    display_sources = re.findall(r"\\\[\s*(.*?)\s*\\\]", md_text, flags=re.DOTALL)
    inline_sources = re.findall(r"\\\((.+?)\\\)", md_text, flags=re.DOTALL)
    source_tags = []
    for source in display_sources:
        match = re.search(r"\\tag\{([^}]+)\}", source)
        if match:
            source_tags.append(match.group(1))

    with zipfile.ZipFile(args.docx) as archive:
        document_xml = archive.read("word/document.xml")
    root = ET.fromstring(document_xml)
    all_math = root.findall(f".//{{{M}}}oMath")

    formula_tables: list[tuple[str, ET.Element]] = []
    formula_geometries: list[dict] = []
    for table in root.findall(f".//{{{W}}}tbl"):
        rows = table.findall(f"{{{W}}}tr")
        if len(rows) != 1:
            continue
        cells = rows[0].findall(f"{{{W}}}tc")
        if len(cells) != 2:
            continue
        formula = cells[0].find(f".//{{{M}}}oMath")
        if formula is None:
            continue
        tag_text = "".join(node.text or "" for node in cells[1].findall(f".//{{{W}}}t"))
        formula_tables.append((tag_text.strip("()"), formula))
        tbl_w = table.find(f"{{{W}}}tblPr/{{{W}}}tblW")
        grid = table.find(f"{{{W}}}tblGrid")
        grid_widths = (
            [int(col.get(f"{{{W}}}w")) for col in grid.findall(f"{{{W}}}gridCol")]
            if grid is not None
            else []
        )
        cell_widths = []
        cell_margins = []
        for cell in cells:
            tc_w = cell.find(f"{{{W}}}tcPr/{{{W}}}tcW")
            cell_widths.append(int(tc_w.get(f"{{{W}}}w")) if tc_w is not None else None)
            tc_mar = cell.find(f"{{{W}}}tcPr/{{{W}}}tcMar")
            margins = {}
            for edge in ("top", "right", "bottom", "left"):
                node = tc_mar.find(f"{{{W}}}{edge}") if tc_mar is not None else None
                margins[edge] = int(node.get(f"{{{W}}}w")) if node is not None else None
            cell_margins.append(margins)
        formula_geometries.append(
            {
                "table_width": int(tbl_w.get(f"{{{W}}}w")) if tbl_w is not None else None,
                "grid_widths": grid_widths,
                "cell_widths": cell_widths,
                "cell_margins": cell_margins,
            }
        )

    tagged = {tag: formula for tag, formula in formula_tables if tag}
    formula_texts = [math_text(formula) for formula in all_math]
    checks: list[dict] = []

    expected_total = len(display_sources) + len(inline_sources)
    add_check(checks, "Markdown公式全部转为OMML", len(all_math) == expected_total, len(all_math), expected_total)
    add_check(
        checks,
        "显示公式数量一致",
        len(formula_tables) == len(display_sources),
        len(formula_tables),
        len(display_sources),
    )
    expected_geometry = {
        "table_width": 4580,
        "grid_widths": [4080, 500],
        "cell_widths": [4080, 500],
        "cell_margins": [
            {"top": 0, "right": 0, "bottom": 0, "left": 0},
            {"top": 0, "right": 0, "bottom": 0, "left": 0},
        ],
    }
    add_check(
        checks,
        "显示公式表使用固定单栏几何",
        all(item == expected_geometry for item in formula_geometries),
        formula_geometries,
        expected_geometry,
    )
    add_check(
        checks,
        "显示公式编号一致",
        [tag for tag, _ in formula_tables if tag] == source_tags,
        [tag for tag, _ in formula_tables if tag],
        source_tags,
    )
    expected_tags = [str(i) for i in range(1, 15)] + ["14a"] + [str(i) for i in range(15, 25)]
    add_check(checks, "主公式编号序列", source_tags == expected_tags, source_tags, expected_tags)

    bad_controls = [
        {"index": index + 1, "text": value}
        for index, value in enumerate(formula_texts)
        if re.search(r"\\|qquad|frac|left|right|operatorname|mathrm|begin|end", value)
    ]
    add_check(checks, "OMML无残留LaTeX控制词", not bad_controls, bad_controls, [])
    replacement_count = document_xml.decode("utf-8").count("\ufffd")
    add_check(checks, "无U+FFFD替换字符", replacement_count == 0, replacement_count, 0)

    def required(tag: str) -> ET.Element:
        if tag not in tagged:
            raise KeyError(f"missing tagged equation {tag}")
        return tagged[tag]

    eq3 = required("3")
    add_check(
        checks,
        "式(3)自由延拓不用脆弱limUpp波浪号",
        not eq3.findall(f".//{{{M}}}limUpp") and "free" in compact(math_text(eq3)),
        {"limUpp": len(eq3.findall(f".//{{{M}}}limUpp")), "text": math_text(eq3)},
        {"limUpp": 0, "contains": "free"},
    )

    eq8 = required("8")
    eq8_text = math_text(eq8)
    add_check(
        checks,
        "式(8)不在数学对象中嵌入中文",
        not re.search(r"[\u4e00-\u9fff]", eq8_text) and "R" in eq8_text,
        eq8_text,
        "仅事件符号R_n，无中文",
    )

    eq14 = required("14")
    eq14_sep = eq14.findall(f".//{{{M}}}sepChr")
    add_check(
        checks,
        "式(14)减号与比较号不滥用delimiter separator",
        len(eq14_sep) == 0,
        len(eq14_sep),
        0,
    )

    eq17 = required("17")
    naries = eq17.findall(f".//{{{M}}}nary")
    nary_operands = [compact(math_text(node.find(f"{{{M}}}e"))) for node in naries if node.find(f"{{{M}}}e") is not None]
    nary_subscripts = [
        len(node.find(f"{{{M}}}e").findall(f".//{{{M}}}sSub"))
        for node in naries
        if node.find(f"{{{M}}}e") is not None
    ]
    add_check(
        checks,
        "式(17)乘积操作数完整",
        any("Pr(Te>t)" in operand for operand in nary_operands)
        and any(count >= 1 for count in nary_subscripts),
        {"operand_text": nary_operands, "subscript_nodes": nary_subscripts},
        "乘积m:e包含Pr(T_e>t)及下标结构",
    )

    eq23 = required("23")
    eq23_counts = {
        "matrix": len(eq23.findall(f".//{{{M}}}m")),
        "fraction": len(eq23.findall(f".//{{{M}}}f")),
        "delimiter": len(eq23.findall(f".//{{{M}}}d")),
    }
    add_check(
        checks,
        "式(23)使用真实矩阵、分式与伸缩括号",
        eq23_counts["matrix"] >= 1 and eq23_counts["fraction"] >= 6 and eq23_counts["delimiter"] >= 2,
        eq23_counts,
        {"matrix": ">=1", "fraction": ">=6", "delimiter": ">=2"},
    )

    eq24 = required("24")
    add_check(
        checks,
        "式(24)的9/8为真实分式",
        len(eq24.findall(f".//{{{M}}}f")) >= 1,
        len(eq24.findall(f".//{{{M}}}f")),
        ">=1",
    )

    passed = sum(item["pass"] for item in checks)
    report = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "metrics": {
            "display_formulas": len(display_sources),
            "inline_formulas": len(inline_sources),
            "omml_formulas": len(all_math),
            "numbered_formulas": len(source_tags),
        },
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("status", "checks_passed", "checks_total", "metrics")}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
