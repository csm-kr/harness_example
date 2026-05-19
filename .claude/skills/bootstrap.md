**하네스 정본 위에 프로젝트 종류를 정하고 종류별 docs 뼈대를 `docs/` 로 깔아주는 가벼운 부트스트래퍼다.**

bootstrap 은 본문을 채우지 않는다. 종류별 템플릿(`PRD/ARCHITECTURE/ADR` 외 종류 고유 문서들)을 `docs/` 로 복사할 뿐 — `{}` 플레이스홀더는 그대로 남겨두고, 사용자가 Claude 와 함께 본문에서 결정한다.

```
bootstrap   →  docker-init   →  harness   →  execute.py
(틀 깔기)        (컨테이너)        (계획)         (실행)
```

책임 분리:
- **결정의 깊이(CRITICAL, 위험, 트레이드오프)** → 사용자가 PRD/ARCH/ADR 본문에서 직접.
- **Dockerfile / compose** → `docker-init`.
- **phase/step 설계, 실제 코드** → `harness` / `execute.py`.

bootstrap 은 한 줄도 본문을 작성하지 않는다.

> **이 스킬도 [LLM_GUIDE.md](../../LLM_GUIDE.md) 의 4원칙을 따른다.** 특히 (1) 가정을 명시하고 묻기, (4) 답이 모호하면 사용자에게 **대안을 제시**하기 — bootstrap 의 모든 질문은 이 패턴을 쓴다.

---

## 핵심 패턴 — 대안 제시 (Always Offer Options)

사용자가 막힐 만한 자리에서 LLM 이 묵묵히 추측하지 마라. **2~4개의 합리적 대안을 제시**하고 사용자가 고르게 한다. 이 패턴은 bootstrap 의 모든 질문에 적용된다.

형식:
```
질문 한 줄.
  (a) 옵션 A — 짧은 설명 / 어울리는 경우
  (b) 옵션 B — 짧은 설명 / 어울리는 경우
  (c) 옵션 C — 짧은 설명 / 어울리는 경우
  (d) 직접 입력 / 다른 의견 — 자유 답변
```

대안의 첫 항목은 **bootstrap 이 추천하는 것**으로 두되, 추천이 강요로 보이지 않게 한다.

---

## 절차

### 1. 인프라 점검

다음 정본 파일이 모두 있어야 한다.

| 카테고리 | 파일 |
|---------|------|
| 스킬 | `.claude/skills/{bootstrap,harness,docker-init,review}.md` |
| 종류별 템플릿 정본 | `.claude/skills/templates/{web,mobile,backend,ai-ml,data-pipeline,cli-lib}/*.md` |
| 공용 템플릿 정본 | `.claude/skills/templates/PRD_VIEW.md` (PRD 검수 13 View) |
| 훅 | `.claude/settings.json` |
| 스크립트 | `scripts/{execute,test_execute}.py` |
| 컨테이너 참고 예시 | `.claude/skills/docker_examples/{Dockerfile,docker-compose.yml}` |
| 헌법 / 협업 가이드 | `CLAUDE.md`, `LLM_GUIDE.md` |
| 도메인 docs | `docs/{PRD,ARCHITECTURE,ADR,HOOKS}.md` |

누락이 있으면 표로 보여주고 종료 — 재클론 안내(`git clone <레포 URL> .` → `rm -rf .git` → `git init`).
모두 있으면 한 줄 보고 후 다음 단계: "인프라 정본 ✅ 모두 확인됨."

---

### 2. 짧은 발견 대화 (3 문항, 대안 제시)

**한 항목씩 순서대로** 묻는다. 한꺼번에 묻지 마라. 각 답이 다음 질문의 컨텍스트가 된다.

#### 2-1. 프로젝트명
- kebab-case 권장 — 디렉터리·이미지·컨테이너명에 사용. 한글 금지.
- 좋은 답: `team-notes-v2`, `receipt-parser`. 나쁜 답: `MyProject`, `temp123`.
- 답이 안 떠오르면 한 줄 목적(2-2)을 먼저 받고 거기서 슬러그 후보 3개를 제시.

#### 2-2. 한 줄 목적
- 동사 + 대상이 들어간 한 문장. PRD 첫 줄에 그대로 들어감.
- 좋은 답: "사내 영수증을 자동 요약해 회계 시스템에 입력한다."
- 나쁜 답 (추상·형용사만): "효율을 높인다", "AI 도구". → 다시 한 번 파고들되, 그래도 막막하면 **비슷한 프로젝트의 한 줄 목적 3개** 를 보여주고 (a/b/c) 또는 (d) 직접 입력으로 선택받는다.

#### 2-3. 종류 결정
1~2 답을 보고 bootstrap 이 1차 추천 + 합리적 대안 1~2개 + (d) 다른 의견 형태로 제시한다.

종류 매트릭스 (전체):

| 코드 | 이름 | 대표 예시 | 대표 신호 |
|------|------|----------|----------|
| `web` | 웹 / 풀스택 | Next.js, React, SvelteKit, 정적 사이트 | "사용자가 브라우저로 접근" |
| `mobile` | 모바일 앱 | React Native, Flutter, 네이티브 | "iOS·Android 앱" |
| `backend` | 백엔드 API 서버 | REST/gRPC/GraphQL, FastAPI, Express | "다른 시스템이 호출" |
| `ai-ml` | AI / ML 개발 | 학습/추론/평가, PyTorch, TF | "모델 학습 / 데이터셋" |
| `data-pipeline` | 데이터 파이프라인 | ETL/스트리밍, Airflow, dbt | "정기적으로 데이터를 옮기고 변환" |
| `cli-lib` | CLI / 라이브러리 | npm, pip, cargo 배포물 | "터미널 도구 / import 해서 사용" |
| `custom` | 기타 | 데스크톱(Tauri/Electron), 게임, 임베디드, IoT | 위 6개에 안 맞음 |

질문 예시 (2-2 답이 "사내 영수증 자동 요약"인 경우):
```
한 줄 목적으로 보면 모델 학습·추론이 핵심으로 보입니다. 어울리는 종류 후보:
  (a) ai-ml — 모델 학습/추론/평가가 중심 (추천)
  (b) backend — 외부에서 호출하는 추론 API 가 더 큰 비중이라면
  (c) data-pipeline — 정기 배치로 영수증을 모아 처리한다면
  (d) 다른 종류 / custom — 위에 안 맞으면 가장 가까운 것 + 한 줄 설명
```

**`custom` 선택 시** — 가장 가까운 base 종류를 (a/b/c) 로 다시 제시받아 그 템플릿을 그대로 깐다. bootstrap 은 새 템플릿을 즉흥 생성하지 않는다. 사용자에게 한 줄 안내: "ARCHITECTURE.md 의 '디렉터리 구조'와 '외부 의존' 섹션은 직접 다시 작성하세요."

더 이상 캐묻지 않는다. 위험 매핑·CRITICAL 도출·6렌즈는 본문 작성 단계의 것이다.

---

### 3. 종류별 docs 를 `docs/` 로 적용 (핵심 동작)

**bootstrap 의 본 작업.** `.claude/skills/templates/{type}/` 의 **모든 `.md` 파일**을 `docs/` 로 디렉터리 통째 복사한다 (이름 보존). 종류별로 파일 개수·이름이 다르다 — bootstrap 은 디렉터리를 스캔만 하고 본문은 그대로다.

추가로 **공용 파일** `.claude/skills/templates/PRD_VIEW.md` 를 `docs/PRD_VIEW.md` 로 함께 복사한다. 이 파일은 종류 무관 PRD 검수 13 View 렌즈로, 사용자가 `PRD.md` 본문을 채울 때 체크리스트로 사용한다.

종류별로 깔리는 docs 예 (현재 정본 기준, **공용 PRD_VIEW.md 포함**):
- `web`: PRD, ARCHITECTURE, ADR, UI_GUIDE, ACCESSIBILITY + PRD_VIEW (6개)
- `mobile`: PRD, ARCHITECTURE, ADR, RELEASE, PUSH + PRD_VIEW (6개)
- `backend`: PRD, ARCHITECTURE, ADR, API_SPEC, MIGRATIONS + PRD_VIEW (6개)
- `ai-ml`: PRD, ARCHITECTURE, ADR, EXPERIMENTS, DATA_CARD, MODEL_CARD, EVAL_PROTOCOL + PRD_VIEW (8개)
- `data-pipeline`: PRD, ARCHITECTURE, ADR, DATA_CONTRACTS, RUNBOOK + PRD_VIEW (6개)
- `cli-lib`: PRD, ARCHITECTURE, ADR, API_REFERENCE, MIGRATION + PRD_VIEW (6개)

**복사 전 — 현재 `docs/` 상태 판단**:
- `docs/{PRD,ARCHITECTURE,ADR}.md` 안 `{` 가 5개 이상 + 30줄 이하 → **정본 상태**로 판단 → 무백업 덮어쓰기 (`docs/PRD_VIEW.md` 도 함께 덮어쓰기).
- 그 외 → **사용자 콘텐츠 의심** → 사용자에게 다음 대안 제시:
  ```
  기존 docs 에 콘텐츠가 있어 보입니다. 어떻게 할까요?
    (a) docs/_archive/{ts}/ 로 이동 후 새 템플릿 깔기 (추천)
    (b) 통째 덮어쓰기 — 기존 내용은 사라짐
    (c) 취소 — bootstrap 종료
  ```
  (a) 선택 시 `docs/_archive/{YYYYMMDD-HHMMSS}/` 로 옮기고 새 템플릿 복사.

**손대지 않는 것** (사용자 답에 따라 절대 바꾸지 마라):
- `CLAUDE.md` — 정본 유지. 플레이스홀더는 사용자가 본문 결정 후 직접 채운다.
- `LLM_GUIDE.md`, `docs/HOOKS.md` — 정본 유지.
- `.claude/settings.json`, `.claude/skills/*` (참고 예시 `.claude/skills/docker_examples/` 포함), `scripts/*`.

**부수**: `phases/index.json` 이 없으면 `{"phases": []}` 로 생성. 있으면 손대지 마라.

---

### 4. 점검 보고

```
[bootstrap 결과 — {프로젝트명} / 종류: {type}]
- 인프라 정본 (.claude, scripts, settings.json, HOOKS.md, LLM_GUIDE.md): ✅ 확인
- docs/ 깔린 파일: {N}개 (PRD, ARCHITECTURE, ADR, {추가 docs 목록}, PRD_VIEW)
- PRD_VIEW.md: 🆕 13 View 검수 렌즈 (공용 — PRD 본문 작성 시 체크리스트로 사용)
- CLAUDE.md: 🔒 정본 유지 (사용자가 직접 채우세요)
- phases/index.json: 🆕 빈 배열 생성 / 🔒 기존 유지
- docs/_archive/{ts}/: 🆕 기존 docs 이동됨 (해당 시에만)
```

⚠️ 가 있으면 (예: archive 이동, custom 분기 안내) 한 줄로 따로 강조한다.

---

### 5. 다음 단계 안내

```
다음 단계:
1. docs/PRD.md → ARCHITECTURE.md → ADR.md 순서로 본문을 채우세요. Claude 와 함께 작업하면 빠릅니다.
   (각 파일 맨 위 "이 문서가 답하는 질문" 헤더가 어디에 무엇을 적을지 안내합니다.)
   👉 **PRD.md 본문을 채울 때는 `docs/PRD_VIEW.md` 의 13 View 질문을 체크리스트로 함께 보세요.**
      각 View 의 "도메인 적용 가이드" 항목을 이 프로젝트 도메인에 맞게 구체화하면 빠진 관점이 줄어듭니다.
2. 종류별 추가 docs 도 같은 방식으로 채우세요 (예: web 의 UI_GUIDE.md, ai-ml 의 DATA_CARD.md).
3. 채운 뒤 새 메시지에서 /docker-init 을 호출하세요. 종류·스택에 맞는 격리 환경 일체(`env_docker/{Dockerfile,docker-compose.yml,...}`)를 한 폴더 안에 만듭니다 — 호스트는 Docker 만 있다고 가정합니다.
4. `docker compose -f env_docker/docker-compose.yml up -d --build && docker compose -f env_docker/docker-compose.yml exec dev bash` (또는 `make up && make shell`) 로 컨테이너 진입. 셸 안에서 `claude` 를 실행해 이후 작업을 컨테이너 안에서 합니다.
5. /harness 로 첫 phase 를 설계하세요.
```

끝. 첫 phase 후보 제안·Docker 인계 요약·산출물 일람표 같은 무거운 마무리는 하지 않는다.

---

## 금지 사항

- **본문을 채우지 마라.** PRD/ARCHITECTURE/ADR 의 `{}` 플레이스홀더는 사용자가 직접 채운다.
- **묵묵히 추측하지 마라.** 답이 모호한 자리에서는 항상 대안 2~4개를 제시한다 ([LLM_GUIDE.md](../../LLM_GUIDE.md) 1·4 원칙).
- **정본 파일을 사용자 답에 따라 바꾸지 마라.** `.claude/settings.json`, `.claude/skills/*` (참고 예시 `.claude/skills/docker_examples/` 포함), `scripts/*`, `docs/HOOKS.md`, `LLM_GUIDE.md`.
- **CLAUDE.md 의 플레이스홀더를 채우지 마라.** 결정의 깊이는 본문 작성 단계의 것이다.
- **Dockerfile / compose 를 만들지 마라.** `docker-init` 책임이다.
- **6렌즈, CRITICAL 능동 도출, 위험 매핑, 자체 검증 10항목 같은 무거운 절차를 부활시키지 마라.** 가벼운 스킬 의도와 정면 충돌한다.
- **새 템플릿을 즉흥 생성하지 마라.** `custom` 분기조차 가장 가까운 base 를 추천하고 그대로 깐다.
- **기존 사용자 콘텐츠를 묻지 않고 덮어쓰지 마라.** 휴리스틱으로 의심되면 archive 옵션을 제시한다.
- **한국어로 질문하라.** 사용자의 글로벌 규칙.
- **한꺼번에 묻지 마라.** 발견 대화 3문항을 순서대로.
