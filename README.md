# Chat Application Backend

Discord 스타일의 실시간 채팅 애플리케이션 백엔드

## 주요 기능

- JWT 기반 회원가입 및 로그인
- 사용자 프로필 관리 (마이페이지)
- Discord 스타일 채팅 시스템
  - Server (메인 채팅방)
  - Channel (서브 채팅방)
- WebSocket 기반 실시간 채팅
- 인증 미들웨어 (모든 API 요청에 JWT 토큰 필요)

## 기술 스택

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Real-time Communication**: WebSocket

## 프로젝트 구조

```
backend/
├── app/
│   ├── main.py              # FastAPI 애플리케이션 진입점
│   ├── config.py            # 환경 설정
│   ├── database.py          # 데이터베이스 연결
│   ├── models/              # SQLAlchemy 모델
│   │   ├── user.py
│   │   ├── server.py
│   │   ├── channel.py
│   │   └── message.py
│   ├── schemas/             # Pydantic 스키마
│   │   ├── user.py
│   │   ├── server.py
│   │   ├── channel.py
│   │   └── message.py
│   ├── routers/             # API 라우터
│   │   ├── auth.py          # 회원가입, 로그인
│   │   ├── user.py          # 사용자 프로필
│   │   ├── server.py        # 서버 관리
│   │   ├── channel.py       # 채널 관리
│   │   └── websocket.py     # 실시간 채팅
│   ├── services/            # 비즈니스 로직
│   │   ├── auth.py          # JWT 인증
│   │   └── websocket.py     # WebSocket 관리
│   └── dependencies/        # FastAPI 의존성
│       └── auth.py          # 인증 미들웨어
├── requirements.txt
├── .env.example
└── README.md
```

## 설치 및 실행

### 1. 저장소 클론 및 가상환경 설정

```bash
# Python 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 값을 설정합니다:

```bash
cp .env.example .env
```

`.env` 파일 내용:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/chatapp_db
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. PostgreSQL 데이터베이스 생성

```bash
# PostgreSQL에 접속
psql -U postgres

# 데이터베이스 생성
CREATE DATABASE chatapp_db;

# 종료
\q
```

### 5. 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 실행되면 다음 주소에서 접근할 수 있습니다:
- API: http://localhost:8000
- Swagger 문서: http://localhost:8000/docs
- ReDoc 문서: http://localhost:8000/redoc

## API 엔드포인트

### 인증 (Authentication)

- `POST /auth/register` - 회원가입
- `POST /auth/login` - 로그인 (JWT 토큰 반환)

### 사용자 (User)

- `GET /users/me` - 내 프로필 조회
- `PUT /users/me` - 내 프로필 수정
- `GET /users/{user_id}` - 다른 사용자 프로필 조회

### 서버 (Server - 메인 채팅방)

- `POST /servers/` - 서버 생성
- `GET /servers/` - 내가 속한 서버 목록
- `GET /servers/{server_id}` - 서버 상세 정보 (채널 포함)
- `PUT /servers/{server_id}` - 서버 정보 수정 (소유자만)
- `DELETE /servers/{server_id}` - 서버 삭제 (소유자만)
- `POST /servers/{server_id}/join` - 서버 참가
- `POST /servers/{server_id}/leave` - 서버 나가기

### 채널 (Channel - 서브 채팅방)

- `POST /channels/` - 채널 생성 (서버 소유자만)
- `GET /channels/{channel_id}` - 채널 정보 조회
- `PUT /channels/{channel_id}` - 채널 정보 수정 (서버 소유자만)
- `DELETE /channels/{channel_id}` - 채널 삭제 (서버 소유자만)
- `GET /channels/{channel_id}/messages` - 채널 메시지 목록

### WebSocket

- `WS /ws/{channel_id}?token={jwt_token}` - 채널 실시간 채팅

## 사용 예시

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

### 2. 로그인

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

### 3. 서버 생성 (인증 필요)

```bash
curl -X POST "http://localhost:8000/servers/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Server",
    "description": "My first server"
  }'
```

### 4. 채널 생성 (인증 필요)

```bash
curl -X POST "http://localhost:8000/channels/" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "general",
    "description": "General discussion",
    "server_id": 1
  }'
```

### 5. WebSocket 채팅 연결 (JavaScript 예시)

```javascript
const token = "YOUR_JWT_TOKEN";
const channelId = 1;
const ws = new WebSocket(`ws://localhost:8000/ws/${channelId}?token=${token}`);

ws.onopen = () => {
  console.log("Connected to chat");

  // 메시지 전송
  ws.send(JSON.stringify({
    content: "Hello, World!"
  }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log(`${message.author_username}: ${message.content}`);
};

ws.onclose = () => {
  console.log("Disconnected from chat");
};
```

## 데이터베이스 스키마

### Users
- id (PK)
- username (unique)
- email (unique)
- hashed_password
- display_name
- bio
- avatar_url
- created_at
- updated_at

### Servers
- id (PK)
- name
- description
- icon_url
- owner_id (FK → Users)
- created_at
- updated_at

### Channels
- id (PK)
- name
- description
- server_id (FK → Servers)
- created_at
- updated_at

### Messages
- id (PK)
- content
- channel_id (FK → Channels)
- author_id (FK → Users)
- created_at
- updated_at

### user_servers (Many-to-Many)
- user_id (FK → Users)
- server_id (FK → Servers)

## 보안

- 모든 비밀번호는 bcrypt로 해싱되어 저장됩니다
- JWT 토큰을 사용한 stateless 인증
- 모든 API 엔드포인트는 인증이 필요합니다 (인증 제외)
- WebSocket 연결도 JWT 토큰 검증이 필요합니다

## 개발

### 개발 모드 실행

```bash
uvicorn app.main:app --reload
```

### 테스트

```bash
pytest
```

## 라이선스

MIT