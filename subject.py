import re
import pandas as pd
from collections import defaultdict

def split_dayp(s):
        m = re.match(r"^([월화수목금토일])(\d+)$", s); return (m.group(1), int(m.group(2))) if m else (None,None) # 요일숫자 -> 요일, 숫자로 분해해

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
            title = str(df.at[i,col]).strip()   # 과목 추출출
            if not title: continue

            room, prof = "", ""
            if i+1 < len(df):                       #과목이 있는 같은 열의 아래행은 강의실 번호 교수님 이름 부분 추출
                nxt = str(df.at[i+1,col]).strip()   # 과목 교수님 이름 앞 뒤 공백 제거해서 추출
                m = re.match(r"^([0-9]{3,5})\s+(.+)$", nxt)     # 추출한 문자열 패턴이랑 매칭칭
                if title and m:                     # 교과목이 안비어 있고 문자열 패턴이랑 일치하면 실행 
                    room, prof = m.group(1), m.group(2)     # 패턴 처음 그룹은 강의실 번호, 두번째 그룹은 교수님 이름 
                    df.at[i+1,col] = ""             # 한번 추출한 열은 비워서 중복 방지지

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

    return merged                                                           # 연강 과목 합쳐진 결과

# 사용 예
if __name__ == "__main__":
    path = r"C:\Users\hyeonseong\Desktop\2025학년도+제2학기+정규시간표.xlsx"
    data = timetable_rows(path)
    print(data[:12])

