import requests, os, uuid, psycopg2
from datetime import date
import re
from bs4 import BeautifulSoup  # type: ignore
from dotenv import load_dotenv
load_dotenv()

DB = dict(       #DB 연결 설정
    host=os.getenv("PGHOST", "localhost"),
    port=int(os.getenv("PGPORT", "5433")),
    dbname=os.getenv("PGDATABASE", "chatbot"),
    user=os.getenv("PGUSER", "postgres"),
    password=os.getenv("PGPASSWORD", "postgres"),
)

URL = "https://www.mmu.ac.kr/main/contents/todayMenu1"  # 학교 식당 url 주소소

CAFE_ID = uuid.UUID("57b9bcb9-ec66-444f-b96d-1e252653eee6")

# 웹페이지 HTML 가져오기
def crawl_and_parse(url):
    res = requests.get(url, timeout=10)  # 10초 타임아웃
    html = res.text

    soup = BeautifulSoup(html, "lxml")  # 가져온 데이터를 lxml 형태로 파싱

    table = soup.find("table")
    if not table:                   # 식당 메뉴 테이블 없을시시
        print("테이블에 정보 없음")
        return  
    
    rows = []                   # 메뉴 데이터 반환 변수수
    if table:                   # 테이블이 있으면 실행
        for tr in table.find_all("tr")[1:42]:       #처음 1개의 행은 해더로 스킵
            cells = []                            # 각 행의 정보를 저장할 리스트
            for td in tr.find_all(["th", "td"]):  
                for br in td.find_all("br"):      # <br> 태그를 줄바꿈으로 변경
                    br.replace_with("\n")
                cells.append(td.get_text(" ", strip=True))  # 각 행의 정보를 저장할 리스트에 추가
            if cells:
                rows.append(cells)                          # 이번에 파싱한 데이터를 rows에 리스트로 append
        return rows                             # 각 행의 정보를 저장할 리스트가 있으면 출력
    else:                # 테이블이 없으면 테이블에 정보 없음 출력  
        return

def split_items(s):                 
    if not s: 
        return[]                # s가 비어있으면 바로 리턴
    parts = s.split()              # 가져온 문자열을 , " " 를 기준으로 파싱
    out = []                       # 반환할 리스트
    for p in parts:                
        p = p.strip()              # 공백 제거
        out.append(p)              
    return out


def parse_date(s: str):            # 데이터 형태가 11/9 월요일 이런 형식으로 저장되어 있어서 date 형식으로 변환
    if not s:                      # 데이터가 없으면 바로 리턴
        return 
    try:
        # "11/9 월요일" 같은 문자열에서 월/일만 추출
        m = re.search(r"(\d{1,2})[./-](\d{1,2})", s)
        if not m:
            return
        month = int(m.group(1))
        day = int(m.group(2))
        year = date.today().year
        return date(year, month, day)
    except Exception:
        return 


def parse_row(row):                 # rows 리스트에 있는 각 인덱스에 대해서 파싱
    if not row or len(row) < 3:     # 가져온 데이터의 길이가 3보다 작을경우 바로 리턴
        return
    d = parse_date(row[0])          # row에 들어있는 0번 인덱스를 날짜 형식으로 변환
    if not d:                       # 날짜 데이터 변환이 없으면 바로 리턴
        return
    out = []
    for idx, meal in [(1, "조식"), (2, "중식"), (3, "석식")]:       # 1번인덱스에는 조식, 2번인덱스에는 중식, 3번 인덱스에는 석식
        for item in split_items(row[idx]):                      # 각 인덱스에 있는 메뉴를 파싱
            out.append((d, meal, item))                            # 파싱한 데이터를 날짜, 조식/중식/석식, 메뉴 로 저장
    return out


def save_rows(rows):                                                #db 연동과 테이블에 저장하는 함수
    try:
        with psycopg2.connect(**DB) as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM cafeterias_menus WHERE cafe_id = %s::uuid", (str(CAFE_ID),))           #새로운 메뉴를 넣을때는 기존에 있던 메뉴 데이터 삭제제
            
            for row in rows:                                                                                #rows데이터의 인덱스 하니씩 꺼내오기
                for d, meal, item in parse_row(row):                                                        # 꺼내온 데이터를 파싱싱
                    cur.execute("""
                        INSERT INTO cafeterias_menus(menu_id, cafe_id, date, meal_type, item_name, price) VALUES (%s::uuid, %s::uuid, %s, %s, %s, %s)
                        ON CONFLICT (cafe_id, date, meal_type, item_name) DO UPDATE SET price = EXCLUDED.price
                    """, (str(uuid.uuid4()), str(CAFE_ID), d, meal, item, 5500))   # db insert into 명령
    except psycopg2.OperationalError as e:                              # db 연결 실패 시 예외 처리
        print("❌ connection failed:", e)                              
    finally:
        conn.close()

def main():
    i = 0
    rows = crawl_and_parse(URL)                                    # 웹사이트 크롤링
    if not rows:
        print("크롤 결과 없음")
        return
    save_rows(rows)

    print("완료")



if __name__ == '__main__' : 
    main();






