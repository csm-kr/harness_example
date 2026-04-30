# 프로젝트: {프로젝트명}

## 한 줄 목적
{[docs/PRD.md](./docs/PRD.md) 의 첫 줄과 동일하게}

## 종류 / 기술 스택
- 종류: {web / mobile / backend / ai-ml / data-pipeline / cli-lib / custom}
- 주 언어 + 버전: {예: Python 3.12 / TypeScript 5.x / Kotlin 1.9}
- 프레임워크 + 버전: {예: FastAPI 0.110 / Next.js 15 / React Native 0.74}
- 추가 의존: {예: PostgreSQL 16, Redis 7 / 없음}

## 아키텍처 규칙
- CRITICAL: {절대 지켜야 할 규칙 1 — 이유와 위반 시 동작도 함께}
- CRITICAL: {절대 지켜야 할 규칙 2}
- {일반 규칙들 — CRITICAL 미만}

## 개발 프로세스
- CRITICAL: 새 기능 / 버그 수정은 **테스트를 먼저 작성**하고 통과시키는 구현으로 진행 (TDD).
- 커밋 메시지: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`).
- 브랜치 / PR 정책: {예: PR 리뷰 1인 이상 / 단독 작업 — main 직접 푸시}

## LLM 협업 원칙
**모든 코딩 작업은 [LLM_GUIDE.md](./LLM_GUIDE.md) 의 4원칙을 따른다**:
1. **Think Before Coding** — 가정을 먼저 명시하고, 불확실하면 묻는다.
2. **Simplicity First** — 요청한 것보다 더 만들지 않는다. 추측성 추상화·과한 에러 핸들링 금지.
3. **Surgical Changes** — 요청한 부분만 고친다. 인접 코드를 임의로 "개선"하지 않는다.
4. **Goal-Driven Execution** — 검증 가능한 성공 기준을 먼저 정한다 ("동작한다" 같은 모호한 기준 금지).

## 문서 트라이앵글
어떤 결정을 어디서 내리는지 한 곳에 못박는다 — Claude 와 사람 모두에게 같은 컨텍스트.
- **무엇을 / 왜**: [docs/PRD.md](./docs/PRD.md)
- **어떻게**: [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)
- **왜 이 결정**: [docs/ADR.md](./docs/ADR.md)
- **종류별 추가 docs**: `docs/` 안의 다른 .md 파일 (예: `UI_GUIDE.md`, `API_SPEC.md`, `DATA_CARD.md`)

규칙: 새 결정은 ADR 항목으로. 새 사용자 시나리오는 PRD 갱신. 새 컴포넌트/모듈은 ARCHITECTURE 갱신.

## 주요 명령어
컨테이너 안에서 실행 (호스트에서는 의존성 누락 가능):

```bash
{빌드 / 컴파일}            # 예: npm run build / poetry install / cargo build
{개발 서버 / 실행}         # 예: npm run dev / uvicorn src.main:app --reload
{린트 / 타입 체크}         # 예: npm run lint / ruff check / tsc --noEmit
{테스트}                   # 예: pytest / npm test / cargo test
```

## Hooks
이 레포의 정본 hook 2개 (위험 명령 차단 + Stop 자동 검증) — [docs/HOOKS.md](./docs/HOOKS.md) 참고.
프로젝트별 추가 hook 정책은 [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) 의 "Hook 정책" 섹션.
