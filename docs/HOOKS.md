# Claude Code Hooks 가이드

이 문서는 `.claude/settings.json`에 설정하는 **hooks**를 설명합니다.
hooks는 Claude Code가 도구를 호출하거나 세션을 마칠 때 **자동으로 실행되는 셸 명령**입니다 — 멘탈 모델에서 🧬 **신경계(반사)** 에 해당합니다.

---

## 핵심 개념

- 모든 hook은 **stdin으로 JSON 이벤트 페이로드**를 받습니다.
- hook의 **종료 코드**가 Claude의 후속 동작을 결정합니다:

| exit code | 의미 | Claude 동작 |
|-----------|------|------------|
| `0` | 정상 통과 | 그대로 진행 |
| `2` | **차단** | 도구 실행을 막고 stderr 메시지를 Claude에 피드백 |
| 기타 (`1`, `>2`) | 일반 실패 | 경고 출력 후 진행 |

> 💡 `exit 2` + `stderr`로 메시지를 내보내는 것이 **Claude에게 말을 거는 유일한 채널**입니다. stdout이 아닌 **stderr**여야 한다는 점에 주의하세요.

- `matcher`로 어떤 도구·이벤트에 반응할지 좁힐 수 있습니다 (`"Bash"`, `"Edit"`, `"Write|Edit"`, `""`(전체) 등).

---

## 4가지 Hook 이벤트

### 1. `PreToolUse` — 도구 실행 **직전**

**언제:** Claude가 도구(Bash, Edit, Write 등)를 호출하기 직전.
**용도:** 위험 명령 차단, 입력 검증, 정책 강제.
**핵심 권한:** `exit 2`로 도구 실행 자체를 막을 수 있는 **유일한** hook.

**입력 페이로드 예시:**
```json
{
  "session_id": "...",
  "tool_name": "Bash",
  "tool_input": { "command": "rm -rf /" }
}
```

**현재 설정 (이 레포)**:
```json
"PreToolUse": [{
  "matcher": "Bash",
  "hooks": [{
    "type": "command",
    "command": "command=$(python3 -c '...stdin에서 command 추출...'); \
                if echo \"$command\" | grep -qE 'rm\\s+-rf|git\\s+push\\s+--force|git\\s+reset\\s+--hard|DROP\\s+TABLE'; \
                then echo 'BLOCKED: 위험한 명령어가 감지되었습니다.' >&2; exit 2; fi"
  }]
}]
```
→ Bash 명령에서 `rm -rf`, `git push --force`, `git reset --hard`, `DROP TABLE`을 감지하면 **차단**합니다.

**활용 아이디어:**
- 특정 디렉터리(`/etc`, `~/.ssh`) 접근 차단
- production 브랜치 푸시 금지
- 시크릿이 포함된 파일 쓰기 차단
- 패키지 설치 명령 화이트리스트

---

### 2. `PostToolUse` — 도구 실행 **직후**

**언제:** 도구가 성공적으로 끝난 직후.
**용도:** 자동 포맷터/린터 실행, 변경 파일 추적, 테스트 트리거.
**한계:** 이미 실행된 작업을 **되돌리지는 못함** (차단 불가). 후처리 전용.

**입력 페이로드 예시:**
```json
{
  "tool_name": "Edit",
  "tool_input": { "file_path": "/workspace/.../foo.py" },
  "tool_response": { "...": "..." }
}
```

**활용 예시:**
```json
"PostToolUse": [{
  "matcher": "Edit|Write",
  "hooks": [{
    "type": "command",
    "command": "file=$(python3 -c 'import json,sys; print(json.load(sys.stdin)[\"tool_input\"].get(\"file_path\",\"\"))'); \
                if [[ \"$file\" == *.py ]]; then ruff format \"$file\" && ruff check --fix \"$file\"; fi"
  }]
}]
```
→ Python 파일을 편집/생성할 때마다 자동으로 ruff 포맷+린트.

**활용 아이디어:**
- `.py` → `ruff format`, `.ts/.tsx` → `prettier --write`
- 변경된 파일 목록을 로그에 누적
- 테스트 파일이 바뀌면 해당 테스트만 자동 실행

---

### 3. `Notification` — 사용자 알림 시점

**언제:** Claude가 **사용자 입력을 기다려야 할 때** (권한 승인 요청, idle 상태 등).
**용도:** 데스크톱 알림, Slack 메시지, 사운드 재생 등으로 사용자 호출.
**한계:** 흐름 제어 불가 (정보성 hook).

**입력 페이로드 예시:**
```json
{
  "session_id": "...",
  "message": "Claude is waiting for your input"
}
```

**활용 예시:**
```json
"Notification": [{
  "matcher": "",
  "hooks": [{
    "type": "command",
    "command": "msg=$(python3 -c 'import json,sys; print(json.load(sys.stdin).get(\"message\",\"\"))'); \
                notify-send 'Claude Code' \"$msg\""
  }]
}]
```
→ 데스크톱 알림 표시 (Linux). macOS는 `osascript -e 'display notification ...'`, Windows는 `powershell` 사용.

**활용 아이디어:**
- 긴 작업 후 Claude가 멈춰서 권한을 기다릴 때 알림
- 터미널 벨(`printf '\a'`) 또는 사운드 파일 재생
- Slack/Discord 웹훅으로 메시지 전송

---

### 4. `Stop` — 세션 **종료 시**

**언제:** Claude가 한 번의 응답(turn)을 마치고 멈출 때.
**용도:** 자동 테스트 실행, 변경사항 검증, 세션 통계 기록.
**핵심 권한:** `exit 2`로 응답을 막고 **Claude를 다시 작업하게 만들 수 있음** — "테스트 통과 전엔 멈추지 마"를 강제하는 데 활용.

**입력 페이로드 예시:**
```json
{
  "session_id": "...",
  "stop_hook_active": true
}
```

**현재 설정 (이 레포)**:
```json
"Stop": [{
  "matcher": "",
  "hooks": [{
    "type": "command",
    "command": "./scripts/run_stop_hook.sh"
  }]
}]
```

`scripts/run_stop_hook.sh`:
```bash
#!/usr/bin/env bash
python3 scripts/test_execute.py
status=$?
if [ $status -ne 0 ]; then
  echo "Stop hook failed: scripts/test_execute.py exited with status $status" >&2
fi
exit $status
```
→ 매 응답이 끝날 때마다 `test_execute.py`를 돌리고, **실패하면 exit 코드를 그대로 전달**해 Claude가 알아채게 함.

**활용 아이디어:**
- 테스트 자동 실행 (현재 설정)
- 타입 체크(`tsc --noEmit`, `mypy`)
- 변경된 파일이 lint 통과하는지 확인
- 세션 종료 시 git 상태 출력

> ⚠️ **주의:** Stop hook이 매번 무거운 빌드를 돌리면 **턴마다 지연**이 누적됩니다. 빠른 검증만 넣으세요.

---

## Hook 작성 베스트 프랙티스

### 1. JSON 파싱은 `python3 -c`로
```bash
python3 -c 'import json,sys; print(json.load(sys.stdin)["tool_input"].get("command",""))'
```
`jq`보다 의존성이 적고 어디서나 동작합니다.

### 2. **stderr**로 메시지를, **exit 2**로 차단을
Claude는 `stderr`만 읽습니다. `echo "메시지"` (stdout)는 무시됩니다.
```bash
echo "BLOCKED: 이유" >&2 && exit 2
```

### 3. **빠르게** 끝나야 함
모든 hook은 **동기 실행**입니다. 무거운 작업은 백그라운드(`&`)로 던지거나 별도 hook 이벤트(`Stop`)로 옮기세요.

### 4. `matcher`로 좁혀라
`matcher: ""`는 모든 도구·이벤트에 발동합니다. 가능한 한 좁혀서 불필요한 호출을 줄이세요.
```json
"matcher": "Bash"            // Bash만
"matcher": "Edit|Write"      // 정규식: Edit 또는 Write
"matcher": ""                // 전체
```

### 5. **외부 스크립트로 분리**하라
인라인 명령이 길어지면 가독성·테스트성이 떨어집니다. 이 레포의 `Stop` hook처럼 `scripts/`에 셸 스크립트로 분리하세요:
```json
{ "type": "command", "command": "./scripts/my_hook.sh" }
```

### 6. **로컬 설정**과 **공유 설정**을 분리하라
- `.claude/settings.json` — 팀 공유 (git 추적)
- `.claude/settings.local.json` — 개인용 (gitignore 권장)

개인 알림(`notify-send`, Slack DM)은 `settings.local.json`에 넣는 게 깔끔합니다.

---

## 디버깅

hook이 동작하는지 확인하려면:

```bash
# 1) 임시로 hook 자체를 로그 파일에 dump
"command": "tee -a /tmp/hook.log >&2 < /dev/stdin"

# 2) 실행되면 /tmp/hook.log에 페이로드가 쌓임
tail -f /tmp/hook.log
```

또는 hook 시작에 `set -x`를 넣고 stderr를 파일로 redirect.

---

## 이 레포의 hook 설계 의도

| Hook | 목적 | 비유 |
|------|------|------|
| `PreToolUse` (Bash) | **사고 방지** — 위험 명령을 손이 닿기 전에 차단 | 🚧 안전 차단봉 |
| `Stop` | **품질 게이트** — 매 응답 후 테스트로 자동 검증 | 🧪 자동 시약 검사 |

추가하면 좋을 후보:
- `PostToolUse` (Edit|Write) — 자동 포맷터
- `Notification` — 사용자 호출 알림 (개인 환경에 맞게 `settings.local.json`)

---

## 참고

- 공식 문서: [Claude Code Hooks](https://docs.anthropic.com/claude-code/hooks)
- 관련 파일: `.claude/settings.json`, `scripts/run_stop_hook.sh`
- 멘탈 모델 위치: README.md의 🧬 신경계 행
