import os           #.env에서 읽어온 환경변수를 os.getenv()로 꺼낼 때 사용
from typing import Optional, List
from datetime import date   # FastAPI 파라미터/응답 모델에서 날짜·시각 타입을 명확히 할 때 사용
from dotenv import load_dotenv  #.env 파일을 읽어 환경변수로 주입
from fastapi import FastAPI, Query, HTTPException       #앱 인스턴스 생성, 쿼리 파라미터 기본값/검증 선언, 401/400 같은 에러 응답 던질 때
from fastapi.middleware.cors import CORSMiddleware
import uuid                                     # departments.dept_id 같은 UUID 생성이 필요할 때 사용.               
from pydantic import BaseModel                  # 요청/응답 스키마 정의(검증·직렬화).
from sqlalchemy import text,create_engine       # raw SQL 실행 시 사용, PostgreSQL 연결 풀 생성


# -------- docker 환경 변수 로딩 --------
load_dotenv()
PGHOST = os.getenv("PGHOST", "localhost")
PGPORT = os.getenv("PGPORT", "5433")
PGDATABASE = os.getenv("PGDATABASE", "chatbot")
PGUSER = os.getenv("PGUSER", "postgres")
PGPASSWORD = os.getenv("PGPASSWORD", "")

DATABASE_URL = f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}:{PGPORT}/{PGDATABASE}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


app = FastAPI(title="Cafeteria API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("ALLOW_ORIGINS", "*").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Cafeteria(BaseModel):
    cafe_id: str
    name: str
    location: str | None = None

class MenuOut(BaseModel):
    menu_id: str
    cafe_name: str
    date: date
    meal_type: str
    item_name: str
    price: int | None = None

@app.get("/cafeterias", response_model=List[Cafeteria])
def list_cafeterias(q: Optional[str] = None):
    sql = "SELECT cafe_id::text, name, location FROM cafeterias"
    params = {}
    if q:
        sql += " WHERE name ILIKE :q"
        params["q"] = f"%{q}%"
    sql += " ORDER BY name"

    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).all()

    return [{"cafe_id": r[0], "name": r[1], "location": r[2]} for r in rows]

@app.get("/menus", response_model=List[MenuOut])
def list_menus(
    date_: Optional[date] = Query(None, alias="date"),
    cafe: Optional[str] = None,
    limit: int = 100
):
    sql = """
    SELECT m.menu_id::text, c.name, m.date, m.meal_type, m.item_name, m.price
    FROM cafeterias_menus m
    JOIN cafeterias c ON c.cafe_id = m.cafe_id
    WHERE 1=1
    """
    params = {}
    if date_:
        sql += " AND m.date = :d"
        params["d"] = date_
    if cafe:
        sql += " AND c.name ILIKE :cafe"
        params["cafe"] = f"%{cafe}%"
    sql += " ORDER BY m.date DESC, m.meal_type, m.item_name LIMIT :lim"
    params["lim"] = limit

    with engine.connect() as conn:
        rows = conn.execute(text(sql), params).all()

    return [
        {
            "menu_id": r[0],
            "cafe_name": r[1],
            "date": r[2],
            "meal_type": r[3],
            "item_name": r[4],
            "price": r[5],
        } for r in rows
    ]

# --- (옵션) 업서트 예시: 크롤러/관리화면에서 사용 ---
class MenuIn(BaseModel):
    cafe_name: str
    date: date
    meal_type: str
    item_name: str
    price: int | None = None

@app.post("/menus", response_model=MenuOut, status_code=201)
def upsert_menu(body: MenuIn):
    with engine.begin() as conn:
        # 식당 ID 확보(없으면 생성)
        row = conn.execute(text("SELECT cafe_id FROM cafeterias WHERE name=:n"),
                           {"n": body.cafe_name}).fetchone()
        if row:
            cafe_id = row[0]

        # 최종 값 반환
        r = conn.execute(text("""
        SELECT m.menu_id::text, c.name, m.date, m.meal_type, m.item_name, m.price
        FROM cafeterias_menus m
        JOIN cafeterias c ON c.cafe_id = m.cafe_id
        WHERE m.cafe_id=:cid AND m.date=:d AND m.meal_type=:m AND m.item_name=:i
        """), {"cid": cafe_id, "d": body.date, "m": body.meal_type, "i": body.item_name}).one()

    return {"menu_id": r[0], "cafe_name": r[1], "date": r[2],
            "meal_type": r[3], "item_name": r[4], "price": r[5]}




# --- 회원가입 (users 테이블 + enroll_status/grade 반영) ---
# 요청/응답 모델
class SignupIn(BaseModel):              #회원가입 입력 데이터터
    name: str
    studentId: str
    email: str
    password: str
    major: str
    phone: str
    userType: str                 # 'student' | 'professor'
    grade: Optional[int] = None   # 학생이면 1~6, 아니면 null
    enrollmentStatus: Optional[str] = None  # 학생이면 값, 아니면 null

class SignupOut(BaseModel):         #회원가입 db에 저장된 데이터
    ok: bool
    userId: str
    name: str
    email: str
    role: str
    deptName: str
    phone: str | None = None
    grade: Optional[int] = None
    enrollmentStatus: Optional[str] = None
    createdAt: date

def get_or_create_dept(conn, dept_name: str) -> str:
    row = conn.execute(
        text("SELECT dept_id::text FROM departments WHERE name = :n LIMIT 1"),
        {"n": dept_name},
    ).fetchone()
    if row:
        return row[0]
    new_id = str(uuid.uuid4())
    conn.execute(
        text("INSERT INTO departments (dept_id, name) VALUES (:id, :n)"),
        {"id": new_id, "n": dept_name},
    )
    return new_id

@app.post("/auth/signup", response_model=SignupOut, status_code=201)
def signup(body: SignupIn):
    role = body.userType.lower().strip()
    if role not in ("student", "professor"):
        raise HTTPException(400, "userType must be 'student' or 'professor'")

    # 학생만 grade/enroll_status 반영, 교수면 NULL로
    grade = body.grade if role == "student" else None
    enroll_status = body.enrollmentStatus if role == "student" else None

    with engine.begin() as conn:
        dept_id = get_or_create_dept(conn, body.major)

        # users: user_id=학번, 나머지 매핑
        conn.execute(text("""
            INSERT INTO users
              (user_id, name, email, password, phone, role, grade, enroll_status, dept_id, created_at)
            VALUES
              (:user_id, :name, :email, :password, :phone, :role, :grade, :enroll_status, :dept_id, NOW())
        """), {
            "user_id": body.studentId,
            "name": body.name,
            "email": body.email,
            "password": body.password,      # 테스트용: 평문 저장(운영 전 해시 필요)
            "phone": body.phone,
            "role": role,
            "grade": grade,
            "enroll_status": enroll_status,
            "dept_id": dept_id,
        })

        row = conn.execute(text("""
            SELECT u.user_id, u.name, u.email, u.role, u.phone, u.grade, u.enroll_status,
                   d.name AS dept_name, u.created_at
            FROM users u
            JOIN departments d ON d.dept_id = u.dept_id
            WHERE u.user_id = :uid
        """), {"uid": body.studentId}).one()

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


# --- 로그인: 학번(userId) + 비밀번호(평문 비교, 테스트용) ---

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
    phone: Optional[str] = None
    grade: Optional[int] = None
    enrollmentStatus: Optional[str] = None
    createdAt: date

@app.post("/auth/login", response_model=LoginOut)
def login(body: LoginIn):
    with engine.connect() as conn:
        row = conn.execute(text("""
            SELECT u.user_id, u.name, u.email, u.password, u.role, u.phone,
                   u.grade, u.enroll_status, d.name AS dept_name, u.created_at
            FROM users u
            JOIN departments d ON d.dept_id = u.dept_id
            WHERE u.user_id = :sid
            LIMIT 1
        """), {"sid": body.studentId}).fetchone()

    # 존재 X 또는 비밀번호 불일치 (테스트: 평문 비교)
    if not row or row[3] != body.password:
        raise HTTPException(status_code=401, detail="invalid credentials")

    return {
        "ok": True,
        "userId": row[0],
        "name": row[1],
        "email": row[2],
        "role": row[4],
        "phone": row[5],
        "grade": row[6],
        "enrollmentStatus": row[7],
        "deptName": row[8],
        "createdAt": row[9],
    }

