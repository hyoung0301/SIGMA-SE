import os
import uuid
from typing import Optional, List, Any
from datetime import datetime, date
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from cafeteria_crawl_menu import main as crawl_menu

# =========================
# 환경 변수 / DB
# =========================
load_dotenv()

PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5433")
PGDATABASE = os.getenv("PGDATABASE", "chatbot")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "")

DATABASE_URL = f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# =========================
# 공용 DB 헬퍼
# =========================
def fetch_all(sql: str, params: dict | None = None) -> list[dict]:
    with engine.connect() as conn:
        return conn.execute(text(sql), params or {}).mappings().all()

def fetch_one(sql: str, params: dict | None = None) -> dict | None:
    with engine.connect() as conn:
        row = conn.execute(text(sql), params or {}).mappings().first()
        return row

# =========================
# FastAPI 설정
# =========================
scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 서버 시작")
    try:
        crawl_menu()
    except Exception as e:
        print("❌ 크롤링 실패:", e)

    scheduler.add_job(crawl_menu, IntervalTrigger(days=3), id="cafeteria", replace_existing=True)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(title="Campus API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# 자동 테이블 GET API
# =========================
AUTO_TABLES = [
    "users",
    "subject",
    "books",
    "departments",
    "library_rooms",
    "library_loans",
    "library_seat_status",
    "kb_chunks",
    "kb_documents",
    "chat_sessions",
    "chat_messages",
    "cafeterias",
    "academic_events",
    "faqs",
    "faq_feedback",
    "notification_logs",
    "notification_subscriptions",
    "class_update",
    "cafeterias_menus",
]

def register_table_endpoint(table: str):
    @app.get(f"/{table}")
    def list_table( _table: str = table):
        return fetch_all(
            f"SELECT * FROM {_table}",
        )

for t in AUTO_TABLES:
    register_table_endpoint(t)


@app.get("/subject/filter")
def subject_filter():
    return fetch_all("""
        SELECT *
        FROM subject
        WHERE dept IN ('컴퓨터공학과', '교양과정부')
        ORDER BY dept, grade, code
    """)


# =========================
# Pydantic 모델 (특수 API용)
# =========================

class SignupIn(BaseModel):
    name: str
    studentId: str
    email: str
    password: str
    major: str
    phone: str
    userType: str
    grade: Optional[int] = None
    enrollmentStatus: Optional[str] = None

class SignupOut(BaseModel):
    ok: bool
    userId: str
    name: str
    email: str
    role: str
    deptName: str
    phone: Optional[str]
    grade: Optional[int]
    enrollmentStatus: Optional[str]
    createdAt: datetime

class LoginIn(BaseModel):
    studentId: str
    password: str

class LoginOut(BaseModel):
    ok: bool
    userId: str
    name: str
    email: str
    role: str
    deptName: str
    phone: Optional[str]
    grade: Optional[int]
    enrollmentStatus: Optional[str]
    createdAt: datetime



# =========================
# 인증
# =========================
def get_or_create_dept(conn, name: str) -> str:
    row = conn.execute(
        text("SELECT dept_id::text FROM departments WHERE name=:n"),
        {"n": name},
    ).fetchone()
    if row:
        return row[0]

    did = str(uuid.uuid4())
    conn.execute(
        text("INSERT INTO departments (dept_id, name) VALUES (:i, :n)"),
        {"i": did, "n": name},
    )
    return did

@app.post("/auth/signup", response_model=SignupOut)
def signup(body: SignupIn):
    role = body.userType.lower()
    if role not in ("student", "professor"):
        raise HTTPException(400, "Invalid role")

    with engine.begin() as conn:
        dept_id = get_or_create_dept(conn, body.major)

        conn.execute(text("""
            INSERT INTO users
            (user_id, name, email, password, phone, role, grade, enroll_status, dept_id, created_at)
            VALUES
            (:id, :n, :e, :p, :ph, :r, :g, :es, :d, NOW() AT TIME ZONE 'Asia/Seoul')
        """), {
            "id": body.studentId,
            "n": body.name,
            "e": body.email,
            "p": body.password,
            "ph": body.phone,
            "r": role,
            "g": body.grade if role == "student" else None,
            "es": body.enrollmentStatus if role == "student" else None,
            "d": dept_id,
        })

        row = conn.execute(text("""
            SELECT u.user_id, u.name, u.email, u.role, u.phone,
                   u.grade, u.enroll_status, d.name, u.created_at
            FROM users u
            JOIN departments d ON d.dept_id = u.dept_id
            WHERE u.user_id = :id
        """), {"id": body.studentId}).one()

    return {
        "ok": True,
        "userId": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[3],
        "phone": row[4],
        "grade": row[5],
        "enrollmentStatus": row[6],
        "deptName": row[7],
        "createdAt": row[8],
    }

@app.post("/auth/login", response_model=LoginOut)
def login(body: LoginIn):
    row = fetch_one("""
        SELECT u.user_id, u.name, u.email, u.password, u.role, u.phone,
               u.grade, u.enroll_status, d.name, u.created_at
        FROM users u
        JOIN departments d ON d.dept_id = u.dept_id
        WHERE u.user_id = :id
    """, {"id": body.studentId})

    if not row or row["password"] != body.password:
        raise HTTPException(401, "Invalid credentials")

    return {
        "ok": True,
        "userId": row["user_id"],
        "name": row["name"],
        "email": row["email"],
        "role": row["role"],
        "phone": row["phone"],
        "grade": row["grade"],
        "enrollmentStatus": row["enroll_status"],
        "deptName": row["name_1"] if "name_1" in row else row["name"],
        "createdAt": row["created_at"],
    }

class ChatIn(BaseModel):
    user_id: str
    message: str = Field(..., alias="text")

@app.post("/chat")
def create_chat(body: ChatIn):
    try:
        with engine.begin() as conn:
            # 1️⃣ 기존 세션 조회
            row = conn.execute(text("""
                SELECT session_id
                FROM chat_sessions
                WHERE user_id = :uid
                ORDER BY created_at DESC
                LIMIT 1
            """), {"uid": body.user_id}).fetchone()

            if row is not None:
                session_id = row[0]
            else:
                # 2️⃣ 세션 없으면 새로 생성
                session_id = str(uuid.uuid4())
                conn.execute(text("""
                    INSERT INTO chat_sessions
                    (session_id, user_id, title, created_at)
                    VALUES
                    (:sid, :uid, :title, NOW() AT TIME ZONE 'Asia/Seoul')
                """), {
                    "sid": session_id,
                    "uid": body.user_id,   # 학번 문자열
                    "title": body.message,
                })

            # 3️⃣ 메시지 저장
            conn.execute(text("""
                INSERT INTO chat_messages
                (message_id, session_id, content, created_at)
                VALUES
                (:mid, :sid, :content, NOW() AT TIME ZONE 'Asia/Seoul')
            """), {
                "mid": str(uuid.uuid4()),
                "sid": session_id,
                "content": body.message,
            })

        return {"ok": True, "session_id": session_id}

    except Exception as e:
        print("🔥 CHAT ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))
