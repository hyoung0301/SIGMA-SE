from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv
from datetime import datetime
import os





# ----------------------------------
# Chrome 옵션 설정 (성능 최적화)
# ----------------------------------
def setup_chrome_options():
    options = Options()
    # 성능 최적화 옵션 (이미지 로딩은 유지 - 일부 사이트에서 JS 실행에 필요)
    prefs = {
        "profile.default_content_setting_values.notifications": 2
    }
    options.add_experimental_option("prefs", prefs)
    # 성능 최적화 옵션
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    return options


# ----------------------------------
# 헬퍼 함수: 프레임 전환 (안정성 향상)
# ----------------------------------
def switch_to_frame_safe(driver, frame_name, wait_time=10):
    """프레임 전환을 안전하게 수행하고 대기"""
    try:
        driver.switch_to.default_content()
        wait = WebDriverWait(driver, wait_time)
        wait.until(EC.frame_to_be_available_and_switch_to_it(frame_name))
        # 프레임 전환 후 짧은 대기로 안정성 확보
        time.sleep(0.3)
        return True
    except TimeoutException:
        print(f"프레임 '{frame_name}' 전환 실패")
        return False


# ----------------------------------
# 헬퍼 함수: 요소 찾기 (재시도 로직 포함)
# ----------------------------------
def find_element_safe(driver, by, value, wait_time=10, retry=3):
    """요소를 안전하게 찾고 재시도"""
    for attempt in range(retry):
        try:
            wait = WebDriverWait(driver, wait_time)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except (TimeoutException, StaleElementReferenceException) as e:
            if attempt == retry - 1:
                print(f"요소 찾기 실패: {by}={value}")
                raise
            # 재시도 전 짧은 대기
            time.sleep(0.3)
    return None


# ----------------------------------
# 헬퍼 함수: Select 옵션 변경 후 대기
# ----------------------------------
def select_and_wait(driver, select_element, value, wait_condition=None, wait_time=10):
    """Select 옵션 변경 후 조건이 충족될 때까지 대기"""
    select_element.select_by_value(value)
    
    # Select 변경 후 옵션이 로드되는 시간 확보
    time.sleep(0.5)
    
    if wait_condition:
        try:
            wait = WebDriverWait(driver, wait_time)
            wait.until(wait_condition)
        except TimeoutException:
            print(f"Select 변경 후 대기 시간 초과: {value}, 계속 진행...")
            # 타임아웃이어도 계속 진행


# ----------------------------------
# 메인 크롤링 로직
# ----------------------------------
def main():
    # Chrome 드라이버 설정
    options = setup_chrome_options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)
    
    global_common_subjects = set()   # 공통 전공에서 나온 과목
    final_list = []                  # 최종 저장 리스트
    csv_headers = None               # CSV 헤더 (첫 번째 테이블에서 추출)
    
    try:
        # ----------------------------------
        # 1. 로그인
        # ----------------------------------
        print("로그인 중...")
        driver.get("https://intranet.mmu.ac.kr")
        driver.maximize_window()
        
        # 로그인 요소가 로드될 때까지 대기
        try:
            user_id_elem = wait.until(EC.presence_of_element_located((By.NAME, "userID")))
            passwd_elem = wait.until(EC.presence_of_element_located((By.NAME, "passWD")))
            login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'로그인')]")))
            
            user_id_elem.send_keys("20213326")
            passwd_elem.send_keys("gustjd152!")
            login_btn.click()
            
            # 로그인 완료 대기
            time.sleep(2)  # 로그인 처리 시간 확보
            print("로그인 완료")
        except Exception as e:
            print(f"로그인 실패: {e}")
            raise
        
        
        # ----------------------------------
        # 2. 강의 페이지 이동
        # ----------------------------------
        print("📚 강의 페이지 이동 중...")
        driver.get("https://intranet.mmu.ac.kr/HagSaeng/SuGang/JeonGong.htm")
        
        # leftFrame으로 전환
        if not switch_to_frame_safe(driver, "leftFrame"):
            print("leftFrame 전환 실패")
            return
        
        # 년도 선택
        year_select_elem = wait.until(EC.presence_of_element_located((By.ID, "nyeondo")))
        select_year = Select(year_select_elem)
        select_year.select_by_value("2025")
        time.sleep(0.3)  # 년도 선택 후 대기
        
        # 학과 SELECT가 로드될 때까지 대기
        hb_select_elem = wait.until(EC.presence_of_element_located((By.ID, "hagbu")))
        select_hb = Select(hb_select_elem)
        
        # 옵션을 인덱스와 값으로 미리 저장 (stale element 방지)
        hb_options_data = []
        for option in select_hb.options:
            value = option.get_attribute("value")
            text = option.text.strip()
            if value and value.strip():
                hb_options_data.append((value, text))
        
        print(f"총 {len(hb_options_data)}개 학과 발견")
        if len(hb_options_data) == 0:
            print("학과 옵션이 없습니다. 페이지 로딩을 확인하세요.")
            driver.quit()
            return
        
        
        # ----------------------------------
        # 3. 모든 학과(HB) 순회
        # ----------------------------------
        for idx, (hb_value, hb_name) in enumerate(hb_options_data, 1):
            # 프레임 재전환 (매번 안전하게)
            if not switch_to_frame_safe(driver, "leftFrame", wait_time=5):
                continue
            
            print(f"\n[{idx}/{len(hb_options_data)}] 학과: {hb_value} / {hb_name}")
            
            # 학과 선택 및 전공 SELECT 로딩 대기
            jg_options_data = []  # 초기화
            try:
                hb_select_elem = wait.until(EC.presence_of_element_located((By.ID, "hagbu")))
                select_hb = Select(hb_select_elem)
                
                # Select 변경
                select_hb.select_by_value(hb_value)
                time.sleep(0.5)  # 전공 옵션 로딩 대기 (원본과 동일)
                
                # 전공 SELECT 요소 가져오기
                try:
                    jg_select_elem = wait.until(
                        EC.presence_of_element_located((By.ID, "jeongong"))
                    )
                except TimeoutException:
                    print(f" 전공 SELECT를 찾을 수 없음, 다음 학과로...")
                    continue
                
                select_jg = Select(jg_select_elem)
                
                # 옵션을 미리 저장 (stale element 방지)
                for option in select_jg.options:
                    value = option.get_attribute("value")
                    text = option.text.strip()
                    if value and value.strip():
                        jg_options_data.append((value, text))
                
            except (TimeoutException, NoSuchElementException) as e:
                print(f"학과 {hb_name} 처리 중 오류: {e}")
                continue
            
            # 전공 옵션이 없으면 스킵
            if not jg_options_data:
                print(f"전공 옵션이 없음, 다음 학과로...")
                continue
            
            print(f"{len(jg_options_data)}개 전공 발견")
            
            
            # ----------------------------------
            # 4. 해당 학과의 모든 전공(JG) 순회
            # ----------------------------------
            for jg_idx, (jg_value, jg_name) in enumerate(jg_options_data, 1):
                
                print(f"  → [{jg_idx}/{len(jg_options_data)}] 전공: {jg_value} / {jg_name}")
                
                try:
                    # leftFrame으로 전환
                    if not switch_to_frame_safe(driver, "leftFrame", wait_time=5):
                        continue
                    
                    # 전공 선택
                    jg_select_elem = wait.until(EC.presence_of_element_located((By.ID, "jeongong")))
                    select_jg = Select(jg_select_elem)
                    select_jg.select_by_value(jg_value)
                    time.sleep(0.3)  # Select 변경 후 대기
                    
                    # 조회 버튼 찾기 및 클릭
                    try:
                        query_btn = wait.until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, ".button.blue"))
                        )
                        query_btn.click()
                        time.sleep(0.5)  # 버튼 클릭 후 페이지 로딩 대기
                    except TimeoutException:
                        print(f"조회 버튼을 찾을 수 없음")
                        continue
                    
                    # mainFrame으로 전환 및 테이블 로딩 대기
                    if not switch_to_frame_safe(driver, "mainFrame", wait_time=10):
                        continue
                    
                    # 테이블이 로드될 때까지 대기
                    time.sleep(0.5)  # 프레임 전환 후 테이블 로딩 대기
                    rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
                    
                    if not rows or len(rows) == 0:
                        print(f"테이블 행이 없음 (rows: {len(rows) if rows else 0})")
                        try:
                            driver.switch_to.default_content()
                        except:
                            pass
                        continue
                    
                    # 테이블 데이터 크롤링
                    row_count = 0
                    print(f"테이블 행 수: {len(rows)}")
                    
                    # 첫 번째 테이블에서 헤더 추출 (한 번만)
                    if csv_headers is None and rows:
                        try:
                            first_row = rows[0]
                            header_cells = [th.text.strip() for th in first_row.find_elements(By.TAG_NAME, "th")]
                            if header_cells:
                                csv_headers = ["학과명"] + header_cells
                                print(f"CSV 헤더 추출: {csv_headers}")
                        except:
                            pass
                    
                    for row_idx, row in enumerate(rows):
                        try:
                            cols = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
                            # 헤더 행은 스킵 (th 태그가 있거나 첫 번째 행)
                            if row_idx == 0:
                                continue
                            if not cols or len(cols) <= 3:
                                continue
                                                     
                            final_list.append([hb_name] + cols)
                            row_count += 1
                            
                        except StaleElementReferenceException:
                            # 요소가 DOM에서 제거된 경우 스킵
                            continue
                    
                    print(f"{row_count}개 과목 수집")
                    
                except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
                    print(f"전공 {jg_name} 처리 중 오류: {e}")
                finally:
                    # 다음 반복을 위해 leftFrame으로 복귀
                    try:
                        driver.switch_to.default_content()
                    except:
                        pass
        
        # ----------------------------------
        # 5. 최종 출력 및 CSV 저장
        # ----------------------------------
        print(f"\n{'='*50}")
        print(f"크롤링 완료: 총 {len(final_list)}개 과목 수집")
        print(f"{'='*50}")
        
        # CSV 파일로 저장
        if final_list:
            # 파일명에 타임스탬프 추가
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"subject_crawl_{timestamp}.csv"
            
            try:
                # CSV 헤더 정의
                # 일반적인 교육과정 테이블 구조를 가정
                if final_list and len(final_list[0]) > 0:
                    num_cols = len(final_list[0])
                    # 헤더 결정: 추출된 헤더가 있으면 사용, 없으면 기본 헤더
                    if csv_headers and len(csv_headers) == num_cols:
                        headers = csv_headers
                    else:
                        # 기본 헤더 (테이블 구조에 맞게 조정 가능)
                        default_headers = ["학과명", "학년", "학기", "과목코드", "과목명", "이수구분", "학점", "시간", "비고"]
                        if num_cols <= len(default_headers):
                            headers = default_headers[:num_cols]
                        else:
                            headers = default_headers + [f"컬럼{i+1}" for i in range(len(default_headers), num_cols)]
                    
                    with open(csv_filename, 'w', newline='', encoding='utf-8-sig') as f:
                        writer = csv.writer(f)
                        writer.writerow(headers)
                        writer.writerows(final_list)
                    
                    file_path = os.path.abspath(csv_filename)
                    print(f"CSV 파일 저장 완료: {csv_filename}")
                    print(f"파일 경로: {file_path}")
                    print(f"총 {len(final_list)}개 행 저장됨")
                else:
                    print("저장할 데이터가 없습니다.")
            except Exception as e:
                print(f"CSV 저장 실패: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("크롤링된 데이터가 없습니다.")
        
        # 콘솔에도 출력 (선택적)
        if final_list:
            print(f"\n처음 5개 항목 미리보기:")
            for i, item in enumerate(final_list[:5], 1):
                print(f"  {i}. {item}")
            
    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        driver.quit()
        print("드라이버 종료")


if __name__ == "__main__":
    main()
  