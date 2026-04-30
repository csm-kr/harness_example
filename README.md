# harness_framework

이 레포지토리는 **하네스(Harness)를 만들기 위한 뼈대**입니다.
실제 하네스 로직 자체가 아니라, 하네스를 구성·실행·검증하는 데 필요한 공통 구조와 도구를 제공합니다.

여기서 "하네스"란 모델·스크립트·실험 코드를 **재현 가능한 환경에서 일관된 방식으로 실행·검증**하기 위한 외피(Wrapper)를 의미합니다.

---

## 🧠 멘탈 모델 — 이 레포는 "사람"처럼 구성돼 있습니다

각 파일·폴더의 역할을 신체 비유로 보면 한눈에 잡힙니다.

| 비유 | 위치 | 역할 |
|------|------|------|
| 📜 **헌법 (최상위 규칙)** | `CLAUDE.md` | 이 하네스가 **반드시 따라야 할 원칙** — TDD, 커밋 컨벤션, 언어, CRITICAL 규칙. 다른 모든 결정은 이 헌법을 위배하면 안 됩니다. |
| 🧠 **뇌 (의도·지식)** | `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/ADR.md` | "**무엇을, 왜** 만드는가" — 목표·아키텍처·결정 기록 |
| 📋 **계획서 (실행 청사진)** | `phases/index.json`, `phases/{task}/index.json`, `phases/{task}/step{N}.md` | "**무엇을, 어떤 순서로** 할 것인가" — `/harness`가 생성하고 `execute.py`가 한 step씩 실행 |
| 🦾 **손 (행동)** | `scripts/execute.py`, `scripts/validate.py`, `scripts/test_*.py` | "실제로 **무엇을 하는가**" — 계획서대로 step 실행·검증·테스트 |
| 🧬 **신경계 (제어·반사)** | `.claude/settings.json` (hooks), `scripts/run_stop_hook.sh` | Claude의 **자동 반응** — 위험 명령 차단(`PreToolUse`), 작업 종료 시 후처리(`Stop`). 자세한 사용법은 [`docs/HOOKS.md`](docs/HOOKS.md) 참고 |
| 🎓 **습관 (반복 능력)** | `.claude/skills/` (`docker-init.md`, `harness.md`, `review.md`) | "**자주 하는 일을 어떻게 하는가**" — 재사용 가능한 절차·체크리스트 |
| 🏠 **몸이 사는 환경** | `Dockerfile`, `docker-compose.yml` | 모든 일이 일어나는 **격리된 컨테이너** |

> 💡 **새 기능을 추가할 때는 이 순서로 생각하세요.**
> 헌법(원칙) → 뇌(의도) → 계획서(`/harness`로 생성) → 손(`execute.py`로 실행) → 환경(필요 시 의존성 추가).
> **충돌이 생기면 항상 헌법(`CLAUDE.md`)이 우선합니다.**

---

## 🔄 표준 작업 흐름

```
docs/ 채우기 (🧠 뇌)
        ↓
/harness 실행
        ↓ Claude가 docs를 읽고 사용자와 논의 후
        ↓ phases/{task}/step*.md 생성 (📋 계획서)
        ↓
python3 scripts/execute.py {task}
        ↓ step 0 → step 1 → ... 순차 실행 (🦾 손)
        ↓ 실패 시 자동 재시도 (최대 3회), step별 자동 커밋
        ↓
완료
```

| 단계 | 누가 하나 | 결과물 |
|------|----------|--------|
| `docs/` 채우기 | 사람 | PRD/ARCHITECTURE/ADR 텍스트 |
| `/harness` | Claude (사람 검토·승인) | `phases/{task}/index.json`, `step{N}.md` |
| `execute.py {task}` | 자동화 스크립트 | `feat-{task}` 브랜치의 step별 커밋 |

> 💡 `/harness`는 **계획만** 만들고 코드는 만들지 않습니다. 실제 코드는 `execute.py`가 step 파일을 Claude에게 한 번에 하나씩 던져 작성시킵니다.

---

## 🚀 Quick Start (5분)

처음 이 레포를 받았다면, 아래 5단계만 순서대로 따라가면 됩니다.

### 1️⃣ 레포 클론

실행할 레포 디렉터리로 들어간 뒤, 아래 명령어를 차례로 입력하세요.

```bash
git clone https://github.com/csm-kr/harness_example .
rm -rf .git
git init
```

> 💡 `git clone ... .` 은 **현재 디렉터리에 그대로** 클론합니다.
> 이어서 `rm -rf .git` 으로 원본 히스토리를 제거하고, `git init` 으로 새 git 저장소를 초기화하면 이 뼈대를 템플릿처럼 사용할 수 있습니다.

### 2️⃣ Claude Code 켜고 **먼저 상의**하기
> ⚠️ **코드를 직접 고치기 전에 Claude와 1회 정렬 세션을 가지세요.**
> 아래 4가지를 결정하지 않고 시작하면 나중에 전부 갈아엎게 됩니다.

Claude에게 다음 그대로 붙여넣어 시작하세요:

```
이 하네스 뼈대를 새 프로젝트에 적용하려고 해. 시작 전에 같이 정해줘:
1. Docker 환경 (베이스 이미지, GPU/CUDA 사용 여부, Python 버전, 패키지 매니저)
2. 프로젝트 메타데이터 (프로젝트명, 기술 스택, 핵심 기능 3가지)
3. execute.py / validate.py가 각각 무엇을 해야 하는지
4. 입력/출력 인터페이스 (설정 파일 형식, 결과 저장 위치)
```

→ 정해진 내용을 Claude가 `Dockerfile`, `CLAUDE.md`, `docs/PRD.md`, `docs/ARCHITECTURE.md`에 반영합니다.

### 3️⃣ Docker 빌드 & 진입
```bash
# 컨테이너를 백그라운드로 띄움 (TensorBoard 등 장시간 작업이 계속 살아 있음)
docker compose up -d --build

# 셸로 접속 (여러 터미널에서 동시 접속 가능)
docker compose exec harness bash

# 작업이 끝났을 때만 정리:
docker compose down
```
> 💡 `exec`로 들어간 셸은 `exit`해도 컨테이너는 죽지 않습니다.
> TensorBoard(`localhost:6007`) 같은 장시간 작업은 `up` 상태에서 계속 동작합니다.

### 4️⃣ 동작 확인
컨테이너 안에서:
```bash
pytest scripts/      # 샘플 테스트가 모두 통과해야 함
```

### 5️⃣ 첫 커밋
```bash
git add .
git commit -m "chore: 프로젝트 초기 설정"
git push -u origin main
```

✅ **여기까지 오면 준비 완료.** 이제 `scripts/execute.py`에 실제 하네스 로직을 채워 나가면 됩니다.

---

## 🗺️ 다음에 무엇을 할까?

| 상황 | 다음 행동 |
|------|----------|
| 하네스 로직을 새로 추가하고 싶다 | `scripts/test_execute.py`에 테스트부터 작성 → `execute.py` 구현 (TDD) |
| 검증 규칙을 추가하고 싶다 | `scripts/test_validate.py` → `validate.py` |
| 아키텍처가 바뀌었다 | `docs/ARCHITECTURE.md` 업데이트, 중요한 결정은 `docs/ADR.md`에 기록 |
| Claude 동작을 바꾸고 싶다 | `.claude/settings.json` 또는 `.claude/skills/` 수정 |
| 어디서부터 봐야 할지 모르겠다 | `docs/PRD.md` → `docs/ARCHITECTURE.md` → `scripts/execute.py` 순서로 읽기 |

---

## 📁 구성

| 경로 | 역할 |
|------|------|
| `Dockerfile`, `docker-compose.yml` | 격리된 개발 환경 (**샘플** — Quick Start 2단계에서 교체) |
| `phases/index.json` | 모든 task(phase)의 진행 상황 인덱스 |
| `phases/{task}/index.json` | 특정 task의 step 목록과 상태 (`pending`/`completed`/`error`/`blocked`) |
| `phases/{task}/step{N}.md` | 각 step의 작업 지시서 (`/harness`가 생성) |
| `phases/{task}/step{N}-output.json` | 각 step의 Claude 실행 결과 (자동 생성) |
| `scripts/execute.py` | step 순차 실행 + 자가 교정 + 자동 커밋 |
| `scripts/validate.py` | 실행 결과 검증 |
| `scripts/test_*.py` | pytest 기반 테스트 |
| `scripts/run_stop_hook.sh` | Claude Code stop hook 스크립트 |
| `docs/PRD.md` | 제품 요구사항 (플레이스홀더) |
| `docs/ARCHITECTURE.md` | 아키텍처 결정 (플레이스홀더) |
| `docs/ADR.md` | 주요 결정 기록 |
| `docs/HOOKS.md` | Claude Code hooks(PreToolUse/PostToolUse/Notification/Stop) 가이드 |
| `docs/UI_GUIDE.md` | UI 가이드 (필요 시) |
| `CLAUDE.md` | 프로젝트 규칙 및 개발 프로세스 (플레이스홀더) |
| `.claude/` | Claude Code 설정 및 스킬 |

---

## 📐 개발 원칙

- **TDD** — 새 기능은 테스트 먼저, 그다음 구현. (`CLAUDE.md` 참고)
- **커밋 메시지** — Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`).
- **언어** — 모든 코드, 주석, 문서, 커밋 메시지는 한국어로 작성.

---

## ❓ 자주 묻는 질문

**Q. Quick Start 2단계를 건너뛰고 바로 Docker 빌드해도 되나요?**
A. 됩니다. 하지만 `Dockerfile`이 샘플이라 GPU/CUDA가 필요하거나 베이스 이미지가 다른 경우 다시 빌드해야 합니다. 처음에 정렬하는 5분이 나중에 한 시간을 아낍니다.

**Q. `pytest scripts/`가 실패해요.**
A. 컨테이너 안인지 먼저 확인하세요. 호스트에서는 의존성이 없을 수 있습니다.

**Q. 플레이스홀더(`{프로젝트명}` 등)는 꼭 채워야 하나요?**
A. 네. Claude가 매 세션마다 이 파일들을 읽어 컨텍스트를 잡기 때문에, 비어 있으면 잘못된 가정을 합니다.

**Q. `docker compose run --rm harness`는 안 되나요?**
A. 비권장입니다. 이 컨테이너는 TensorBoard 같은 장시간 작업이 계속 살아 있어야 의미가 있는 구조(포트 `6007:6006` 매핑)입니다. `run --rm`은 `exit`하는 순간 모든 작업이 같이 죽기 때문에, **`up -d` + `exec` 조합**을 쓰세요. 여러 터미널에서 동시에 `exec`로 접속할 수도 있습니다.

**Q. `docker compose down`은 언제 해야 하나요?**
A. 작업을 완전히 마쳤을 때만 하세요. 셸에서 빠져나오는 정도라면 `exit`만으로 충분합니다 (컨테이너는 계속 살아 있음). `down`은 컨테이너를 완전히 제거하므로, 안에 띄워둔 TensorBoard·학습 프로세스도 함께 종료됩니다.

---

## 🎯 목적

이 뼈대를 기반으로 각 프로젝트에 맞는 하네스를 추가·확장해 나가는 것을 전제로 합니다.
세부 설계와 결정 사항은 `docs/` 디렉터리의 문서를 참고하세요.
