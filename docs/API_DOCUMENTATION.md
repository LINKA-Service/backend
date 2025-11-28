# API Documentation

## 개요

Discord 스타일의 실시간 채팅 애플리케이션 API

- **Base URL**: `http://localhost:8000`
- **인증 방식**: JWT Bearer Token
- **응답 형식**: JSON

---

## 인증 (Authentication)

모든 API 엔드포인트는 `/auth/register`와 `/auth/login`을 제외하고 JWT 토큰이 필요합니다.

### 인증 헤더 형식
```
Authorization: Bearer {access_token}
```

---

## 엔드포인트 목록

### 1. 인증 (Auth)

#### 1.1 회원가입
```http
POST /auth/register
```

**요청 본문**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**응답 (201 Created)**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "display_name": "testuser",
  "bio": null,
  "avatar_url": null,
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T10:30:00"
}
```

**에러**
- `400 Bad Request`: Use  rname 또는 Email이 이미 존재함

---

#### 1.2 로그인
```http
POST /auth/login
```

**요청 본문** (application/x-www-form-urlencoded)
```
username=testuser&password=password123
```

**응답 (200 OK)**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**에러**
- `401 Unauthorized`: 잘못된 username 또는 password

---

### 2. 사용자 (Users)

#### 2.1 내 프로필 조회
```http
GET /users/me
```

**인증**: 필수

**응답 (200 OK)**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "display_name": "Test User",
  "bio": "Hello, I'm a test user!",
  "avatar_url": "https://example.com/avatar.jpg",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T11:00:00"
}
```

---

#### 2.2 내 프로필 수정
```http
PUT /users/me
```

**인증**: 필수

**요청 본문**
```json
{
  "display_name": "New Display Name",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "password": "newpassword123"
}
```

> 모든 필드는 선택사항입니다. 수정하려는 필드만 포함하면 됩니다.

**응답 (200 OK)**
```json
{
  "id": 1,
  "username": "testuser",
  "email": "test@example.com",
  "display_name": "New Display Name",
  "bio": "Updated bio",
  "avatar_url": "https://example.com/new-avatar.jpg",
  "created_at": "2025-01-15T10:30:00",
  "updated_at": "2025-01-15T11:30:00"
}
```

---

#### 2.3 다른 사용자 프로필 조회
```http
GET /users/{user_id}
```

**인증**: 필수

**경로 파라미터**
- `user_id` (integer): 조회할 사용자 ID

**응답 (200 OK)**
```json
{
  "id": 2,
  "username": "otheruser",
  "email": "other@example.com",
  "display_name": "Other User",
  "bio": "Another user",
  "avatar_url": null,
  "created_at": "2025-01-14T09:00:00",
  "updated_at": "2025-01-14T09:00:00"
}
```

**에러**
- `404 Not Found`: 사용자를 찾을 수 없음

---

### 3. 서버 (Servers)

#### 3.1 서버 생성
```http
POST /servers/
```

**인증**: 필수

**요청 본문**
```json
{
  "name": "My Server",
  "description": "This is my awesome server",
  "icon_url": "https://example.com/server-icon.jpg"
}
```

> `description`과 `icon_url`은 선택사항입니다.

**응답 (201 Created)**
```json
{
  "id": 1,
  "name": "My Server",
  "description": "This is my awesome server",
  "icon_url": "https://example.com/server-icon.jpg",
  "owner_id": 1,
  "created_at": "2025-01-15T12:00:00",
  "updated_at": "2025-01-15T12:00:00"
}
```

---

#### 3.2 내가 속한 서버 목록 조회
```http
GET /servers/
```

**인증**: 필수

**응답 (200 OK)**
```json
[
  {
    "id": 1,
    "name": "My Server",
    "description": "This is my awesome server",
    "icon_url": "https://example.com/server-icon.jpg",
    "owner_id": 1,
    "created_at": "2025-01-15T12:00:00",
    "updated_at": "2025-01-15T12:00:00"
  },
  {
    "id": 2,
    "name": "Another Server",
    "description": "Another server I joined",
    "icon_url": null,
    "owner_id": 2,
    "created_at": "2025-01-14T10:00:00",
    "updated_at": "2025-01-14T10:00:00"
  }
]
```

---

#### 3.3 서버 상세 정보 조회 (채널 포함)
```http
GET /servers/{server_id}
```

**인증**: 필수

**경로 파라미터**
- `server_id` (integer): 서버 ID

**응답 (200 OK)**
```json
{
  "id": 1,
  "name": "My Server",
  "description": "This is my awesome server",
  "icon_url": "https://example.com/server-icon.jpg",
  "owner_id": 1,
  "created_at": "2025-01-15T12:00:00",
  "updated_at": "2025-01-15T12:00:00",
  "channels": [
    {
      "id": 1,
      "name": "general",
      "description": "General discussion",
      "server_id": 1,
      "created_at": "2025-01-15T12:05:00",
      "updated_at": "2025-01-15T12:05:00"
    },
    {
      "id": 2,
      "name": "random",
      "description": "Random stuff",
      "server_id": 1,
      "created_at": "2025-01-15T12:10:00",
      "updated_at": "2025-01-15T12:10:00"
    }
  ]
}
```

**에러**
- `404 Not Found`: 서버를 찾을 수 없음
- `403 Forbidden`: 서버 멤버가 아님

---

#### 3.4 서버 정보 수정
```http
PUT /servers/{server_id}
```

**인증**: 필수 (서버 소유자만)

**경로 파라미터**
- `server_id` (integer): 서버 ID

**요청 본문**
```json
{
  "name": "Updated Server Name",
  "description": "Updated description",
  "icon_url": "https://example.com/new-icon.jpg"
}
```

> 모든 필드는 선택사항입니다.

**응답 (200 OK)**
```json
{
  "id": 1,
  "name": "Updated Server Name",
  "description": "Updated description",
  "icon_url": "https://example.com/new-icon.jpg",
  "owner_id": 1,
  "created_at": "2025-01-15T12:00:00",
  "updated_at": "2025-01-15T13:00:00"
}
```

**에러**
- `404 Not Found`: 서버를 찾을 수 없음
- `403 Forbidden`: 서버 소유자가 아님

---

#### 3.5 서버 삭제
```http
DELETE /servers/{server_id}
```

**인증**: 필수 (서버 소유자만)

**경로 파라미터**
- `server_id` (integer): 서버 ID

**응답 (204 No Content)**

**에러**
- `404 Not Found`: 서버를 찾을 수 없음
- `403 Forbidden`: 서버 소유자가 아님

---

#### 3.6 서버 참가
```http
POST /servers/{server_id}/join
```

**인증**: 필수

**경로 파라미터**
- `server_id` (integer): 서버 ID

**응답 (200 OK)**
```json
{
  "id": 1,
  "name": "My Server",
  "description": "This is my awesome server",
  "icon_url": "https://example.com/server-icon.jpg",
  "owner_id": 1,
  "created_at": "2025-01-15T12:00:00",
  "updated_at": "2025-01-15T12:00:00"
}
```

**에러**
- `404 Not Found`: 서버를 찾을 수 없음
- `400 Bad Request`: 이미 서버 멤버임

---

#### 3.7 서버 나가기
```http
POST /servers/{server_id}/leave
```

**인증**: 필수

**경로 파라미터**
- `server_id` (integer): 서버 ID

**응답 (204 No Content)**

**에러**
- `404 Not Found`: 서버를 찾을 수 없음
- `400 Bad Request`: 서버 멤버가 아니거나 서버 소유자는 나갈 수 없음

---

### 4. 채널 (Channels)

#### 4.1 채널 생성
```http
POST /channels/
```

**인증**: 필수 (서버 소유자만)

**요청 본문**
```json
{
  "name": "general",
  "description": "General discussion",
  "server_id": 1
}
```

> `description`은 선택사항입니다.

**응답 (201 Created)**
```json
{
  "id": 1,
  "name": "general",
  "description": "General discussion",
  "server_id": 1,
  "created_at": "2025-01-15T12:05:00",
  "updated_at": "2025-01-15T12:05:00"
}
```

**에러**
- `404 Not Found`: 서버를 찾을 수 없음
- `403 Forbidden`: 서버 소유자가 아님

---

#### 4.2 채널 정보 조회
```http
GET /channels/{channel_id}
```

**인증**: 필수

**경로 파라미터**
- `channel_id` (integer): 채널 ID

**응답 (200 OK)**
```json
{
  "id": 1,
  "name": "general",
  "description": "General discussion",
  "server_id": 1,
  "created_at": "2025-01-15T12:05:00",
  "updated_at": "2025-01-15T12:05:00"
}
```

**에러**
- `404 Not Found`: 채널을 찾을 수 없음
- `403 Forbidden`: 서버 멤버가 아님

---

#### 4.3 채널 정보 수정
```http
PUT /channels/{channel_id}
```

**인증**: 필수 (서버 소유자만)

**경로 파라미터**
- `channel_id` (integer): 채널 ID

**요청 본문**
```json
{
  "name": "updated-general",
  "description": "Updated description"
}
```

> 모든 필드는 선택사항입니다.

**응답 (200 OK)**
```json
{
  "id": 1,
  "name": "updated-general",
  "description": "Updated description",
  "server_id": 1,
  "created_at": "2025-01-15T12:05:00",
  "updated_at": "2025-01-15T13:05:00"
}
```

**에러**
- `404 Not Found`: 채널을 찾을 수 없음
- `403 Forbidden`: 서버 소유자가 아님

---

#### 4.4 채널 삭제
```http
DELETE /channels/{channel_id}
```

**인증**: 필수 (서버 소유자만)

**경로 파라미터**
- `channel_id` (integer): 채널 ID

**응답 (204 No Content)**

**에러**
- `404 Not Found`: 채널을 찾을 수 없음
- `403 Forbidden`: 서버 소유자가 아님

---

#### 4.5 채널 메시지 목록 조회
```http
GET /channels/{channel_id}/messages
```

**인증**: 필수

**경로 파라미터**
- `channel_id` (integer): 채널 ID

**쿼리 파라미터**
- `limit` (integer, optional): 반환할 메시지 개수 (기본값: 50)
- `offset` (integer, optional): 건너뛸 메시지 개수 (기본값: 0)

**예시**
```
GET /channels/1/messages?limit=20&offset=0
```

**응답 (200 OK)**
```json
[
  {
    "id": 1,
    "content": "Hello, World!",
    "channel_id": 1,
    "author_id": 1,
    "author_username": "testuser",
    "created_at": "2025-01-15T12:30:00",
    "updated_at": "2025-01-15T12:30:00"
  },
  {
    "id": 2,
    "content": "How are you?",
    "channel_id": 1,
    "author_id": 2,
    "author_username": "otheruser",
    "created_at": "2025-01-15T12:31:00",
    "updated_at": "2025-01-15T12:31:00"
  }
]
```

**에러**
- `404 Not Found`: 채널을 찾을 수 없음
- `403 Forbidden`: 서버 멤버가 아님

---

### 5. WebSocket (실시간 채팅)

#### 5.1 WebSocket 연결
```
WS /ws/{channel_id}?token={jwt_token}
```

**경로 파라미터**
- `channel_id` (integer): 채널 ID

**쿼리 파라미터**
- `token` (string): JWT 액세스 토큰

**예시 URL**
```
ws://localhost:8000/ws/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

#### 5.2 메시지 전송 (Client → Server)

**형식**
```json
{
  "content": "Hello, World!"
}
```

---

#### 5.3 메시지 수신 (Server → Client)

**형식**
```json
{
  "id": 1,
  "content": "Hello, World!",
  "channel_id": 1,
  "author_id": 1,
  "author_username": "testuser",
  "created_at": "2025-01-15T12:30:00"
}
```

---

#### 5.4 JavaScript 예시

```javascript
const token = "your_jwt_token_here";
const channelId = 1;

// WebSocket 연결
const ws = new WebSocket(`ws://localhost:8000/ws/${channelId}?token=${token}`);

// 연결 성공
ws.onopen = () => {
  console.log("Connected to chat");

  // 메시지 전송
  ws.send(JSON.stringify({
    content: "Hello, World!"
  }));
};

// 메시지 수신
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`[${message.created_at}] ${message.author_username}: ${message.content}`);
};

// 에러 처리
ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

// 연결 종료
ws.onclose = () => {
  console.log("Disconnected from chat");
};
```

---

## 에러 코드

| 상태 코드 | 설명 |
|-----------|------|
| 200 OK | 성공 |
| 201 Created | 리소스 생성 성공 |
| 204 No Content | 성공 (응답 본문 없음) |
| 400 Bad Request | 잘못된 요청 |
| 401 Unauthorized | 인증 실패 |
| 403 Forbidden | 권한 없음 |
| 404 Not Found | 리소스를 찾을 수 없음 |
| 500 Internal Server Error | 서버 에러 |

---

## 에러 응답 형식

```json
{
  "detail": "에러 메시지"
}
```

**예시**
```json
{
  "detail": "Username already registered"
}
```

---

## 인증 플로우

### 1. 회원가입
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
  }'
```

### 2. 로그인 및 토큰 획득
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=password123"
```

응답:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. 인증이 필요한 API 호출
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## 사용 시나리오

### 시나리오 1: 서버 생성 및 채널 추가

1. 회원가입 및 로그인
2. 서버 생성 (`POST /servers/`)
3. 채널 생성 (`POST /channels/`)
4. WebSocket으로 채팅 시작

### 시나리오 2: 기존 서버 참가

1. 회원가입 및 로그인
2. 서버 참가 (`POST /servers/{server_id}/join`)
3. 서버 정보 조회 (`GET /servers/{server_id}`)
4. 채널 선택 및 WebSocket 연결

---

## 참고사항

- 모든 날짜/시간은 UTC 기준입니다
- JWT 토큰 만료 시간은 기본 30분입니다 (설정 변경 가능)
- WebSocket 연결은 JWT 토큰 검증 후 유지됩니다
- 서버 소유자만 채널을 생성/수정/삭제할 수 있습니다
- 서버 소유자는 서버를 나갈 수 없으며, 삭제만 가능합니다
