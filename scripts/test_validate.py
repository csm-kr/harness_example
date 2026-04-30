"""
validate.py TDD 테스트.
PhaseValidator 동작을 사전 정의하고 구현이 이를 충족하는지 검증한다.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from validate import PhaseValidator


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------

def _valid_step_md(step_num: int = 0) -> str:
    return f"""\
# Step {step_num}: setup

## 읽어야 할 파일

- `/docs/ARCHITECTURE.md`

## 작업

프로젝트 초기화 작업을 수행한다.

## Acceptance Criteria

```bash
npm run build
npm test
```

## 금지사항

- 기존 테스트를 깨뜨리지 마라.
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def phase_dir(tmp_path):
    d = tmp_path / "phases" / "0-mvp"
    d.mkdir(parents=True)
    index = {
        "project": "TestProject",
        "phase": "0-mvp",
        "steps": [{"step": 0, "name": "setup", "status": "pending"}],
    }
    (d / "index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False))
    (d / "step0.md").write_text(_valid_step_md(0))
    return d


# ---------------------------------------------------------------------------
# validate() 진입점
# ---------------------------------------------------------------------------

class TestValidate:
    def test_valid_phase_returns_no_errors(self, phase_dir):
        assert PhaseValidator(phase_dir).validate() == []

    def test_missing_phase_dir(self, tmp_path):
        errors = PhaseValidator(tmp_path / "nonexistent").validate()
        assert len(errors) == 1
        assert "존재하지 않습니다" in errors[0]

    def test_missing_index_json(self, tmp_path):
        d = tmp_path / "phases" / "0-mvp"
        d.mkdir(parents=True)
        errors = PhaseValidator(d).validate()
        assert any("index.json" in e for e in errors)

    def test_malformed_index_json(self, phase_dir):
        (phase_dir / "index.json").write_text("{invalid json")
        errors = PhaseValidator(phase_dir).validate()
        assert any("파싱 실패" in e for e in errors)


# ---------------------------------------------------------------------------
# _validate_index_fields
# ---------------------------------------------------------------------------

class TestValidateIndexFields:
    def _write_index(self, phase_dir, index):
        (phase_dir / "index.json").write_text(json.dumps(index, ensure_ascii=False))

    def test_missing_project_field(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        del index["project"]
        self._write_index(phase_dir, index)
        errors = PhaseValidator(phase_dir).validate()
        assert any("'project'" in e for e in errors)

    def test_missing_phase_field(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        del index["phase"]
        self._write_index(phase_dir, index)
        errors = PhaseValidator(phase_dir).validate()
        assert any("'phase'" in e for e in errors)

    def test_missing_steps_field(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        del index["steps"]
        self._write_index(phase_dir, index)
        errors = PhaseValidator(phase_dir).validate()
        assert any("'steps'" in e for e in errors)

    def test_invalid_status(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        index["steps"][0]["status"] = "running"
        self._write_index(phase_dir, index)
        errors = PhaseValidator(phase_dir).validate()
        assert any("유효하지 않은 status" in e for e in errors)

    def test_all_valid_statuses_accepted(self, phase_dir):
        for status in ("pending", "completed", "error", "blocked"):
            index = json.loads((phase_dir / "index.json").read_text())
            index["steps"][0]["status"] = status
            field_errors = PhaseValidator(phase_dir)._validate_index_fields(index)
            assert not any("유효하지 않은 status" in e for e in field_errors), f"{status} should be valid"

    def test_step_missing_name(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        del index["steps"][0]["name"]
        self._write_index(phase_dir, index)
        errors = PhaseValidator(phase_dir).validate()
        assert any("'name'" in e for e in errors)

    def test_step_missing_status(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        del index["steps"][0]["status"]
        self._write_index(phase_dir, index)
        errors = PhaseValidator(phase_dir).validate()
        assert any("'status'" in e for e in errors)


# ---------------------------------------------------------------------------
# _validate_step_files
# ---------------------------------------------------------------------------

class TestValidateStepFiles:
    def test_missing_step_file(self, phase_dir):
        (phase_dir / "step0.md").unlink()
        errors = PhaseValidator(phase_dir).validate()
        assert any("step0.md 파일이 없습니다" in e for e in errors)

    def test_all_steps_must_have_files(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        index["steps"].append({"step": 1, "name": "core", "status": "pending"})
        (phase_dir / "index.json").write_text(json.dumps(index))
        # step1.md 없음
        errors = PhaseValidator(phase_dir).validate()
        assert any("step1.md" in e for e in errors)

    def test_existing_step_file_no_error(self, phase_dir):
        errors = PhaseValidator(phase_dir).validate()
        assert not any("파일이 없습니다" in e for e in errors)


# ---------------------------------------------------------------------------
# _validate_content
# ---------------------------------------------------------------------------

class TestValidateContent:
    def test_missing_작업_section(self, phase_dir):
        content = _valid_step_md().replace("## 작업", "## 다른섹션")
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert any("## 작업" in e for e in errors)

    def test_missing_ac_section(self, phase_dir):
        content = _valid_step_md().replace("## Acceptance Criteria", "## 다른섹션")
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert any("Acceptance Criteria" in e for e in errors)

    def test_ac_without_code_block(self, phase_dir):
        content = "## 작업\n내용\n\n## Acceptance Criteria\n\n텍스트만 있고 커맨드 없음\n"
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert any("커맨드 블록" in e for e in errors)

    def test_ac_with_bash_block(self, phase_dir):
        errors = PhaseValidator(phase_dir).validate()
        assert not any("커맨드 블록" in e for e in errors)

    def test_ac_with_plain_code_block(self, phase_dir):
        content = "## 작업\n내용\n\n## Acceptance Criteria\n\n```\nnpm test\n```\n"
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert not any("커맨드 블록" in e for e in errors)

    def test_ac_with_sh_block(self, phase_dir):
        content = "## 작업\n내용\n\n## Acceptance Criteria\n\n```sh\npython -m pytest\n```\n"
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert not any("커맨드 블록" in e for e in errors)

    def test_forbidden_ref_이전_대화에서(self, phase_dir):
        content = _valid_step_md() + "\n이전 대화에서 결정한 대로 구현하라.\n"
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert any("외부 대화 참조 금지" in e for e in errors)

    def test_forbidden_ref_위에서_논의한(self, phase_dir):
        content = _valid_step_md() + "\n위에서 논의한 방식으로 구현한다.\n"
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert any("외부 대화 참조 금지" in e for e in errors)

    def test_forbidden_ref_앞서_말했듯(self, phase_dir):
        content = _valid_step_md() + "\n앞서 말했듯 이 방식이 올바르다.\n"
        (phase_dir / "step0.md").write_text(content)
        errors = PhaseValidator(phase_dir).validate()
        assert any("외부 대화 참조 금지" in e for e in errors)

    def test_valid_content_no_errors(self, phase_dir):
        assert PhaseValidator(phase_dir).validate() == []


# ---------------------------------------------------------------------------
# 다중 step 통합
# ---------------------------------------------------------------------------

class TestMultipleSteps:
    def test_errors_aggregated_across_steps(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        index["steps"].append({"step": 1, "name": "core", "status": "pending"})
        (phase_dir / "index.json").write_text(json.dumps(index))
        (phase_dir / "step1.md").write_text("# Step 1\n\n필수 섹션이 없음\n")

        errors = PhaseValidator(phase_dir).validate()
        step1_errors = [e for e in errors if "step1" in e]
        assert len(step1_errors) >= 2  # 작업 없음 + AC 없음

    def test_valid_first_invalid_second(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        index["steps"].append({"step": 1, "name": "core", "status": "pending"})
        (phase_dir / "index.json").write_text(json.dumps(index))
        (phase_dir / "step1.md").write_text("## 작업\n내용\n")  # AC 없음

        errors = PhaseValidator(phase_dir).validate()
        assert not any("step0" in e for e in errors)
        assert any("step1" in e for e in errors)

    def test_all_valid_steps_no_errors(self, phase_dir):
        index = json.loads((phase_dir / "index.json").read_text())
        index["steps"].append({"step": 1, "name": "core", "status": "pending"})
        (phase_dir / "index.json").write_text(json.dumps(index))
        (phase_dir / "step1.md").write_text(_valid_step_md(1))

        assert PhaseValidator(phase_dir).validate() == []
