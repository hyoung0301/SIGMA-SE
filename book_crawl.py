from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
import csv


# ---------------------------
# 제목/저자 파싱 함수
# ---------------------------
def parse_title_author(raw):
    if not raw:
        return None, None

    # 1) '/' 기준으로 제목 / 저자 분리
    parts = raw.split("/")
    title = parts[0].strip()
    rest = parts[1].strip() if len(parts) > 1 else ""

    # 2) 옮긴이 제거
    if ";" in rest:
        rest = rest.split(";")[0].strip()

    # 3) '지음' 제거
    rest = rest.replace("지음", "").strip()

    # 4) 숫자 제거 (ex. 1920-1994)
    rest = re.sub(r"\d+-?\d*", "", rest).strip()

    # 5) 공백 정리
    rest = re.sub(r"\s+", " ", rest)

    return title, rest


# ---------------------------
# Selenium 기본 설정
# ---------------------------
options = Options()
options.headless = False  # True = 브라우저 안보임

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

driver.get("https://lib.mmu.ac.kr/#/popular-charged-book")
time.sleep(2)

# ---------------------------
# 인기자료 목록 링크 가져오기
# ---------------------------
book_elements = driver.find_elements(By.CSS_SELECTOR, "a.ikc-item-title")

book_list = []
for el in book_elements:
    list_title = el.text.strip().replace("\n", " ")
    link = el.get_attribute("href")
    book_list.append((list_title, link))

book_list = book_list[:20]  # 20권만


books_data = []

# ---------------------------
# 상세 페이지에서 데이터 크롤링
# ---------------------------
for idx, (_, link) in enumerate(book_list, start=1):
    driver.get(link)
    time.sleep(1)

    # --- 더보기 버튼 클릭 ---
    try:
        more_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "btn-biblio-more-open"))
        )
        more_btn.click()
        time.sleep(1)
    except:
        print("더보기 버튼 없음 → 넘어감")

    detail_items = driver.find_elements(By.CSS_SELECTOR, "ul.ikc-biblio-infolist li")

    raw_title_author = None
    isbn_list = []

    for item in detail_items:
        try:
            label = item.find_element(By.TAG_NAME, "label").text.strip()

            # 서명(제목+저자)
            if label == "서명":
                raw_title_author = item.find_element(By.CSS_SELECTOR, "span").text.strip()

            # ISBN (여러 span 가능)
            if label == "ISBN":
                spans = item.find_elements(By.CSS_SELECTOR, "span")
                for sp in spans:
                    isbn_list.append(sp.text.strip())

        except:
            continue

    # 제목/저자 정제
    title, author = parse_title_author(raw_title_author)

    # ISBN 문자열 정리 (여러 개 있으면 콤마로 합침)
    isbn = ", ".join(isbn_list) if isbn_list else None

    print(f"{idx}: {title} / {author} / {isbn}")

    books_data.append({
        "title": title,
        "author": author,
        "isbn": isbn
    })


driver.quit()

# ---------------------------
# CSV 저장
# ---------------------------
csv_filename = "popular_books.csv"

with open(csv_filename, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=["title", "author", "isbn"])
    writer.writeheader()
    writer.writerows(books_data)

print(f"\n📁 CSV 저장 완료: {csv_filename}")
