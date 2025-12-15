from asyncio import events
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time, os, re

import psycopg2

DB = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5433")),
    "database": os.getenv("PGDATABASE", "chatbot"),  # dbname 대신 database 사용
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", "postgres"),
}


def fetch_schedule(url="https://www.mmu.ac.kr/main/acschedule"):
    options = Options()
    options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    driver.get(url)
    time.sleep(0.5)  # JS 로딩 대기

    html = driver.page_source
    driver.quit()

    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select("div.schedule table tbody tr")

    events = []
    for tr in rows:
        th = tr.find("th")
        td = tr.find("td")
        if th and td:
            date = th.get_text(strip=True)
            content = td.get_text(strip=True)
            events.append([date, content])

    return events

def convert_event(row):
    yyyy = row[0][:4]
    text = row[1]

    date_pattern = r"(\d{2}\.\d{2})"
    dates = re.findall(date_pattern, text)

    if len(dates) == 1:
        start = f"{yyyy}-{dates[0].replace('.', '-')}"
        end = start
    else:
        start = f"{yyyy}-{dates[0].replace('.', '-')}"
        end = f"{yyyy}-{dates[1].replace('.', '-')}"

    # 🔥 날짜(+요일) 제거 패턴
    date_remove = r"\d{2}\.\d{2}(?:\.\([^)]+\))?"

    # 🔥 텍스트에서 날짜 패턴 완전히 제거
    clean_text = re.sub(date_remove, "", text)

    # 🔥 ' - ' 같은 남은 구분자 제거
    clean_text = clean_text.replace("-", "")
    clean_text = clean_text.strip()

    return [start, end, clean_text]

def insert_events(conn, events):
    cursor = conn.cursor()

    for start_date, end_date, title in events:
        cursor.execute("""
            INSERT INTO academic_events (title, start_date, end_date)
            VALUES (%s, %s, %s)
        """, (title, start_date, end_date))

    conn.commit()
    cursor.close()


if __name__ == "__main__":
    event_crawl = fetch_schedule()
    events = []
    for row in event_crawl:
        event = convert_event(row)
        events.append(event)
    
    with psycopg2.connect(**DB) as conn: 
        insert_events(conn, events)