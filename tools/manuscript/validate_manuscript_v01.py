#!/usr/bin/env python3
"""Validate a Chinese journal manuscript and its DOCX package.

This is a deterministic structural/content gate.  It does not replace peer review;
it checks the key claims, journal-facing metadata limits, and Word package shape.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M = "http://schemas.openxmlformats.org/officeDocument/2006/math"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chinese_length(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def check(condition: bool, name: str, actual, expected, checks: list[dict]) -> None:
    checks.append(
        {
            "name": name,
            "pass": bool(condition),
            "actual": actual,
            "expected": expected,
        }
    )


def expand_citation(token: str) -> list[int]:
    values: list[int] = []
    for part in token.split(","):
        if "-" in part:
            start, end = (int(value) for value in part.split("-", 1))
            values.extend(range(start, end + 1))
        else:
            values.append(int(part))
    return values


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--md", type=Path, required=True)
    parser.add_argument("--docx", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    md_text = args.md.read_text(encoding="utf-8")
    checks: list[dict] = []
    display_math_sources = re.findall(r"\\\[\s*(.*?)\s*\\\]", md_text, flags=re.DOTALL)
    inline_math_sources = re.findall(r"\\\((.+?)\\\)", md_text, flags=re.DOTALL)
    expected_omath_count = len(display_math_sources) + len(inline_math_sources)
    equation_tags = [
        match.group(1)
        for source in display_math_sources
        if (match := re.search(r"\\tag\{([^}]+)\}", source))
    ]

    title_match = re.search(r"^#\s+(.+)$", md_text, flags=re.MULTILINE)
    abstract_match = re.search(
        r"\*\*摘\s*要：\*\*\s*(.+?)\n\n\*\*关键词：\*\*",
        md_text,
        flags=re.DOTALL,
    )
    keyword_match = re.search(r"\*\*关键词：\*\*\s*(.+)", md_text)
    title = title_match.group(1).strip() if title_match else ""
    abstract = re.sub(r"\s+", "", abstract_match.group(1)) if abstract_match else ""
    keywords = (
        [item.strip() for item in re.split(r"[；;]", keyword_match.group(1)) if item.strip()]
        if keyword_match
        else []
    )
    references = re.findall(r"^\[(\d+)\]\s", md_text, flags=re.MULTILINE)
    expected_reference_numbers = list(range(1, len(references) + 1))
    expected_reference_strings = [str(value) for value in expected_reference_numbers]
    body_before_references = md_text.split("## 参考文献", 1)[0]
    citation_tokens = re.findall(r"\[([0-9]+(?:[-,][0-9]+)*)\]", body_before_references)
    citation_sequence = [number for token in citation_tokens for number in expand_citation(token)]
    first_citation_order = list(dict.fromkeys(citation_sequence))

    check(chinese_length(title) <= 20, "中文标题不超过20字", chinese_length(title), "<=20", checks)
    check(chinese_length(abstract) <= 200, "中文摘要不超过200字", chinese_length(abstract), "<=200", checks)
    check(len(keywords) >= 4, "中文关键词不少于4个", len(keywords), ">=4", checks)
    check(
        references == expected_reference_strings,
        "参考文献连续编号",
        references,
        f"1..{len(references)}",
        checks,
    )
    check(
        first_citation_order == expected_reference_numbers,
        "正文首次引文顺序",
        first_citation_order,
        expected_reference_numbers,
        checks,
    )
    check(
        set(citation_sequence) == set(expected_reference_numbers),
        "全部参考文献均在正文引出",
        sorted(set(citation_sequence)),
        expected_reference_numbers,
        checks,
    )

    compact_text = re.sub(r"\s+", "", md_text)
    required_fragments = {
        "T16对应定理1": "定理1有限网络吸收方程",
        "T17漂移主导部分": "定理2漂移主导区",
        "T17集中界充分大N": r"N\geN_\varepsilon\)满足",
        "T17指数矩充分大N": r"\sup_{N\geN_0}",
        "T17扩散部分": "定理3临界与公平扩散区",
        "T18a对应定理4": "定理4高斯块独立",
        "T19对应定理5": "定理5离散—高斯生存序桥接",
        "T19离散相关均值": "0.933236",
        "T19离散独立均值": "0.884056239375",
        "N=3精确均值": "8.654869502436274",
        "三分区双阶段样本量": "双阶段32万条轨迹",
        "三分区阶段差异": "20个阶段差异",
        "高阶跨拓扑36单元": "36个预设有限设计单元",
        "高阶最弱单元效应": "0.0157195",
        "2026设计单元": "2026年过滤投影的主阶段与异种子阶段各含16个单元",
        "需求插值总体斜率": "-0.038857",
        "统一时钟配对轨迹束": "共96000个独立轨迹束",
        "统一时钟严格事件顺序": r"全部满足\(0<\widetilde\tau_N<\rho_{\rmbal}\)",
        "等节点资本设计": r"每节点资本\(4N\)",
        "触零一步风险": "19.23%～24.66%",
        "固定路由失败边界": "固定路由因方向余额不足而被拒绝",
        "停止量语义边界": "不等同于现实支付失败",
    }
    for name, fragment in required_fragments.items():
        check(fragment in compact_text, f"关键声明存在：{name}", fragment in compact_text, True, checks)

    forbidden_patterns = {
        "禁止有限N普遍非负声明": r"有限(?:规模|N).{0,12}(?:普遍|总是|必然).{0,8}(?:非负|不短)",
        "禁止真实支付失败等同声明": r"(?<!不)(?:等同于|就是)真实支付失败",
        "禁止完整2026网络声明": r"2026.{0,12}(?:完整|全量)Lightning网络",
    }
    forbidden_hits = {
        name: re.findall(pattern, md_text) for name, pattern in forbidden_patterns.items()
    }
    for name, hits in forbidden_hits.items():
        check(not hits, name, hits, [], checks)

    with zipfile.ZipFile(args.docx) as archive:
        names = archive.namelist()
        name_set = set(names)
        zip_crc_error = archive.testzip()
        document_xml = archive.read("word/document.xml")
        root = ET.fromstring(document_xml)
        omath_count = len(root.findall(f".//{{{M}}}oMath"))
        omath_texts = [
            "".join(node.text or "" for node in formula.findall(f".//{{{M}}}t"))
            for formula in root.findall(f".//{{{M}}}oMath")
        ]
        omath_bad_controls = [
            {"equation": index + 1, "text": value}
            for index, value in enumerate(omath_texts)
            if re.search(r"\\|qquad|frac|left|right|infty|operatorname|mathrm|begin|end", value)
        ]
        replacement_character_count = document_xml.decode("utf-8").count("\ufffd")
        formula_tables = []
        formula_table_geometries = []
        for table in root.findall(f".//{{{W}}}tbl"):
            rows = table.findall(f"{{{W}}}tr")
            if len(rows) != 1:
                continue
            cells = rows[0].findall(f"{{{W}}}tc")
            if len(cells) != 2 or not cells[0].findall(f".//{{{M}}}oMath"):
                continue
            tag_text = "".join(node.text or "" for node in cells[1].findall(f".//{{{W}}}t"))
            formula_tables.append(tag_text)
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
            formula_table_geometries.append(
                {
                    "table_width": int(tbl_w.get(f"{{{W}}}w")) if tbl_w is not None else None,
                    "grid_widths": grid_widths,
                    "cell_widths": cell_widths,
                    "cell_margins": cell_margins,
                }
            )
        sect_prs = root.findall(f".//{{{W}}}sectPr")
        column_counts = []
        for sect_pr in sect_prs:
            cols = sect_pr.find(f"{{{W}}}cols")
            value = cols.get(f"{{{W}}}num") if cols is not None else None
            column_counts.append(int(value) if value else 1)
        media = [name for name in names if name.startswith("word/media/")]
        media_suffixes = sorted(Path(name).suffix.lower() for name in media)
        field_count = len(root.findall(f".//{{{W}}}fldSimple")) + len(
            root.findall(f".//{{{W}}}fldChar")
        )
        rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
        missing_relationship_targets: list[dict] = []
        for rel_name in (name for name in names if name.endswith(".rels")):
            rel_root = ET.fromstring(archive.read(rel_name))
            source_dir = posixpath.dirname(posixpath.dirname(rel_name))
            for relation in rel_root.findall(f"{{{rel_ns}}}Relationship"):
                if relation.get("TargetMode") == "External":
                    continue
                target = relation.get("Target", "")
                resolved = posixpath.normpath(posixpath.join(source_dir, target)).lstrip("/")
                if resolved not in name_set:
                    missing_relationship_targets.append(
                        {"rels": rel_name, "id": relation.get("Id"), "target": resolved}
                    )

    check(
        omath_count == expected_omath_count,
        "Markdown公式均转换为可编辑Word公式对象",
        omath_count,
        expected_omath_count,
        checks,
    )
    check(
        len(formula_tables) == len(display_math_sources),
        "显示公式表数量与Markdown一致",
        len(formula_tables),
        len(display_math_sources),
        checks,
    )
    check(
        [text.strip("()") for text in formula_tables if text]
        == equation_tags,
        "显示公式编号与源文件一致",
        [text.strip("()") for text in formula_tables if text],
        equation_tags,
        checks,
    )
    expected_formula_geometry = {
        "table_width": 4580,
        "grid_widths": [4080, 500],
        "cell_widths": [4080, 500],
        "cell_margins": [
            {"top": 0, "right": 0, "bottom": 0, "left": 0},
            {"top": 0, "right": 0, "bottom": 0, "left": 0},
        ],
    }
    check(
        all(item == expected_formula_geometry for item in formula_table_geometries),
        "显示公式表严格位于单栏宽度内",
        formula_table_geometries,
        expected_formula_geometry,
        checks,
    )
    check(not omath_bad_controls, "Word公式无未转换控制词", omath_bad_controls, [], checks)
    check(replacement_character_count == 0, "Word正文无替换字符U+FFFD", replacement_character_count, 0, checks)
    full_width_artifact_count = len(re.findall(r"^\*\*表\d+", md_text, flags=re.MULTILINE)) + len(
        re.findall(r"^!\[", md_text, flags=re.MULTILINE)
    )
    expected_section_count = 2 + 2 * full_width_artifact_count
    expected_column_counts = [1, 2] + [value for _ in range(full_width_artifact_count) for value in (1, 2)]
    check(len(sect_prs) == expected_section_count, "连续分节数量", len(sect_prs), expected_section_count, checks)
    check(column_counts == expected_column_counts, "单双栏分节序列", column_counts, expected_column_counts, checks)
    markdown_image_count = len(re.findall(r"^!\[", md_text, flags=re.MULTILINE))
    expected_media_suffixes = [".png"] * markdown_image_count
    check(
        media_suffixes == expected_media_suffixes,
        "稿件仅嵌入Markdown声明的PNG图片",
        media_suffixes,
        expected_media_suffixes,
        checks,
    )
    check(field_count == 0, "无动态域残留", field_count, 0, checks)
    check(zip_crc_error is None, "DOCX ZIP CRC完整", zip_crc_error, None, checks)
    check(not missing_relationship_targets, "DOCX内部关系目标完整", missing_relationship_targets, [], checks)

    passed = sum(item["pass"] for item in checks)
    report = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "inputs": {
            "markdown": str(args.md.resolve()),
            "markdown_sha256": sha256(args.md),
            "docx": str(args.docx.resolve()),
            "docx_sha256": sha256(args.docx),
        },
        "metrics": {
            "title_chinese_characters": chinese_length(title),
            "abstract_chinese_characters": chinese_length(abstract),
            "keyword_count": len(keywords),
            "reference_count": len(references),
            "omath_count": omath_count,
            "display_formula_count": len(display_math_sources),
            "inline_formula_count": len(inline_math_sources),
            "equation_tags": equation_tags,
            "section_count": len(sect_prs),
            "column_counts": column_counts,
            "media_suffixes": media_suffixes,
        },
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("status", "checks_passed", "checks_total", "metrics")}, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
