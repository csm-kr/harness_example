# harness_framework

이 레포지토리는 **하네스(Harness)를 만들기 위한 뼈대**입니다.
실제 하네스 로직이 아니라, 하네스를 구성·실행·검증하는 데 필요한 공통 구조와 도구를 제공합니다.

> "하네스" = 모델·스크립트·실험 코드를 **재현 가능한 환경에서 일관된 방식으로 실행·검증**하기 위한 외피(Wrapper).

---

## Quick Start — 텅 빈 디렉터리에서 시작

새 프로젝트 디렉터리에서 다음 6단계를 따릅니다.

| 단계 | 무엇 | 어디서 |
|------|------|------|
| 1. 클론 | 빈 디렉터리에 이 뼈대 정본을 깐다 | 호스트 셸 (아래 코드블록) |
| 2. `/bootstrap` | 종류별 docs 뼈대를 `docs/` 에 깐다 | Claude Code |
| 3. docs 채우기 | `PRD.md → ARCHITECTURE.md → ADR.md` 순서로 본문 채움 | Claude 와 함께 |
| 4. `/docker-init` | `docs/` 정보로 `Dockerfile` / `docker-compose.yml` 갱신 | Claude Code |
| 5. `up` & `exec` | 컨테이너 띄우고 셸로 진입 | 호스트 셸 (아래 코드블록) |
| 6. `/harness` → `execute.py` | 첫 phase 설계 → step 순차 실행 | 컨테이너 안의 Claude Code |

호스트 셸 명령:

```bash
# 1. 클론 — 빈 디렉터리 안에서
git clone https://github.com/csm-kr/harness_example .
rm -rf .git
git init

# 5. 컨테이너 진입
docker compose up -d --build      # 백그라운드 띄움
docker compose exec harness bash  # 셸로 접속
```

요점:
- `/bootstrap` 은 프로젝트명·한 줄 목적·종류(`web` / `mobile` / `backend` / `ai-ml` / `data-pipeline` / `cli-lib` / `custom`)를 **대안 제시 형태**로 묻고, 고른 종류에 맞춰 `docs/` 에 PRD/ARCHITECTURE/ADR + 추가 docs 를 깐다.
- 각 docs 맨 위 "이 문서가 답하는 질문" 헤더가 무엇을 적을지 안내. 본문은 `{}` 플레이스홀더로 남아 있고 사용자가 Claude 와 함께 채운다.
- 종류별 추가 docs (예: `web` → `UI_GUIDE.md`, `ai-ml` → `DATA_CARD.md`) 도 같은 방식.
- `exec` 로 들어간 셸은 `exit` 해도 컨테이너는 살아 있다. 작업을 완전히 마쳤을 때만 `docker compose down`.

---

## 멘탈 모델 — 이 레포는 "사람"처럼 구성돼 있습니다

각 파일·폴더의 역할을 신체 비유로 보면 한눈에 잡힙니다.

| 비유 | 자산 | 역할 |
|------|------|------|
| <sub>📜&nbsp;**헌법**</sub> | <sub>`CLAUDE.md`</sub> | <sub>프로젝트가 반드시 따라야 할 원칙 (종류·스택·CRITICAL). 모든 세션에 자동 주입 → 우선순위 1번.</sub> |
| <sub>🤝&nbsp;**협업&nbsp;원칙**</sub> | <sub>`LLM_GUIDE.md`</sub> | <sub>Claude/LLM 4원칙: Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution. `CLAUDE.md` 가 참고.</sub> |
| <sub>🧠&nbsp;**뇌&nbsp;(의도·지식)**</sub> | <sub>`docs/PRD.md`, `ARCHITECTURE.md`, `ADR.md` (+ 종류별 추가 docs)</sub> | <sub>"무엇을 / 누구에게 / 왜 / 어떻게 / 왜 이 결정". 다이어그램·cross-reference 포함.</sub> |
| <sub>📋&nbsp;**계획서**</sub> | <sub>`phases/index.json`, `phases/{task}/step{N}.md`</sub> | <sub>"무엇을, 어떤 순서로". `/harness` 가 생성, `execute.py` 가 step 씩 실행.</sub> |
| <sub>🦾&nbsp;**손&nbsp;(실행)**</sub> | <sub>`scripts/execute.py`, `scripts/test_execute.py`</sub> | <sub>step 순차 실행 + 자가 교정 + 자동 커밋 + 자동 테스트.</sub> |
| <sub>🧬&nbsp;**신경계&nbsp;(자동&nbsp;반응)**</sub> | <sub>`.claude/settings.json`</sub> | <sub>`PreToolUse` 위험 명령 차단 / `Stop` 시 자동 테스트. ([HOOKS.md](docs/HOOKS.md))</sub> |
| <sub>🎓&nbsp;**습관&nbsp;(반복&nbsp;능력)**</sub> | <sub>`.claude/skills/{bootstrap,docker-init,harness,review}.md` + `templates/{type}/`</sub> | <sub>슬래시 스킬 4종 + 종류별 템플릿 정본.</sub> |
| <sub>🏠&nbsp;**환경&nbsp;(몸이&nbsp;사는&nbsp;곳)**</sub> | <sub>`Dockerfile`, `docker-compose.yml`</sub> | <sub>격리된 컨테이너. `/docker-init` 이 종류에 맞춰 갱신.</sub> |

> 충돌이 생기면 항상 헌법(`CLAUDE.md`)이 우선합니다.

---

## 🔄 표준 작업 흐름

```
0. 텅 빈 디렉터리 클론 (Quick Start 0️⃣)
        ↓
1. /bootstrap          → docs/ 에 종류별 뼈대 깔림
        ↓ 사용자가 docs/PRD → ARCH → ADR 본문 채움 (Claude 와 함께)
        ↓
2. /docker-init        → Dockerfile / docker-compose.yml 갱신
        ↓
3. /harness            → phases/{task}/step{N}.md 생성
        ↓
4. execute.py {task}   → step 순차 실행 + 자동 테스트 + 자동 커밋
        ↓
완료
```

| 단계 | 누가 | 결과물 |
|------|------|--------|
| 0. 클론 | 사람 | 정본이 깔린 빈 프로젝트 |
| 1. `/bootstrap` | Claude (대안 제시 + 사용자 선택) | 종류별 `docs/` 뼈대 |
| 1.5 docs 본문 | 사람 + Claude | 채워진 PRD/ARCH/ADR + 추가 docs |
| 2. `/docker-init` | Claude | 종류·스택에 맞는 컨테이너 환경 |
| 3. `/harness` | Claude (사람 검토·승인) | `phases/{task}/step{N}.md` |
| 4. `execute.py` | 자동화 스크립트 | `feat-{task}` 브랜치의 step별 커밋 |

---

## 📁 구성

| 경로 | 역할 |
|------|------|
| `CLAUDE.md` | 프로젝트 헌법 (플레이스홀더) — 종류·기술 스택·CRITICAL 규칙 |
| `LLM_GUIDE.md` | Claude/LLM 코딩 4원칙 — `CLAUDE.md` 가 참고 |
| `docs/PRD.md` | "무엇을·왜" — bootstrap 이 종류별로 깐 후 사용자가 채움 |
| `docs/ARCHITECTURE.md` | "어떻게" — 시스템 구조·흐름·다이어그램·외부 의존 |
| `docs/ADR.md` | "왜 이 결정" — 트레이드오프 기록 |
| `docs/HOOKS.md` | 이 레포의 정본 hook 2개 설명 + 공식 문서 링크 |
| `docs/{종류별 추가}` | 예: web → `UI_GUIDE.md`, `ACCESSIBILITY.md` / ai-ml → `DATA_CARD.md`, `MODEL_CARD.md`, `EVAL_PROTOCOL.md`, `EXPERIMENTS.md` |
| `Dockerfile`, `docker-compose.yml` | 격리된 개발 환경 (샘플 — `/docker-init` 에서 갱신) |
| `scripts/execute.py` | step 순차 실행 + 자가 교정 + 자동 커밋 |
| `scripts/test_execute.py` | pytest 기반 자동 검증 (Stop hook 이 매 응답 종료 시 실행) |
| `phases/{task}/...` | `/harness` 가 생성한 step 파일과 진행 상태 |
| `.claude/settings.json` | Claude Code hooks (PreToolUse 차단, Stop 자동 검증) |
| `.claude/skills/{bootstrap,docker-init,harness,review}.md` | 슬래시 스킬 정본 |
| `.claude/skills/templates/{type}/` | bootstrap 이 종류별로 `docs/` 에 복사하는 정본 (PRD/ARCH/ADR + 추가 docs) |

---

## 📐 개발 원칙

- **TDD** — 새 기능은 테스트 먼저, 그다음 구현. (`CLAUDE.md` 의 CRITICAL 규칙)
- **LLM 협업 4원칙** — Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution. ([LLM_GUIDE.md](./LLM_GUIDE.md) 참고)
- **커밋 메시지** — Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- **언어** — 모든 코드·주석·문서·커밋 메시지는 한국어.

---

## 🎯 목적

이 뼈대를 기반으로 각 프로젝트에 맞는 하네스를 추가·확장해 나가는 것을 전제로 합니다.
세부 설계와 결정 사항은 `docs/` 디렉터리의 문서를 참고하세요.
