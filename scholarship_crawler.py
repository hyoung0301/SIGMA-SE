import os
import time
import json
import uuid
import re
import requests
import pdfplumber
from pdf2image import convert_from_path
from PIL import Image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import psycopg2
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import easyocr

import torch
torch.cuda.is_available()
torch.version.cuda

load_dotenv()

# ===========================================
# 기본 설정
# ===========================================
BASE = "https://www.mmu.ac.kr"
BOARD_URL = "https://www.mmu.ac.kr/main/board/303"

DOWNLOAD_DIR = "downloads"
TEMP_DIR = "temp_images"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

POPPLER_PATH = r"C:\poppler-25.11.0\Library\bin"

reader = easyocr.Reader(['ko', 'en'], gpu=True)
embed_model = SentenceTransformer("BAAI/bge-small-en")

# ===========================================
# 파일명 안전화
# ===========================================
def sanitize_filename(name):
    ext = os.path.splitext(name)[1]
    return f"file_{uuid.uuid4().hex}{ext}"

# ===========================================
# 텍스트 정리
# ===========================================
def clean_text(text):
    if not text:
        return ""
    return text.replace("\x00", "").replace("\u0000", "")

# ===========================================
# OCR 노이즈 제거
# ===========================================
def clean_ocr_noise(text):
    if not text:
        return ""

    text = clean_text(text)
    text = re.sub(r'(.)\1{3,}', ' ', text)
    text = re.sub(r'[ㄱ-ㅎㅏ-ㅣ]{2,}', ' ', text)
    text = re.sub(r'[^가-힣0-9A-Za-z\s.,()\-_/]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# ===========================================
# 텍스트 유효성 검사
# ===========================================
def is_valid_text(text):
    if not text or len(text.strip()) < 40:
        return False

    letters = re.findall(r"[가-힣A-Za-z]", text)
    if len(letters) / max(len(text), 1) < 0.08:
        return False

    if re.search(r"(.)\1{5,}", text):
        return False

    return True

# ===========================================
# 임베딩
# ===========================================
def create_embedding(text):
    return embed_model.encode(text).tolist()

# ===========================================
# DB 연결
# ===========================================
def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        dbname=os.getenv("DB_NAME")
    )

# ===========================================
# 🔥 이미 수집된 게시글인지 확인 (핵심)
# ===========================================
def is_already_crawled(url: str) -> bool:
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM kb_documents WHERE url = %s LIMIT 1",
        (url,)
    )
    exists = cur.fetchone() is not None
    cur.close()
    conn.close()
    return exists

# ===========================================
# 텍스트 청크
# ===========================================
def chunk_text(text, size=700):
    words = text.split()
    chunks, curr = [], []

    for w in words:
        curr.append(w)
        if len(" ".join(curr)) > size:
            chunks.append(" ".join(curr))
            curr = []

    if curr:
        chunks.append(" ".join(curr))

    return chunks

# ===========================================
# PDF 텍스트
# ===========================================
def extract_pdf_text(path):
    try:
        with pdfplumber.open(path) as pdf:
            texts = []
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    texts.append(t)

        raw_text = clean_text("\n".join(texts))
        return raw_text if is_valid_text(raw_text) else None
    except:
        return None

# ===========================================
# PDF OCR
# ===========================================
def extract_pdf_ocr(path):
    try:
        images = convert_from_path(path, poppler_path=POPPLER_PATH)
    except:
        return ""

    all_text = []
    for i, img in enumerate(images):
        temp_path = os.path.join(TEMP_DIR, f"page_{i}.png")
        img.save(temp_path, "PNG")
        result = reader.readtext(temp_path, detail=0, paragraph=True)
        text = clean_ocr_noise("\n".join(result))
        all_text.append(text)

    final = "\n".join(all_text)
    return final if is_valid_text(final) else ""

# ===========================================
# 첨부파일 텍스트
# ===========================================
def extract_attachment_text(files):
    final_texts = []

    for f in files:
        if f.lower().endswith(".pdf"):
            text = extract_pdf_text(f) or extract_pdf_ocr(f)
            if text:
                final_texts.append(text)

    return "\n\n".join(final_texts)

# ===========================================
# HTML 본문
# ===========================================
def extract_html_body(soup):
    body = soup.select_one(".board_con")
    if not body:
        return ""

    for img in body.find_all("img"):
        img.decompose()
    for tag in body(["script", "style"]):
        tag.decompose()

    txt = clean_text(body.get_text("\n", strip=True))
    return "\n".join(line for line in txt.split("\n") if line.strip())

# ===========================================
# 첨부파일 다운로드
# ===========================================
def download_attachments(soup):
    files = []

    for a in soup.select("a[title='첨부파일 다운로드']"):
        href = a["href"]
        orig = a.get_text(strip=True)
        if not orig:
            continue

        url = href if href.startswith("http") else BASE + href
        safe = sanitize_filename(orig)
        save_path = os.path.join(DOWNLOAD_DIR, safe)

        data = requests.get(url).content
        with open(save_path, "wb") as f:
            f.write(data)

        files.append(save_path)

    return files

# ===========================================
# DB 저장
# ===========================================
def save_to_db(title, url, final_text, attachments):
    conn = get_db()
    cur = conn.cursor()

    doc_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO kb_documents (doc_id, title, source, url, created_at)
        VALUES (%s, %s, %s, %s, NOW())
    """, (doc_id, title, "장학공지", url))

    for idx, chunk in enumerate(chunk_text(final_text)):
        cur.execute("""
            INSERT INTO kb_chunks
            (chunk_id, doc_id, chunk_index, content, embedding, meta_json, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            str(uuid.uuid4()),
            doc_id,
            idx,
            chunk,
            create_embedding(chunk),
            json.dumps({"attachments": attachments}, ensure_ascii=False)
        ))

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ 저장 완료: {title}")

# ===========================================
# 상세 페이지
# ===========================================
def crawl_detail(href, driver):
    url = BASE + href
    driver.get(url)
    time.sleep(0.5)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    title_tag = soup.select_one("span.tit")
    title = clean_text(title_tag.get_text(strip=True) if title_tag else "(제목 없음)")

    body_text = extract_html_body(soup)
    files = download_attachments(soup)
    attach_text = extract_attachment_text(files)

    final_text = body_text
    if attach_text and is_valid_text(attach_text):
        final_text += "\n\n" + attach_text

    save_to_db(title, url, final_text.strip(), files)

# ===========================================
# 목록 페이지
# ===========================================
def crawl_list(page, driver):
    driver.get(f"{BOARD_URL}/{page}")
    time.sleep(0.4)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return [a["href"] for a in soup.select("td.title a") if "/read/" in a["href"]]

# ===========================================
# 실행
# ===========================================
if __name__ == "__main__":
    print("🚀 장학공지 크롤링 시작 (중복 발견 시 즉시 중단)")

    chrome_options = Options()
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )

    try:
        for page in range(1, 4):
            links = crawl_list(page, driver)

            for link in links:
                full_url = BASE + link

                # 🔥 이미 DB에 있으면 즉시 중단
                if is_already_crawled(full_url):
                    print("⛔ 이미 수집된 게시글 발견 → 전체 크롤링 중단")
                    print(full_url)
                    raise StopIteration

                crawl_detail(link, driver)

    except StopIteration:
        pass
    finally:
        driver.quit()
        print("🎉 크롤링 종료")
