"""Build markdown chapters with embedded Playwright screenshots for a living user manual."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from playwright.sync_api import Page


def _safe_image_stem(name: str, max_len: int = 64) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", name.strip())[:max_len]
    return s.strip("-") or "step"


@dataclass
class _Chapter:
    slug: str
    title: str
    parts: list[str] = field(default_factory=list)
    step_no: int = 0


class ManualBuilder:
    """Collects chapters; each :meth:`step` appends a heading, copy, and one screenshot path."""

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir).resolve()
        self.images_dir = self.output_dir / "images"
        self._chapters: list[_Chapter] = []
        self._current: _Chapter | None = None
        self._shot_idx = 0

    def start_chapter(self, slug: str, title: str, intro: str | None = None) -> None:
        ch = _Chapter(slug=slug, title=title)
        ch.parts.append(f"# {title}\n\n")
        if intro:
            ch.parts.append(f"{intro}\n\n")
        self._chapters.append(ch)
        self._current = ch

    def step(
        self,
        page: Page,
        *,
        title: str,
        why: str,
        how: str,
        image_basename: str,
        full_page: bool = True,
    ) -> None:
        if self._current is None:
            raise RuntimeError("Call start_chapter() before step()")
        ch = self._current
        ch.step_no += 1
        self._shot_idx += 1
        stem = _safe_image_stem(image_basename)
        filename = f"{ch.slug}_{ch.step_no:02d}_{self._shot_idx:03d}_{stem}.png"
        self.images_dir.mkdir(parents=True, exist_ok=True)
        path = self.images_dir / filename
        page.screenshot(path=str(path), full_page=full_page)
        rel = f"images/{filename}"
        n = ch.step_no
        ch.parts.append(f"## {n}. {title}\n\n")
        ch.parts.append("**Why:** " + why.strip() + "\n\n")
        ch.parts.append("**How:** " + how.strip() + "\n\n")
        ch.parts.append(f"![{title}]({rel})\n\n")
        ch.parts.append("---\n\n")

    def write_chapter_files(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        for ch in self._chapters:
            (self.output_dir / f"{ch.slug}.md").write_text("".join(ch.parts), encoding="utf-8")

    def write_index(self) -> None:
        self.write_chapter_files()
        lines: list[str] = [
            "# Req2Veri user manual (generated)\n\n",
            "This document set is **generated automatically** by the Playwright suite in "
            "`external_frontend_tests/docs_suite/`. It explains *why* each area exists and *how* to open it. "
            "Re-run the suite after UI changes to refresh screenshots.\n\n",
            "## Chapters\n\n",
        ]
        for ch in self._chapters:
            lines.append(f"- [{ch.title}]({ch.slug}.md)\n")
        lines.append("\n## Regenerate\n\n")
        lines.append(
            "From `external_frontend_tests` with the SPA and API running, see [the suite README](../README.md).\n"
        )
        (self.output_dir / "index.md").write_text("".join(lines), encoding="utf-8")
