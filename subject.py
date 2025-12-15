import re, os, uuid, psycopg2
import pandas as pd
import csv
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()


DB = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5433")),
    "database": os.getenv("PGDATABASE", "chatbot"),  # dbname 대신 database 사용
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}


CAFE_ID = uuid.UUID("57b9bcb9-ec66-444f-b96d-1e252653eee6")

def split_dayp(s):
        m = re.match(r"^([월화수목금토일])(\d+)$", s); return (m.group(1), int(m.group(2))) if m else (None,None) # 요일숫자 -> 요일, 숫자로 분해

def timetable_rows(path: str) -> list[list[str]]:
    df = (pd.read_excel(path, dtype=str, engine="openpyxl")         # 파일 읽기
          if path.lower().endswith((".xlsx",".xls"))
          else pd.read_csv(path, dtype=str, encoding="utf-8-sig")).fillna("")


    for c in ["반"]:                
        if c in df: df[c] = df[c].replace("", pd.NA).ffill().fillna("")         # 학기, 학부과명, 학년, 반 비어있으면 위에 값으로 채우기기

    daycols = [c for c in df.columns if re.fullmatch(r"[월화수목금토일]\d+", c.strip())]    #요일교시 형태 추출

    rows = []
    for i in range(len(df)):
        term  = df.at[i,"학기"]     
        dept  = df.at[i,"학부과명"] 
        grade = df.at[i,"학년"]     
        sect  = df.at[i,"반"]   

        for col in daycols:
            title = str(df.at[i,col]).strip()   # 과목 추출
            if not title: continue

            room, prof = "", ""
            if i+1 < len(df):                       #과목이 있는 같은 열의 아래행은 강의실 번호 교수님 이름 부분 추출
                nxt = str(df.at[i+1,col]).strip()   # 과목 교수님 이름 앞 뒤 공백 제거해서 추출
                m = re.match(r"^\s*([A-Za-z0-9_]+)\s+(.+)$", nxt)   # 추출한 문자열 패턴이랑 매칭칭
                if title and m:                     # 교과목이 안비어 있고 문자열 패턴이랑 일치하면 실행 
                    room, prof = m.group(1), m.group(2)     # 패턴 처음 그룹은 강의실 번호, 두번째 그룹은 교수님 이름 
                    df.at[i+1,col] = ""             # 한번 추출한 열은 비워서 중복 방지

            rows.append([term, dept, grade, sect, col, title, room, prof])


    buckets = defaultdict(list)
    for term,dept,grade,sect,dayp,title,room,prof in rows:
        day,p = split_dayp(dayp)                # 요일숫자 를 요일, 숫자 로 분해해서 day, d로 저장장
        buckets[(term,dept,grade,sect,day,title,room,prof)].append(p)       # 강의 시간만 추가로 buckets에 값 형태로 저장장
        
    merged = []                                                             # 최종적으로 병합된 결과 행들을 담을 리스트
    for (term,dept,grade,sect,day,title,room,prof), ps in buckets.items():  # ps: 해당 (학기/학과/학년/분반/요일/강의명/강의실/교수) 조합에 속한 교시 목록
        ps = sorted(set(ps))                                           # 교시 목록 중복 제거 후 오름차순 정렬 (예: [1,2,3,5,6])
        start = prev = ps[0]                                                # 현재 연속된 구간 시작점, 직전값 초기화화
        for cur in ps[1:] + [None]:                                         # 연강이 끝날때 또는 문서의 끝일때때
            if cur is None or cur != prev+1:                                
                merged.append([term,dept,grade,sect, f"{day}{start}" if start==prev else f"{day}{start}~{prev}", title, room, prof])        # 단일교시면 월1, 연속 교시면 월1~2 로 포멧멧
                if cur is not None: start = cur                             # 아직 목록이 남아있으면 새 시작점을 현재 값으로 갱신
            prev = prev if cur is None else cur                             # 다음 루프를 위해 직전값 갱신

    return merged 
    
def extract_subject_info(csv_path, columns=None):
    # 기본 컬럼 정의 (학년학기 포함)
    if columns is None:
        columns = ["학과명", "과목코드", "학점", "과목명", "학년"]

    # CSV 읽기
    df = pd.read_csv(csv_path)

    # 학과명 앞 숫자 제거
    if "학과명" in df.columns:
        df["학과명"] = df["학과명"].astype(str).apply(
            lambda x: re.sub(r"^\s*[A-Za-z0-9]+\s+", "", x)
        )


    # 학년학기 분리: "2 / 1" → "2", "1"
    if "학년" in df.columns:
        df["학기"]  = df["학년"].astype(str).apply(lambda x: x.split("/")[1].strip())
        df["학년"] = df["학년"].astype(str).apply(lambda x: x.split("/")[0].strip())
        

    # 최종 선택 컬럼: 학년/학기 추가
    final_columns = ["학과명", "과목코드", "학점", "과목명", "학년", "학기"]
    

    return df[final_columns].values.tolist()
   
def append_code_and_credit(existing_array, csv_array):

    updated = []

    for row in existing_array:
        semester = row[0]
        dept = row[1]      # 기존 배열 학과명
        year = row[2]
        name = row[5]      # 기존 배열 과목명
        
        # 기본값: 변경 없이 그대로
        new_row = row.copy()

        # CSV 배열과 직접 비교
        for csv_row in csv_array:
            csv_dept, csv_name, csv_credit, csv_code, csv_year, csv_st = csv_row
            if(dept == "해양컴퓨터공학과") : 
                dept = "컴퓨터공학과"
         
            if (dept == csv_dept or dept == "교양과정부" ) and name == csv_name and year == csv_year and csv_st == semester:
                new_row += [csv_code, csv_credit]
                break  # 더 찾을 필요 없음

        updated.append(new_row)


    return updated


def insert_subjects(conn, rows):
    cursor = conn.cursor()

    for row in rows:
        if len(row) != 10:
            continue  # 길이가 안 맞으면 건너뛰기
        term, dept, grade, section, time_label, title, room_number, instructor_name, code, credit = row


        cursor.execute("""
            SELECT user_id
            FROM users
            WHERE name = %s
            AND dept_id = (SELECT dept_id FROM departments WHERE name = %s LIMIT 1)
            LIMIT 1
        """, (instructor_name, dept))
        result = cursor.fetchone()
        instructor_user_id = result if result else None

        # 2) INSERT 실행
        cursor.execute("""
            INSERT INTO subject (
                subjectID,
                dept,
                grade,
                term,
                section,
                time_label,
                title,
                room_number,
                instructor_user_id,
                code,
                credit
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s
            )
        """, (
            str(uuid.uuid4()),   # subjectID
            dept,
            int(grade),
            int(term),
            section,
            time_label,
            title,
            room_number,
            instructor_user_id,
            code,
            int(credit)
        ))

    conn.commit()
    cursor.close()                                              


if __name__ == "__main__":
    path = r"C:\Users\hyeonseong\Desktop\2025학년도+제2학기+정규시간표.xlsx"
    data = timetable_rows(path)
    
    csv_path = r"C:\Users\hyeonseong\chatbot\subject_crawl_20251130_034046.csv"

    csv_result = extract_subject_info(csv_path)
    result = append_code_and_credit(data, csv_result)
    
   
    with psycopg2.connect(**DB) as conn:
        insert_subjects(conn, result)
    
    
   
   
