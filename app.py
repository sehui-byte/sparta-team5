import streamlit as st
import os
import tempfile
import time
from utils import display_job_description, validate_file, extract_text_from_file
from job_data import get_job_details
from ai_analysis import analyze_resume
from styles import set_page_styling, display_custom_css

# Set page configuration - MUST be the first Streamlit command
st.set_page_config(page_title="무한상사 채용 플랫폼", page_icon="💼", layout="wide")

# Apply page styling
set_page_styling()
display_custom_css()

# Initialize session state variables
if 'job_id' not in st.session_state:
    st.session_state.job_id = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'login_success' not in st.session_state:
    st.session_state.login_success = False
if 'login_error' not in st.session_state:
    st.session_state.login_error = False
if 'resume_processed' not in st.session_state:
    st.session_state.resume_processed = False
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = None
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None

# Check for job_id in query params for detailed view
query_params = st.query_params
job_id_from_query = query_params.get("job_id", [None])[0]

# Enhanced debugging for job_id
print(f"Debug - job_id from query params: '{job_id_from_query}'")
print(f"Debug - URL query params: {dict(query_params)}")

# Check if job_id exists in job_listings directly from job_data
if job_id_from_query:
    from job_data import get_job_details
    test_job = get_job_details(job_id_from_query)
    print(f"Debug - Test job lookup result: {test_job['title'] if test_job else 'Not found'}")

# Update job_id in session state if it changes via query params
if job_id_from_query and st.session_state.job_id != job_id_from_query:
    st.session_state.job_id = job_id_from_query
    # Reset states when job changes
    st.session_state.show_login = False
    st.session_state.login_success = False
    st.session_state.login_error = False
    st.session_state.resume_processed = False
    st.session_state.resume_text = None
    st.session_state.analysis_result = None

# Get current job_id from session state
job_id = st.session_state.job_id

# Debug logging
# st.write(f"Debug - Current job_id: {job_id}")
# st.write(f"Debug - Session State: {st.session_state}")

# Main page (job listings)
if not st.session_state.job_id:
    # Reset states when going back to main page
    st.session_state.job_id = None
    st.session_state.show_login = False
    st.session_state.login_success = False
    st.session_state.login_error = False
    st.session_state.resume_processed = False
    st.session_state.resume_text = None
    st.session_state.analysis_result = None
    # Page title with icon
    st.markdown(
        '<div class="main-title"><span class="icon">💼</span> 무한상사 채용 플랫폼</div>',
        unsafe_allow_html=True)
    st.markdown('<div class="subtitle">다양한 채용 정보를 확인하세요!</div>',
                unsafe_allow_html=True)

    # Job selection filters
    # st.markdown('<div class="filter-section"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="filter-label">직무</div>',
                    unsafe_allow_html=True)
        job_category = st.selectbox("직무 필터", ["전체", "개발", "디자인", "마케팅", "영업"])

    with col2:
        st.markdown('<div class="filter-label">지역</div>',
                    unsafe_allow_html=True)
        location = st.selectbox("지역 필터", ["전체", "서울", "경기", "인천", "부산"])

    with col3:
        st.markdown('<div class="filter-label">경력</div>',
                    unsafe_allow_html=True)
        experience = st.selectbox("경력 필터",
                                  ["전체", "신입", "1-3년", "3-5년", "5년 이상"])

    # Display job listings in a grid
    st.markdown('<div class="job-grid">', unsafe_allow_html=True)

    # Get all job listings for display
    job_ids = ["it-개발자", "인사-담당자", "재무-회계-담당자", "영업-담당자", "디자인-기획자", "마케팅-매니저"]
    
    # Create enough columns for all job listings (adjust grid layout based on number of jobs)
    num_jobs = len(job_ids)
    cols_per_row = 3  # 3 cards per row looks better than 4 with more details
    job_grid = st.columns(cols_per_row)

    for i, job_id in enumerate(job_ids):
        print(f"i >>>{i} job_id >>> {job_id}")
        job = get_job_details(job_id)
        
        # Calculate the correct column index for the current job
        col_index = i % cols_per_row
        
        with job_grid[col_index]:
            st.markdown(f"""
            <div class="job-card">
                <h3>{job['title']}</h3>
                <div class="job-company">{job['company']}</div>
                <div class="job-tag location">{job['location']}</div>
                <div class="job-tag experience">{job['experience']}</div>
                <div class="salary">{job['salary']}</div>
                <div class="skills">{job['skills']}</div>
                <a href="?job_id={job_id}" class="view-btn">자세히 보기</a>
            </div>
            """,
                        unsafe_allow_html=True)
            
            # Add some vertical space between rows
            if i % cols_per_row == cols_per_row - 1:
                st.write("")  # Add empty space between rows

    st.markdown('</div>', unsafe_allow_html=True)

# Detail page (job details and resume upload)
else:
    # Get job details
    job_details = get_job_details(job_id)
    
    # Debug information
    print(f"Requested job_id: {job_id}")
    print(f"Retrieved job details: {job_details['title'] if job_details else 'None'}")
    
    # 유효하지 않은 job_id인 경우 메인 페이지로 리다이렉트 - 이제 get_job_details에서 항상 기본값을 반환하므로 이 조건은 사용하지 않음
    # if job_details is None:
    #     st.error(f"요청하신 직무 정보({job_id})를 찾을 수 없습니다. 다른 직무를 선택해주세요.")
    #     # 잠시 대기 후 메인 페이지로 리다이렉트
    #     time.sleep(2)
    #     st.session_state.job_id = None
    #     st.query_params.clear()
    #     st.rerun()
    
    # Back button - IMPORTANT: Use st.query_params to clear job_id
    if st.button("← 목록으로 돌아가기"):
        st.query_params.clear()
        st.rerun()

    # Display detailed job description
    st.markdown(f"""
    <div class="job-detail">
        <h2>{job_details['title']}</h2>
        <div class="detail-section">
            <div class="detail-item"><span class="info-label">지역</span>: {job_details['location']}</div>
            <div class="detail-item"><span class="info-label">경력</span>: {job_details['experience']}</div>
            <div class="detail-item"><span class="info-label">급여</span>: {job_details['salary']}</div>
            <div class="detail-item"><span class="info-label">기술</span>: {job_details['skills']}</div>
        </div>
    """,
                unsafe_allow_html=True)

    # 직무 개요 및 주요 업무를 자격요건과 동일한 스타일로 표시
    description_text = job_details['description']

    # 직무 개요와 주요 업무 분리
    sections = description_text.split('\n\n')

    # 복리후생 정보 미리 추출
    benefits_section = None
    for section in sections:
        if section.strip() and '복리후생:' in section:
            benefits_section = section
            break

    st.markdown("""
    <div class="requirement-section">
        <h3>직무 개요 및 주요 업무</h3>
    """,
                unsafe_allow_html=True)

    for section in sections:
        if section.strip():
            if '직무 개요:' in section:
                content = section.replace('직무 개요:', '').strip()
                st.markdown(
                    f'<div class="qualification-item"><span class="qualification-label">직무 개요</span>: {content}</div>',
                    unsafe_allow_html=True)
            elif '주요 업무:' in section:
                st.markdown(
                    f'<div class="qualification-item"><span class="qualification-label">주요 업무</span>:</div>',
                    unsafe_allow_html=True)
                tasks = section.replace('주요 업무:', '').strip().split('\n')
                for task in tasks:
                    if task.strip():
                        st.markdown(
                            f'<div class="task-item">{task.strip()}</div>',
                            unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # 자격 요건 표시
    from job_data import qualification_requirements
    qualification_reqs = qualification_requirements.get(
        job_details['title'], {})

    if qualification_reqs:
        st.markdown("""
        <div class="requirement-section">
            <h3>자격 요건</h3>
        """,
                    unsafe_allow_html=True)

        if "academic" in qualification_reqs:
            st.markdown(
                f'<div class="qualification-item"><span class="qualification-label">학력</span>: {qualification_reqs["academic"]}</div>',
                unsafe_allow_html=True)
        if "language" in qualification_reqs:
            st.markdown(
                f'<div class="qualification-item"><span class="qualification-label">어학</span>: {qualification_reqs["language"]}</div>',
                unsafe_allow_html=True)
        if "certificate" in qualification_reqs:
            st.markdown(
                f'<div class="qualification-item"><span class="qualification-label">자격증</span>: {qualification_reqs["certificate"]}</div>',
                unsafe_allow_html=True)
        if "experience" in qualification_reqs:
            st.markdown(
                f'<div class="qualification-item"><span class="qualification-label">경험/경력</span>: {qualification_reqs["experience"]}</div>',
                unsafe_allow_html=True)
        if "skills" in qualification_reqs:
            st.markdown(
                f'<div class="qualification-item"><span class="qualification-label">스킬/기술</span>: {qualification_reqs["skills"]}</div>',
                unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # 복리후생 정보 표시
    # for benefit in job_details['benefits']:
    #     if not benefit.startswith("복리후생:"): # 제목이 아닌 항목만 표시
    #         st.markdown(f"<div class='benefit-item'>{benefit}</div>", unsafe_allow_html=True)

    # st.markdown('</div>', unsafe_allow_html=True)

    # 복리후생 정보 표시 (마지막에 배치)
    if benefits_section:
        st.markdown("""
        <div class="requirement-section benefits-section">
            <h3>복리후생</h3>
        """,
                    unsafe_allow_html=True)

        benefits = benefits_section.replace('복리후생:', '').strip().split('\n')
        for benefit in benefits:
            if benefit.strip():
                st.markdown(f'<div class="task-item">{benefit.strip()}</div>',
                            unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Resume upload section
    st.markdown('<div class="resume-section">', unsafe_allow_html=True)
    st.markdown("## 이력서 업로드")
    st.markdown("PDF 형식의 이력서를 업로드하고 귀하의 자격에 대한 맞춤형 분석을 받아보세요.")

    uploaded_file = st.file_uploader("이력서 선택", type=["pdf"], key=f"uploader_{st.session_state.job_id}") # Use key to reset on job change

    if uploaded_file and not st.session_state.resume_processed:
        with st.spinner("이력서 처리 및 분석 중..."): # Combined spinner message
            is_valid, file_type = validate_file(uploaded_file)

            if is_valid:
                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    temp_file_path = tmp_file.name

                # Extract text
                resume_text = extract_text_from_file(temp_file_path, file_type)
                os.unlink(temp_file_path) # Remove temp file

                if resume_text:
                    st.session_state.resume_text = resume_text
                    # Get job requirements
                    job_requirements = job_details["requirements"]
                    job_description = job_details["description"]
                    job_title = job_details["title"]

                    # Analyze resume
                    analysis_result = analyze_resume(
                        resume_text, job_title, job_description,
                        job_requirements)

                    st.session_state.analysis_result = analysis_result
                    st.session_state.resume_processed = True
                    st.session_state.show_login = True # Show login popup AFTER processing
                    st.success("이력서 분석 완료! 마케팅 활용에 동의해주세요.")
                    time.sleep(1) # Short delay before rerun
                    st.rerun()
                else:
                    st.error("이력서에서 텍스트를 추출할 수 없습니다. 파일을 확인하고 다시 시도해 주세요.")
                    st.session_state.resume_processed = False # Reset flag on error
            else:
                st.error("유효한 PDF 파일을 업로드해 주세요.")
                st.session_state.resume_processed = False # Reset flag on error

    # --- Marketing Consent Popup Logic (Using st.dialog) ---
    dialog_result = None
    if st.session_state.show_login and not st.session_state.login_success:
        @st.dialog("마케팅 활용 동의")
        def show_consent_dialog():
            st.markdown("""
                <p style="font-size: 14px; line-height: 1.5; color: #555; margin-bottom: 20px;">
                    입력해주신 정보는 채용 관련 소식 및 서비스 제공을<br>
                    위해 활용됩니다.<br>
                    마케팅 정보 수신에 동의해주시기 바랍니다.
                </p>
            """, unsafe_allow_html=True)

            agree_marketing = st.checkbox("마케팅 활용에 동의합니다.", key="agree_marketing_checkbox_dialog")
            user_id = st.text_input("아이디 입력", key="user_id_input_dialog")
            password = st.text_input("비밀번호 입력", type="password", key="password_input_dialog")

            col1, col2 = st.columns(2) # Create columns for buttons
            with col1:
                if st.button("동의하고 합격률 알아보기", key="submit_consent_button_dialog", use_container_width=True):
                    if agree_marketing:
                        # Return True if consent is given
                        st.session_state.login_success = True # Set state here
                        st.session_state.show_login = False
                        st.session_state.login_error = False
                        st.rerun() # Rerun immediately after setting state
                    else:
                        st.error("마케팅 활용에 동의해야 합격률을 볼 수 있습니다.")
                        # Return False or None to keep dialog open or indicate non-consent
                        # return False # No explicit return needed, error shown, dialog stays
            with col2:
                # Add a separate close button
                if st.button("닫기", key="close_consent_button_dialog", use_container_width=True):
                     st.session_state.show_login = False # Just hide the dialog
                     st.rerun()

        # Call the dialog function - it doesn't return anything in this structure
        # The rerun happens inside the button click logic now.
        show_consent_dialog()

    # --- Display Login Success Message OR Analysis Results ---
    if st.session_state.login_success:
        st.markdown("""
        <div class="centered">
            <h2>🎁 동의 완료!</h2>
            <p>이제 합격률 분석 결과를 확인할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2) # Show message briefly before showing results

        # Now display the analysis results if processing was done
        if st.session_state.resume_processed and st.session_state.analysis_result:
            analysis_result = st.session_state.analysis_result
            st.markdown('<div class="analysis-results">', unsafe_allow_html=True)
            st.markdown("## 분석 결과")
            # Display success rate
            success_rate = analysis_result.get("success_rate", 0)
            st.markdown(
                f'<div class="success-rate">예상 합격률: <span class="rate-value">{success_rate}%</span></div>',
                unsafe_allow_html=True)

            # 자격 요건 평가 표시
            st.markdown('<div class="qualification-section">',
                        unsafe_allow_html=True)
            st.markdown("## 자격 요건 평가", unsafe_allow_html=True)

            qualification_ratings = analysis_result.get(
                "qualification_ratings", {})
            if qualification_ratings:
                # 자격 요건 카테고리 이름 매핑
                qualification_name_map = {
                    "academic": "학력 요건",
                    "language": "어학 능력",
                    "certificate": "자격증",
                    "experience": "경험/경력",
                    "skills": "스킬/기술"
                }

                for key, rating in qualification_ratings.items():
                    if isinstance(rating, dict):
                        rating_score = rating.get("score", 0)
                    elif isinstance(rating, int):
                        rating_score = rating
                    else:
                        rating_score = 0  # 예상치 못한 타입 대비

                    # Ensure rating_score is an integer
                    try:
                        rating_score = int(rating_score)
                    except (ValueError, TypeError):
                        rating_score = 0  # Default to 0 if conversion fails

                    if isinstance(rating, dict):
                        rating_desc = rating.get("description", "")
                        meets_requirement = rating.get(
                            "meets_requirement", False)
                    elif isinstance(rating, int):
                        rating_desc = ""  # Assign an empty string if rating is an integer
                        meets_requirement = True  # Assume not met if rating is an integer
                    else:
                        rating_desc = ""
                        meets_requirement = True
                    
                    # Only try to get description if rating is a dict
                    if isinstance(rating, dict):
                        rating_desc = rating.get("description", "")
                        meets_requirement = rating.get("meets_requirement", False)
                    
                    # 70점 이상이면 자격 요건 충족으로 처리
                    if rating_score >= 70:
                        meets_requirement = True

                    qual_name = qualification_name_map.get(
                        key, key)

                    # 자격 요건 충족 여부에 따른 색상 설정
                    status_color = "#28a745" if meets_requirement else "#dc3545"  # 녹색 또는 빨간색
                    status_text = "충족" if meets_requirement else "미충족"
                    status_icon = "✓" if meets_requirement else "✗"

                    # 점수에 따른 바 색상 계산
                    if rating_score >= 80:
                        bar_color = "#28a745"  # 녹색
                    elif rating_score >= 60:
                        bar_color = "#17a2b8"  # 파란색
                    else:
                        bar_color = "#ffc107"  # 노란색

                    st.markdown(f'''
                    <div class="qualification-item" style="margin-bottom: 20px; height: 60px;">
                        <div class="qualification-header" style="margin-bottom: 8px; height: 20px;">
                            <span class="qualification-name" style="display: inline-block; padding: 0;">{qual_name}</span>
                            <span class="qualification-status" style="color: {status_color}; float: right; padding: 0;">{status_icon} {status_text}</span>
                        </div>
                        <div class="qualification-bar-container" style="height: 24px; padding: 0; background-color: #f2f2f2; border-radius: 4px; overflow: hidden;">
                            <div class="qualification-bar" style="width: {rating_score}%; background-color: {bar_color}; height: 24px; line-height: 24px; text-align: right; padding-right: 10px;">
                                <span class="qualification-score" style="color: white; font-weight: bold;">{rating_score}%</span>
                            </div>
                        </div>
                    </div>
                    ''', unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # 핵심 역량 지표 평가 표시
            st.markdown('<div class="competency-section">',
                        unsafe_allow_html=True)
            st.markdown("## 핵심 역량 지표 평가", unsafe_allow_html=True)

            competency_ratings = analysis_result.get(
                "competency_ratings", {})
            if competency_ratings:
                # 육각형 그래프(레이더 차트)를 위한 데이터 준비
                import matplotlib.pyplot as plt
                import numpy as np
                import io
                import base64
                from matplotlib.path import Path
                from matplotlib.spines import Spine
                from matplotlib.transforms import Affine2D
                import matplotlib.font_manager as fm
                
                # 한글 폰트 설정
                import platform
                
                # 운영체제별 기본 한글 폰트 설정
                if platform.system() == 'Windows':
                    # Windows - 맑은 고딕 폰트 사용
                    plt.rcParams['font.family'] = 'Malgun Gothic'
                    plt.rcParams['axes.unicode_minus'] = False  # 마이너스 기호 깨짐 방지
                elif platform.system() == 'Darwin':  # macOS
                    plt.rcParams['font.family'] = 'AppleGothic'
                    plt.rcParams['axes.unicode_minus'] = False
                else:  # Linux 등 기타 OS
                    # 나눔고딕 등이 없는 경우를 대비하여 기본 sans-serif 폰트 사용
                    plt.rcParams['font.family'] = 'NanumGothic, sans-serif'
                    plt.rcParams['axes.unicode_minus'] = False
                
                # 최대 6개의 역량만 선택 (육각형 시각화를 위해)
                competency_keys = list(competency_ratings.keys())[:6]
                competency_scores = []
                competency_names = []
                
                # 데이터 준비
                for key in competency_keys:
                    rating = competency_ratings[key]
                    # Rating 형식 확인 및 점수 추출
                    if isinstance(rating, dict):
                        rating_score = rating.get("score", 0)
                        rating_desc = rating.get("description", "")
                    elif isinstance(rating, (int, float)):
                        rating_score = rating
                        rating_desc = ""
                    else:
                        rating_score = 0
                        rating_desc = ""
                    
                    # 점수를 정수로 변환
                    try:
                        rating_score = int(rating_score)
                    except (ValueError, TypeError):
                        rating_score = 0
                    
                    # 역량 이름 변환
                    competency_name_map = {
                        "technical_skills": "기술적 역량",
                        "problem_solving": "문제 해결 능력",
                        "system_design": "시스템 설계 능력",
                        "code_quality": "코드 품질 관리",
                        "teamwork": "팀 협업 능력",
                        "continuous_learning": "지속적 학습 능력",
                        "hr_knowledge": "인사 지식",
                        "recruitment": "채용 역량",
                        "employee_relations": "직원 관계 관리",
                        "organizational_development": "조직 개발 능력",
                        "communication": "커뮤니케이션 능력",
                        "data_analysis": "데이터 분석 능력",
                        "accounting_principles": "회계 원칙 이해도",
                        "financial_analysis": "재무 분석 능력",
                        "regulatory_compliance": "법규 준수 역량",
                        "budget_management": "예산 관리 능력",
                        "risk_assessment": "리스크 평가 능력",
                        "reporting_skills": "보고서 작성 능력",
                        "client_relationship": "고객 관계 관리",
                        "negotiation": "협상 능력",
                        "market_knowledge": "시장 지식",
                        "goal_orientation": "목표 지향성",
                        "presentation_skills": "프레젠테이션 스킬",
                        "adaptability": "적응력"
                    }
                    
                    competency_name = competency_name_map.get(key, key)
                    competency_names.append(competency_name)
                    competency_scores.append(rating_score)
                
                # 자격요건평가(좌측)와 상세역량점수(우측) 레이아웃
                qual_comp_col1, qual_comp_col2 = st.columns(2)
                
                # 자격요건평가 (좌측 컬럼)
                with qual_comp_col1:
                    st.markdown("<h3>자격요건 평가</h3>", unsafe_allow_html=True)
                    for key, rating in qualification_ratings.items():
                        if isinstance(rating, dict):
                            rating_score = rating.get("score", 0)
                        elif isinstance(rating, int):
                            rating_score = rating
                        else:
                            rating_score = 0
                        
                        try:
                            rating_score = int(rating_score)
                        except (ValueError, TypeError):
                            rating_score = 0
                            
                        qual_name = qualification_name_map.get(key, key)
                        
                        # 자격 요건 충족 여부에 따른 색상 설정
                        meets_requirement = rating_score >= 70
                        status_color = "#28a745" if meets_requirement else "#dc3545"
                        status_text = "충족" if meets_requirement else "미충족"
                        status_icon = "✓" if meets_requirement else "✗"
                        
                        # 점수에 따른 바 색상 계산
                        if rating_score >= 80:
                            bar_color = "#28a745"  # 녹색
                        elif rating_score >= 60:
                            bar_color = "#17a2b8"  # 파란색
                        else:
                            bar_color = "#ffc107"  # 노란색
                            
                        st.markdown(f'''
                        <div class="qualification-item" style="margin-bottom: 20px; height: 60px;">
                            <div class="qualification-header" style="margin-bottom: 8px; height: 20px;">
                                <span class="qualification-name" style="display: inline-block; padding: 0;">{qual_name}</span>
                                <span class="qualification-status" style="color: {status_color}; float: right; padding: 0;">{status_icon} {status_text}</span>
                            </div>
                            <div class="qualification-bar-container" style="height: 24px; padding: 0; background-color: #f2f2f2; border-radius: 4px; overflow: hidden;">
                                <div class="qualification-bar" style="width: {rating_score}%; background-color: {bar_color}; height: 24px; line-height: 24px; text-align: right; padding-right: 10px;">
                                    <span class="qualification-score" style="color: white; font-weight: bold;">{rating_score}%</span>
                                </div>
                            </div>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    # 자격요건 평가는 항목이 더 적으므로 여백 추가 (빈 div로 공간 확보)
                    # 상세역량점수와 높이를 맞추기 위한 빈 공간 추가
                    qualifications_count = len(qualification_ratings)
                    competencies_count = min(len(competency_keys), 6)  # 최대 6개까지 표시
                    
                    # 상세역량점수가 더 많은 경우 차이만큼 여백 추가
                    if competencies_count > qualifications_count:
                        for i in range(competencies_count - qualifications_count):
                            st.markdown('<div style="height: 60px;"></div>', unsafe_allow_html=True)
                
                # 상세역량점수 (우측 컬럼)
                with qual_comp_col2:
                    st.markdown("<h3>상세 역량 점수</h3>", unsafe_allow_html=True)
                    for key in competency_keys:
                        rating = competency_ratings[key]
                        if isinstance(rating, dict):
                            rating_score = rating.get("score", 0)
                        elif isinstance(rating, (int, float)):
                            rating_score = rating
                        else:
                            rating_score = 0
                            
                        try:
                            rating_score = int(rating_score)
                        except (ValueError, TypeError):
                            rating_score = 0
                            
                        competency_name = competency_name_map.get(key, key)
                        
                        # 점수에 따른 바 색상 계산
                        if rating_score >= 80:
                            bar_color = "#28a745"  # 녹색
                        elif rating_score >= 60:
                            bar_color = "#17a2b8"  # 파란색
                        else:
                            bar_color = "#ffc107"  # 노란색
                            
                        st.markdown(f"""
                        <div class="competency-item" style="margin-bottom: 20px; height: 60px;">
                            <div class="competency-name" style="margin-bottom: 8px; height: 20px; padding: 0;">{competency_name}</div>
                            <div class="competency-bar-container" style="height: 24px; padding: 0; background-color: #f2f2f2; border-radius: 4px; overflow: hidden;">
                                <div class="competency-bar" style="width: {rating_score}%; background-color: {bar_color}; height: 24px; line-height: 24px; text-align: right; padding-right: 10px;">
                                    <span class="competency-score" style="color: white; font-weight: bold;">{rating_score}%</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # 추가 역량 정보 - 확장형 패널
                with st.expander("모든 역량 점수 상세 보기"):
                    for key, rating in competency_ratings.items():
                        if key not in competency_keys:  # 메인 화면에 표시되지 않은 역량만 보여줌
                            if isinstance(rating, dict):
                                rating_score = rating.get("score", 0)
                                rating_desc = rating.get("description", "")
                            elif isinstance(rating, (int, float)):
                                rating_score = rating
                                rating_desc = ""
                            else:
                                rating_score = 0
                                rating_desc = ""
                                
                            try:
                                rating_score = int(rating_score)
                            except (ValueError, TypeError):
                                rating_score = 0
                                
                            competency_name = competency_name_map.get(key, key)
                            
                            # 점수에 따른 바 색상 계산
                            if rating_score >= 80:
                                bar_color = "#28a745"  # 녹색
                            elif rating_score >= 60:
                                bar_color = "#17a2b8"  # 파란색
                            else:
                                bar_color = "#ffc107"  # 노란색
                                
                            st.markdown(f"""
                            <div class="competency-item">
                                <div class="competency-name">{competency_name}</div>
                                <div class="competency-bar-container">
                                    <div class="competency-bar" style="width: {rating_score}%; background-color: {bar_color};">
                                        <span class="competency-score">{rating_score}%</span>
                                    </div>
                                </div>
                                <div class="competency-desc">{rating_desc}</div>
                            </div>
                            """, unsafe_allow_html=True)
                
                # 두 막대그래프와 다음 섹션 사이에 진회색 구분선 추가
                st.markdown('<hr style="height: 1px; background-color: #555; border: none; margin: 30px 0px;">', unsafe_allow_html=True)
                
                # 역량종합분석(좌측)과 강점&개선영역(우측) 레이아웃
                radar_strength_col1, radar_strength_col2 = st.columns(2)
                
                # 역량종합분석 방사형 그래프 (좌측 컬럼)
                with radar_strength_col1:
                    st.markdown("<h3>역량 종합 분석</h3>", unsafe_allow_html=True)
                    
                    # 육각형 그래프 그리기
                    N = len(competency_names)
                    if N > 0:  # 데이터가 있는 경우에만 그래프 그리기
                        # 데이터가 6개보다 적으면 6개까지 확장 (None으로 채움)
                        while len(competency_names) < 6:
                            competency_names.append("")
                            competency_scores.append(None)
                        
                        # 각도 설정 (6각형)
                        angles = np.linspace(0, 2*np.pi, 6, endpoint=False).tolist()
                        
                        # 데이터를 닫힌 다각형으로 만들기
                        competency_scores_normalized = [score/100 if score is not None else 0 for score in competency_scores]
                        competency_scores_normalized += competency_scores_normalized[:1]  # 첫 데이터를 마지막에 복제하여 닫힌 모양 만들기
                        angles += angles[:1]  # 첫 각도를 마지막에 복제
                        
                        # 그래프 설정
                        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
                        
                        # 그래프 색상 및 라인 설정
                        ax.plot(angles, competency_scores_normalized, 'o-', linewidth=2, color='#1a73e8')
                        ax.fill(angles, competency_scores_normalized, alpha=0.25, color='#1a73e8')
                        
                        # y축 설정 (0부터 1까지)
                        ax.set_ylim(0, 1)
                        
                        # x축 라벨 설정 (역량 이름)
                        ax.set_xticks(angles[:-1])  # 마지막 중복 각도 제외
                        # 라벨을 그래프에서 더 멀리 위치시키기 위해 패딩 추가
                        ax.set_xticklabels(competency_names[:6], fontsize=12)  # 6개의 역량 이름
                        # 라벨과 그래프 사이의 거리를 늘리기 위해 tick_params 사용
                        ax.tick_params(axis='x', pad=15)  # x축 라벨에 패딩 추가
                        
                        # 그리드 설정
                        ax.set_rticks([0.2, 0.4, 0.6, 0.8, 1.0])  # 20%, 40%, 60%, 80%, 100%
                        ax.set_rgrids([0.2, 0.4, 0.6, 0.8, 1.0], angle=35, labels=['20%', '40%', '60%', '80%', '100%'])
                        
                        # 배경 스타일 설정
                        ax.grid(True, linestyle='-', alpha=0.7)
                        
                        # 그래프 제목
                        ax.set_title('핵심 역량 지표 육각형 그래프', size=15, color='#333', y=1.1)
                        
                        # 그래프 이미지를 바이트로 변환하여 HTML에 삽입
                        buf = io.BytesIO()
                        fig.savefig(buf, format='png', bbox_inches='tight', transparent=True)
                        buf.seek(0)
                        img_str = base64.b64encode(buf.read()).decode('utf-8')
                        plt.close(fig)  # 메모리 누수 방지
                        
                        # 이미지 표시
                        st.markdown(f"""
                        <div style="display: flex; justify-content: center; margin: 20px 0;">
                            <img src="data:image/png;base64,{img_str}" alt="역량 육각형 그래프" style="max-width: 100%; height: auto;">
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 범례 표시
                        st.markdown("""
                        <div style="text-align: center; margin-bottom: 10px; color: #666; font-size: 14px;">
                            그래프가 넓게 퍼질수록 해당 역량이 높다는 것을 의미합니다.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.warning("핵심 역량 데이터가 없습니다.")
                
                # 강점 & 개선영역 (우측 컬럼)
                with radar_strength_col2:
                    st.markdown("<h3>강점 & 개선영역</h3>", unsafe_allow_html=True)
                    
                    # 강점
                    st.markdown('<div class="analysis-section strengths">', unsafe_allow_html=True)
                    st.markdown("#### 강점", unsafe_allow_html=True)
                    strengths = analysis_result.get("strengths", [])
                    for strength in strengths:
                        st.markdown(f'<div class="analysis-item">✓ {strength}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # 개선 영역
                    st.markdown('<div class="analysis-section improvements">', unsafe_allow_html=True)
                    st.markdown("#### 개선 영역", unsafe_allow_html=True)
                    improvement_areas = analysis_result.get("improvement_areas", [])
                    for area in improvement_areas:
                        st.markdown(f'<div class="analysis-item">△ {area}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)

            # 맞춤형 추천사항
            st.markdown('<div class="recommendations">',
                        unsafe_allow_html=True)
            st.markdown("### 맞춤형 추천사항")
            recommendations = analysis_result.get(
                "recommendations", [])
            for i, recommendation in enumerate(recommendations, 1):
                st.markdown(
                    f'<div class="recommendation-item">{i}. {recommendation}</div>',
                    unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Allow downloading the analysis
            if st.button("분석 결과 다운로드"):
                import json
                import base64

                analysis_json = json.dumps(analysis_result,
                                           indent=4)
                b64 = base64.b64encode(
                    analysis_json.encode()).decode()
                href = f'<a href="data:application/json;base64,{b64}" download="resume_analysis.json" class="download-btn">분석 결과 JSON 다운로드</a>'
                st.markdown(href, unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
        elif st.session_state.resume_processed and not st.session_state.analysis_result:
             st.error("분석 결과가 없습니다. 이력서를 다시 업로드해주세요.")

# Footer (Ensure it's outside the main 'if/else job_id' block)
st.markdown('<footer>© 2025 무한상사 채용 플랫폼 - 모든 권리 보유</footer>', unsafe_allow_html=True)
