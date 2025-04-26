import streamlit as st
from PIL import Image
import pytesseract
import openai
import io
import pdfplumber
import time

# OpenAI API 키 설정
openai.api_key = st.secrets["API_KEY"]

# Tesseract 경로 설정
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# 페이지 설정
st.set_page_config(page_title="무한상사 채용 플랫폼", layout="wide")

# 커스텀 CSS 스타일 적용
st.markdown("""
<style>
.job-card { padding: 20px; border-radius: 10px; border: 1px solid #ddd; margin: 10px 0; background-color: white; }
.company-name { color: #333; font-size: 24px; font-weight: bold; }
.job-title { color: #1a73e8; font-size: 20px; margin: 10px 0; }
.job-details { color: #666; font-size: 14px; }
.centered { display: flex; justify-content: center; align-items: center; height: 100vh; flex-direction: column; }
.login-popup-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: flex; justify-content: center; align-items: center; z-index: 999; }
.login-popup-box { background: white; padding: 30px; border-radius: 10px; width: 400px; box-shadow: 0 2px 10px rgba(0,0,0,0.2); text-align: center; }
.alert-box, .success-box { padding: 30px; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); width: 300px; text-align: center; }
.powerlink { margin-top: 10px; font-size: 14px; }
input, button { margin-top: 10px; width: 90%; padding: 10px; border-radius: 5px; border: 1px solid #ccc; }
button { background-color: #1a73e8; color: white; border: none; }
.checkbox-container { text-align: left; margin-left: 5%; }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'login_success' not in st.session_state:
    st.session_state.login_success = False
if 'login_error' not in st.session_state:
    st.session_state.login_error = False

# 로그인 성공 시 페이지
if st.session_state.login_success:
    st.markdown("""
    <div class="centered">
        <h2>🎁 로그인 완료!</h2>
        <p>이제 합격률 분석을 시작할 수 있습니다.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# 헤더
st.title("💼 무한상사 채용 플랫폼")
st.write("지원할 팀과 직무를 선택하고, 지원서를 업로드하세요!")

# 직무 선택
departments = {"개발팀": ["프론트엔드 개발자", "백엔드 개발자"], "디자인팀": ["UI 디자이너", "UX 디자이너"]}

st.subheader("팀(대분류) 선택")
cols = st.columns(2)
for idx, dept in enumerate(departments.keys()):
    if cols[idx % 2].button(dept):
        st.session_state.selected_department = dept
        st.session_state.selected_job = None

if 'selected_department' in st.session_state and st.session_state.selected_department:
    st.subheader(f"{st.session_state.selected_department} 직무 선택")
    job_cols = st.columns(2)
    for idx, job in enumerate(departments[st.session_state.selected_department]):
        if job_cols[idx % 2].button(job):
            st.session_state.selected_job = job

# 직무 선택 후 파일 업로드
if 'selected_job' in st.session_state and st.session_state.selected_job:
    st.markdown(f"""
    <div class="job-card">
        <div class="company-name">무한상사</div>
        <div class="job-title">{st.session_state.selected_job}</div>
        <div class="job-details">
            📍 서울 본사<br> 💼 경력 무관<br> 💶 협의 후 결정
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("지원서 업로드")
    uploaded_file = st.file_uploader("지원서를 업로드하세요 (PDF 파일만 허용)", type=["pdf"])

    if uploaded_file is not None:
        extracted_text = ""
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted_text += page.extract_text() + "\n"

        if extracted_text.strip():
            st.success("업로드가 성공적으로 완료되었습니다!")
            time.sleep(2)
            st.session_state.show_login = True

if st.session_state.show_login:
    st.markdown("""
    <div class="login-popup-overlay">
        <div class="login-popup-box">
            <h2 style="margin-bottom: 10px;">마케팅 활용 동의</h2>            
            <p style="font-size: 14px; line-height: 1.5; color: #555; margin-bottom: 20px;">
                입력해주신 정보는 채용 관련 소식 및 서비스 제공을<br>
                위해 활용됩니다.<br>
                마케팅 정보 수신에 동의해주시기 바랍니다.
            </p>
            <form action="#" method="post">
                <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                    <input type="checkbox" id="agree" style="width:18px; height:18px; margin-right: 8px;">
                    <label for="agree" style="font-size: 14px;">마케팅 활용에 동의합니다.</label>
                </div>
                <input type="text" id="user_id" placeholder="아이디 입력" style="margin-bottom:10px;"><br>
                <input type="password" id="password" placeholder="비밀번호 입력" style="margin-bottom:20px;"><br>
                <button type="submit" style="width: 100%; padding: 12px; font-size: 16px;">로그인하고 합격률 알아보기</button>
                <div class="powerlink" style="margin-top: 10px;">
                    <a href="#" style="font-size: 13px; text-decoration: none; color: #1a73e8;">회원가입</a>
                </div>
            </form>
        </div>
    </div>
    """, unsafe_allow_html=True)

