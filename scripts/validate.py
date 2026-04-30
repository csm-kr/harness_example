#!/usr/bin/env python3
"""
Phase 검증기 — execute.py 실행 전 phase 구조와 step 파일을 검증한다.

Usage:
    python3 scripts/validate.py <phase-dir>
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class PhaseValidator:
    """Phase 디렉토리 구조와 step 파일 내용을 검증한다."""

    REQUIRED_SECTIONS = ["## 작업", "## Acceptance Criteria"]
    FORBIDDEN_REFS = [
        (r"이전 대화에서", "외부 대화 참조 금지"),
        (r"위에서 논의한", "외부 대화 참조 금지"),
        (r"앞서 말했듯", "외부 대화 참조 금지"),
    ]
    AC_COMMAND_RE = re.compile(r"```(?:bash|sh|shell)?\n.+?```", re.DOTALL)
    VALID_STATUSES = {"pending", "completed", "error", "blocked"}

    def __init__(self, phase_dir: Path):
        self._phase_dir = phase_dir
        self._index_file = phase_dir / "index.json"

    def validate(self) -> list[str]:
        """검증 실행. 에러 메시지 목록을 반환한다. 빈 리스트면 이상 없음."""
        if not self._phase_dir.is_dir():
            return [f"Phase 디렉토리가 존재하지 않습니다: {self._phase_dir}"]
        if not self._index_file.exists():
            return [f"index.json이 없습니다: {self._index_file}"]

        try:
            index = json.loads(self._index_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            return [f"index.json 파싱 실패: {e}"]

        errors = self._validate_index_fields(index)
        if not errors:
            errors.extend(self._validate_step_files(index))
        return errors

    def _validate_index_fields(self, index: dict) -> list[str]:
        errors = []
        for field in ("project", "phase", "steps"):
            if field not in index:
                errors.append(f"index.json: 필수 필드 '{field}'가 없습니다")
        if "steps" not in index:
            return errors
        for s in index["steps"]:
            n = s.get("step", "?")
            for f in ("step", "name", "status"):
                if f not in s:
                    errors.append(f"step {n}: 필수 필드 '{f}'가 없습니다")
            if s.get("status") not in self.VALID_STATUSES:
                errors.append(f"step {n}: 유효하지 않은 status '{s.get('status')}'")
        return errors

    def _validate_step_files(self, index: dict) -> list[str]:
        errors = []
        for s in index.get("steps", []):
            step_num = s["step"]
            step_file = self._phase_dir / f"step{step_num}.md"
            if not step_file.exists():
                errors.append(f"step{step_num}.md 파일이 없습니다")
                continue
            content = step_file.read_text(encoding="utf-8")
            errors.extend(self._validate_content(step_num, content))
        return errors

    def _validate_content(self, step_num: int, content: str) -> list[str]:
        errors = []
        for section in self.REQUIRED_SECTIONS:
            if section not in content:
                errors.append(f"step{step_num}.md: 필수 섹션 '{section}'이 없습니다")
        for pattern, reason in self.FORBIDDEN_REFS:
            if re.search(pattern, content):
                errors.append(f"step{step_num}.md: {reason}")
        if "## Acceptance Criteria" in content:
            ac_start = content.index("## Acceptance Criteria")
            if not self.AC_COMMAND_RE.search(content[ac_start:]):
                errors.append(f"step{step_num}.md: AC에 실행 커맨드 블록(```bash)이 없습니다")
        return errors


def main():
    parser = argparse.ArgumentParser(description="Phase 검증기")
    parser.add_argument("phase_dir", help="Phase 디렉토리명 (예: 0-mvp)")
    args = parser.parse_args()

    phase_dir = ROOT / "phases" / args.phase_dir
    errors = PhaseValidator(phase_dir).validate()

    if errors:
        print(f"✗ 검증 실패 ({len(errors)}개 오류):")
        for e in errors:
            print(f"  • {e}")
        sys.exit(1)

    print(f"✓ {args.phase_dir} 검증 통과")


if __name__ == "__main__":
    main()
