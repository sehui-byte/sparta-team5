
import streamlit as st
import random

# 페이지 기본 설정
st.set_page_config(page_title="채용 플랫폼", layout="wide")

# 커스텀 CSS 스타일
st.markdown("""
<style>
.job-card {
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #ddd;
    margin: 10px;
    background-color: white;
}
.company-name {
    color: #333;
    font-size: 20px;
    font-weight: bold;
}
.job-title {
    color: #1a73e8;
    font-size: 18px;
    margin: 10px 0;
}
.job-details {
    color: #666;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

# 헤더
st.title("💼 채용 플랫폼")
st.write("다양한 채용 정보를 확인하세요!")

# 검색 필터
col1, col2, col3 = st.columns(3)
with col1:
    job_category = st.selectbox("직무", ["전체", "개발", "디자인", "마케팅", "영업"])
with col2:
    location = st.selectbox("지역", ["전체", "서울", "경기", "인천", "부산"])
with col3:
    experience = st.selectbox("경력", ["전체", "신입", "1-3년", "3-5년", "5년 이상"])

# 샘플 채용 정보
sample_jobs = [
    {
        "company": "테크스타트업",
        "title": "프론트엔드 개발자",
        "location": "서울 강남",
        "experience": "1-3년",
        "salary": "4,500만원 ~ 6,000만원",
        "skills": ["React", "TypeScript", "Node.js"]
    },
    {
        "company": "글로벌기업",
        "title": "백엔드 개발자",
        "location": "서울 서초",
        "experience": "3-5년",
        "salary": "5,000만원 ~ 7,000만원",
        "skills": ["Python", "Django", "AWS"]
    },
    {
        "company": "IT기업",
        "title": "UI/UX 디자이너",
        "location": "경기 판교",
        "experience": "신입",
        "salary": "3,500만원 ~ 4,500만원",
        "skills": ["Figma", "Adobe XD", "Sketch"]
    }
]

# 카드 형식으로 채용 정보 표시
cols = st.columns(3)
for idx, job in enumerate(sample_jobs):
    with cols[idx % 3]:
        st.markdown(f"""
        <div class="job-card">
            <div class="company-name">{job['company']}</div>
            <div class="job-title">{job['title']}</div>
            <div class="job-details">
                📍 {job['location']}<br>
                💼 {job['experience']}<br>
                💰 {job['salary']}<br>
                🛠 {', '.join(job['skills'])}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"지원하기 {idx+1}", key=f"apply_{idx}"):
            st.success("지원이 완료되었습니다!")
