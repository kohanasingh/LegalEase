"""
Sources bare-act section text for the LegalEase legal corpus.

Source: advocatekhoj.com's bare-acts library (see CHANGES.md for why this
replaces indiacode.nic.in — the official India Code portal blocks scripted
requests). Its robots.txt declares Content-Signal: search=yes, ai-train=no,
use=reference — we only read statutory text for retrieval-time grounding
(reference use), never for model training, consistent with that policy.

Each act's site section is a flat list of numbered section pages
(".../<slug>/<n>.php"); not every number in range is a real section
(repealed chapters return 404), so this walks a number range and skips
misses. Output: one JSON file per act under corpus/raw/, each section
already an atomic chunk (structure-aware — see ARCHITECTURE.md §3).
"""
import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

RAW_DIR = Path(__file__).resolve().parent.parent / "raw"
USER_AGENT = "LegalEaseCorpusBot/1.0 (educational project; contact: ca13em04en@gmail.com)"
REQUEST_DELAY_SECONDS = 0.5

ACTS = [
    {
        "slug": "indian_contract_act_1872",
        "source_name": "Indian Contract Act, 1872",
        "source_type": "act",
        "base_url": "https://www.advocatekhoj.com/library/bareacts/indiancontract",
        "max_section": 240,
    },
]


def fetch_section(base_url: str, number: int) -> dict | None:
    url = f"{base_url}/{number}.php"
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=20)
    if resp.status_code != 200:
        return None

    soup = BeautifulSoup(resp.text, "lxml")
    heading = soup.select_one("p.font-bold.border-b")
    if heading is None:
        return None

    heading_text = heading.get_text(strip=True)
    match = re.match(r"^(\d+[A-Za-z]?)\.\s*(.*)$", heading_text)
    if not match:
        return None
    section_number, title = match.group(1), match.group(2)

    body_paragraphs = [
        p.get_text(" ", strip=True)
        for p in heading.find_next_siblings("p", class_="mb-4")
    ]
    text = "\n".join(p for p in body_paragraphs if p)
    if not text:
        return None

    return {"section": section_number, "title": title, "text": text}


def scrape_act(act: dict) -> list[dict]:
    sections = []
    for number in range(1, act["max_section"] + 1):
        section = fetch_section(act["base_url"], number)
        if section is not None:
            sections.append(section)
            print(f"  [{act['slug']}] section {section['section']}: {section['title'][:60]}")
        time.sleep(REQUEST_DELAY_SECONDS)
    return sections


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for act in ACTS:
        print(f"Scraping {act['source_name']}...")
        sections = scrape_act(act)
        out_path = RAW_DIR / f"{act['slug']}.json"
        out_path.write_text(
            json.dumps(
                {
                    "source_name": act["source_name"],
                    "source_type": act["source_type"],
                    "sections": sections,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        print(f"Wrote {len(sections)} sections to {out_path}")


if __name__ == "__main__":
    main()
