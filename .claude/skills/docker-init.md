# docker-init

프로젝트의 Docker 개발 환경과 하네스를 초기화한다.

## 절차

### 1. 정보 수집

아래 항목을 **순서대로 하나씩** 질문하라. 한꺼번에 묻지 말 것.

1. **프로젝트명** — 컨테이너명·디렉토리명에 사용됨
2. **기술 스택** — 구체적인 버전까지 (예: Node.js 22 + TypeScript, Python 3.12 + FastAPI, Next.js 15)
3. **앱 포트** — 컨테이너가 expose할 포트 (스택에 따라 기본값 제안)
4. **추가 서비스** — 필요한 외부 서비스 (예: PostgreSQL 16, Redis 7, 없음)

### 2. 파일 생성

수집한 정보를 바탕으로 아래 파일을 생성한다.

#### `Dockerfile`

- 기술 스택에 맞는 공식 베이스 이미지 사용
- 의존성 설치를 앞 레이어로 분리해 빌드 캐시 최적화
- 개발 모드 실행 CMD (핫리로드 포함)
- 불필요한 파일 제외 `.dockerignore` 함께 생성

#### `docker-compose.yml`

- `app` 서비스: Dockerfile 빌드, 소스 볼륨 마운트, 포트 바인딩
- 선택한 추가 서비스: 공식 이미지, named volume, healthcheck
- `env_file: .env` 참조
- 서비스 간 depends_on 연결

#### `.env.example`

- DB URL, 포트, 시크릿 키 등 필요한 환경변수 목록
- 실제 값은 비워두고 설명 주석 포함

#### `CLAUDE.md` 업데이트

현재 프로젝트의 `CLAUDE.md`를 열어 아래 섹션을 실제 값으로 채운다:

- `기술 스택` — 결정된 스택과 버전
- `명령어` — docker compose 기반으로 교체:

```
docker compose up --build   # 개발 서버
docker compose run --rm app <lint-cmd>   # 린트
docker compose run --rm app <test-cmd>   # 테스트
```

#### `.claude/settings.json` 업데이트

Stop hook의 테스트 명령어를 Docker 환경에 맞게 수정:

```json
"command": "docker compose run --rm app <test-cmd> 2>&1"
```

#### 하네스 구조 초기화

- `phases/` 디렉토리 생성
- `phases/index.json` 생성:

```json
{
  "phases": []
}
```

### 3. 완료 안내

생성된 파일 목록을 출력하고 시작 방법을 안내한다:

```bash
cp .env.example .env   # 환경변수 설정
docker compose up --build   # 개발 서버 시작
```

## 주의사항

- `.env`는 생성하지 마라. `.env.example`만 생성한다. 이유: 실제 시크릿이 git에 커밋되는 것을 방지.
- `CLAUDE.md`의 `{중괄호}` 플레이스홀더는 반드시 실제 값으로 교체하라. 이유: 플레이스홀더가 남으면 이후 Claude 세션이 잘못된 컨텍스트를 읽는다.
- 기존 `Dockerfile`이나 `docker-compose.yml`이 있으면 덮어쓰기 전에 사용자에게 확인하라.
