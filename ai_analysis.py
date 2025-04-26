import os
import json
import streamlit as st
from openai import OpenAI
import re

# The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# Do not change this unless explicitly requested by the user.


def get_qualification_metrics(job_title):
    """
    각 직무별 자격 요건 및 핵심 역량 지표를 반환합니다.

    Args:
        job_title (str): 직무 제목

    Returns:
        dict: 직무별 자격 요건 및 핵심 역량 지표
    """
    # 직무별 자격 요건 정의 (이미지 기반)
    qualification_metrics = {
        "인사 담당자": {
            "academic": "전공 선호(경영, 심리), 학점 3.0↑",
            "language": "영어(TOEIC 800+), 중요",
            "certificate": "직무 관련 자격증(사내강사, HRD) 가산",
            "experience": "인턴 경험 (HR팀 경험 우대)",
            "skills": "엑셀 중상급, 데이터 분석 도구, HR포탈, 리더십 활동 가산"
        },
        "재무/회계 담당자": {
            "academic": "전공 필수(회계/경영), 학점 3.2↑",
            "language": "영어(TOEIC 700+), 참고",
            "certificate": "전산회계2급 이상 필수",
            "experience": "인턴 필수 (회계법인, 재경팀 등)",
            "skills": "엑셀 중상급, 회계시스템(더존) 활용, 없음(크게 중요하지 않음)"
        },
        "영업 담당자": {
            "academic": "전공 무관, 학점 2.8↑",
            "language": "영어(TOEIC 700+), 중요",
            "certificate": "필요없음(우대시 유통관리사 등)",
            "experience": "인턴/아르바이트 매우 중요 (세일즈)",
            "skills": "커뮤니케이션, 협상 스킬, 동아리, 판매량 대회 등 우대"
        },
        "IT 개발자": {
            "academic": "전공 선호(컴퓨터공학, 소프트웨어 관련), 학점 3.0↑",
            "language": "영어(TOEIC 750+), 중요",
            "certificate": "정보처리기사, 클라우드 자격증 등 우대",
            "experience": "인턴 또는 프로젝트 경험 필수",
            "skills": "프로그래밍 언어(React, TypeScript 등), 버전 관리 시스템"
        }
    }

    # 직무별 핵심 역량 지표 정의
    competency_metrics = {
        "인사 담당자": {
            "hr_knowledge": "인사 관련 법규 및 제도 이해도",
            "recruitment": "채용 및 선발 역량",
            "employee_relations": "직원 관계 관리 능력",
            "organizational_development": "조직 개발 및 문화 형성 능력",
            "communication": "커뮤니케이션 능력",
            "data_analysis": "인사 데이터 분석 능력"
        },
        "재무/회계 담당자": {
            "accounting_principles": "회계 원칙 이해도",
            "financial_analysis": "재무 분석 능력",
            "regulatory_compliance": "법규 준수 및 이해도",
            "budget_management": "예산 관리 능력",
            "risk_assessment": "리스크 평가 능력",
            "reporting_skills": "보고서 작성 및 데이터 표현 능력"
        },
        "영업 담당자": {
            "client_relationship": "고객 관계 구축 능력",
            "negotiation": "협상 능력",
            "market_knowledge": "시장 및 제품 지식",
            "goal_orientation": "목표 지향적 성과 달성 능력",
            "presentation_skills": "프레젠테이션 및 제안 능력",
            "adaptability": "적응력 및 대응 능력"
        },
        "IT 개발자": {
            "technical_skills": "기술적 역량 (프로그래밍 언어, 프레임워크, 개발 도구)",
            "problem_solving": "문제 해결 능력",
            "system_design": "시스템 설계 및 아키텍처 이해도",
            "code_quality": "코드 품질 및 최적화 능력",
            "teamwork": "팀 협업 능력",
            "continuous_learning": "지속적 학습 능력"
        }
    }

    # 요청한 직무 제목에 대한 데이터 반환
    # 없는 경우 빈 딕셔너리 반환 (기본값을 사용하지 않도록 수정)
    return {
        "qualifications": qualification_metrics.get(job_title, {}),
        "competencies": competency_metrics.get(job_title, {})
    }


def get_competency_metrics(job_title):
    """
    각 직무별 핵심 역량 지표를 반환합니다.

    Args:
        job_title (str): 직무 제목

    Returns:
        dict: 직무별 핵심 역량 지표
    """
    return get_qualification_metrics(job_title)["competencies"]


def analyze_resume(resume_text, job_title, job_description, job_requirements):
    """
    Analyze the resume against job requirements using OpenAI API

    Args:
        resume_text (str): Text content of the resume
        job_title (str): The title of the job
        job_description (str): The job description text
        job_requirements (list): List of job requirements

    Returns:
        dict: Analysis results including success rate, strengths, improvement areas, recommendations, and competency ratings
    """

    try:
        # Get API key from environment variable
        os.environ["OPENAI_API_KEY"] = st.secrets["API_KEY"]
        api_key = os.environ.get("OPENAI_API_KEY")

        # 규칙 기반 평가를 사용할지 여부 결정 (규칙 기반 평가로 변경)
        use_rule_based = True  # True이면 규칙 기반 평가, False이면 OpenAI API 사용

        if use_rule_based:
            return get_rule_based_analysis(resume_text, job_title)

        if not api_key:
            st.warning(
                "OpenAI API 키를 찾을 수 없습니다. 데모용 테스트 응답을 사용합니다. 전체 기능을 사용하려면 OPENAI_API_KEY 환경 변수를 설정하세요."
            )
            return get_test_analysis(job_title)

        client = OpenAI(api_key=api_key)

        # Format job requirements as a string
        requirements_text = "\n".join([f"- {req}" for req in job_requirements])

        # 직무별 자격 요건 및 핵심 역량 지표 가져오기
        qual_metrics = get_qualification_metrics(job_title)
        competency_metrics = qual_metrics["competencies"]
        qualification_metrics = qual_metrics.get("qualifications", {})

        # 핵심 역량 지표 텍스트 구성
        competency_metrics_text = "\n".join(
            [f"- {key}: {value}" for key, value in competency_metrics.items()])

        # 자격 요건 텍스트 구성
        qualification_text = ""
        if qualification_metrics:
            qualification_text = "채용 자격 요건:\n"
            for category, requirement in qualification_metrics.items():
                if category == "academic":
                    qualification_text += f"- 학력: {requirement}\n"
                elif category == "language":
                    qualification_text += f"- 어학: {requirement}\n"
                elif category == "certificate":
                    qualification_text += f"- 자격증: {requirement}\n"
                elif category == "experience":
                    qualification_text += f"- 경험: {requirement}\n"
                elif category == "skills":
                    qualification_text += f"- 스킬: {requirement}\n"

        prompt = f"""
        AI 커리어 어드바이저로서 {job_title} 직책에 대한 다음 이력서를 분석하세요.

        직무 설명:
        {job_description}

        직무 요구사항:
        {requirements_text}

        {qualification_text}

        핵심 역량 지표:
        {competency_metrics_text}

        지원자 이력서:
        {resume_text}

        다음 정보를 포함한 상세 분석을 JSON 형식으로 제공하세요:
        1. success_rate: 지원자가 직무 요구사항을 충족하는 정도를 나타내는 백분율(0-100)
        2. strengths: 직무와 잘 맞는 이력서의 강점 3-5개 목록
        3. improvement_areas: 지원자가 직무 요구사항을 더 잘 충족하기 위해 개선할 수 있는 영역 3-5개 목록
        4. recommendations: 지원자의 합격 가능성을 높이기 위한 구체적이고 실행 가능한 추천사항 3-5개 목록
        5. competency_ratings: 각 핵심 역량 지표에 대한 0-100 점수 평가. 각 역량별로 점수와 간략한 설명 포함
        6. qualification_ratings: 각 자격 요건에 대한 평가. 학력, 어학, 자격증, 경험, 스킬 각각에 대해 충족 여부 및 점수(0-100) 평가

        응답은 이 여섯 가지 키만 포함하는 유효한 JSON 객체여야 합니다.
        모든 분석 결과는 한국어로 작성해 주세요.
        """

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "system",
                "content": "당신은 전문적인 커리어 어드바이저이자 이력서 분석가입니다. 한국어로 응답하세요."
            }, {
                "role": "user",
                "content": prompt
            }],
            response_format={"type": "json_object"},
            max_tokens=1500)

        result = json.loads(response.choices[0].message.content)

        # Ensure all expected keys are present
        required_keys = [
            "success_rate", "strengths", "improvement_areas", "recommendations"
        ]
        for key in required_keys:
            if key not in result:
                result[key] = [] if key != "success_rate" else 0

        return result

    except Exception as e:
        st.error(f"AI 분석 중 오류 발생: {str(e)}")
        return None


def get_rule_based_analysis(resume_text, job_title):
    """
    규칙 기반의 고정된 점수 평가 시스템을 사용하여 이력서를 분석합니다.
    특정 키워드와 패턴에 따라 일관된 점수를 부여합니다.

    Args:
        resume_text (str): 이력서 텍스트
        job_title (str): 직무 제목

    Returns:
        dict: 분석 결과
    """
    resume_lower = resume_text.lower()  # 대소문자 구분 없이 검색하기 위해 소문자로 변환

    # 기본 결과 구조 설정
    result = {
        "success_rate": 0,
        "strengths": [],
        "improvement_areas": [],
        "recommendations": [],
        "competency_ratings": {},
        "qualification_ratings": {
            "academic": {"score": 0, "description": "", "meets_requirement": False},
            "language": {"score": 0, "description": "", "meets_requirement": False},
            "certificate": {"score": 0, "description": "", "meets_requirement": False},
            "experience": {"score": 0, "description": "", "meets_requirement": False},
            "skills": {"score": 0, "description": "", "meets_requirement": False}
        }
    }

    # 1. 학력 평가
    academic_score = 60  # 기본 점수
    academic_description = "학력 정보가 충분하지 않습니다."
    
    # 대학교 등급별 점수 부여
    top_universities = ["서울대", "연세대", "고려대", "카이스트"]
    good_universities = ["성균관대", "한양대", "이화여대", "서강대", "중앙대", "경희대", "한국외대", "Kyung Hee University"]
    
    for univ in top_universities:
        if univ in resume_text:
            academic_score = 95
            academic_description = f"{univ} 출신으로 최상위권 학력"
            break
    
    if academic_score < 90:  # 최상위권이 아니라면 좋은 대학 체크
        for univ in good_universities:
            if univ in resume_text:
                academic_score = 85
                academic_description = f"{univ} 출신으로 우수한 학력"
                break
    
    # 인서울 대학 키워드
    if academic_score < 80 and ("인서울" in resume_text or "4년제" in resume_text):
        academic_score = 75
        academic_description = "인서울 4년제 대학 학력"
    
    # 학점 체크
    gpa_patterns = [
        r'학점[\s]*:[\s]*([0-9]+\.[0-9]+)',
        r'GPA[\s]*:[\s]*([0-9]+\.[0-9]+)',
        r'평점[\s]*:[\s]*([0-9]+\.[0-9]+)'
    ]
    
    for pattern in gpa_patterns:
        match = re.search(pattern, resume_text)
        if match:
            try:
                gpa = float(match.group(1))
                if gpa >= 4.0:
                    academic_score += 10
                    academic_description += ", 우수한 학점(4.0 이상)"
                elif gpa >= 3.5:
                    academic_score += 7
                    academic_description += ", 양호한 학점(3.5 이상)"
                elif gpa >= 3.0:
                    academic_score += 5
                    academic_description += ", 평균 이상 학점(3.0 이상)"
            except:
                pass
            break
    
    # 전공 체크 (직무별)
    if job_title == "IT 개발자":
        relevant_majors = ["컴퓨터", "소프트웨어", "정보", "전산", "전자", "컴공"]
        for major in relevant_majors:
            if major in resume_text:
                academic_score += 5
                academic_description += f", {major} 관련 전공"
                break
    elif job_title == "인사 담당자":
        relevant_majors = ["경영", "인사", "심리", "HR", "인적자원"]
        for major in relevant_majors:
            if major in resume_text:
                academic_score += 5
                academic_description += f", {major} 관련 전공"
                break
    
    # 최종 학력 점수 조정 (최대 100점)
    academic_score = min(100, academic_score)
    
    # 2. 어학 능력 평가
    language_score = 50  # 기본 점수
    language_description = "어학 능력 정보가 충분하지 않습니다."
    
    # 토익 점수 체크
    toeic_patterns = [
        r'토익[\s]*:[\s]*([0-9]+)',
        r'TOEIC[\s]*:[\s]*([0-9]+)',
        r'토익[\s]*([0-9]+)점'
    ]
    
    for pattern in toeic_patterns:
        match = re.search(pattern, resume_text)
        if match:
            try:
                toeic = int(match.group(1))
                if toeic >= 900:
                    language_score = 95
                    language_description = f"토익 {toeic}점으로 매우 우수"
                elif toeic >= 850:
                    language_score = 90
                    language_description = f"토익 {toeic}점으로 우수"
                elif toeic >= 800:
                    language_score = 85
                    language_description = f"토익 {toeic}점으로 상위권"
                elif toeic >= 750:
                    language_score = 80
                    language_description = f"토익 {toeic}점으로 양호"
                elif toeic >= 700:
                    language_score = 75
                    language_description = f"토익 {toeic}점으로 평균 이상"
                elif toeic >= 650:
                    language_score = 70
                    language_description = f"토익 {toeic}점으로 보통"
                elif toeic >= 600:
                    language_score = 65
                    language_description = f"토익 {toeic}점으로 기본 수준"
                else:
                    language_score = 60
                    language_description = f"토익 {toeic}점으로 기초 수준"
            except:
                pass
            break
    
    # 3. 자격증 평가
    certificate_score = 60  # 기본 점수
    certificate_description = "관련 자격증 정보가 충분하지 않습니다."
    
    # 직무별 관련 자격증
    if job_title == "IT 개발자":
        relevant_certs = ["정보처리기사", "SQLD", "AWS", "Azure", "Google", "리눅스마스터", 
                          "네트워크", "보안", "정보보안", "CCNA", "클라우드"]
        cert_count = 0
        found_certs = []
        
        for cert in relevant_certs:
            if cert in resume_text:
                cert_count += 1
                found_certs.append(cert)
        
        if cert_count > 0:
            certificate_score = 60 + (cert_count * 10)
            certificate_description = f"{', '.join(found_certs)} 자격증 보유"
            
    elif job_title == "인사 담당자":
        relevant_certs = ["공인노무사", "인사관리사", "경영지도사", "CS", "사내강사", "NLP", "코칭"]
        cert_count = 0
        found_certs = []
        
        for cert in relevant_certs:
            if cert in resume_text:
                cert_count += 1
                found_certs.append(cert)
        
        if cert_count > 0:
            certificate_score = 60 + (cert_count * 10)
            certificate_description = f"{', '.join(found_certs)} 자격증 보유"
    
    # 최종 자격증 점수 조정 (최대 100점)
    certificate_score = min(100, certificate_score)
    
    # 4. 경험 평가
    experience_score = 60  # 기본 점수
    experience_description = "관련 경험 정보가 충분하지 않습니다."
    
    # 인턴 경험 체크
    if "인턴" in resume_text:
        experience_score += 10
        experience_description = "인턴 경험 보유"
    
    # 프로젝트 경험 체크
    if "프로젝트" in resume_text:
        experience_score += 10
        experience_description += ", 프로젝트 경험 보유"
    
    # 경력 연차 체크
    year_patterns = [
        r'([0-9]+)년차',
        r'([0-9]+)[\s]*년[\s]*경력',
        r'경력[\s]*:[\s]*([0-9]+)[\s]*년'
    ]
    
    for pattern in year_patterns:
        match = re.search(pattern, resume_text)
        if match:
            try:
                years = int(match.group(1))
                if years >= 5:
                    experience_score += 25
                    experience_description += f", {years}년 경력으로 경험 풍부"
                elif years >= 3:
                    experience_score += 20
                    experience_description += f", {years}년 경력으로 경험 우수"
                elif years >= 1:
                    experience_score += 15
                    experience_description += f", {years}년 경력"
            except:
                pass
            break
    
    # 최종 경험 점수 조정 (최대 100점)
    experience_score = min(100, experience_score)
    
    # 5. 스킬 평가
    skills_score = 60  # 기본 점수
    skills_description = "관련 스킬 정보가 충분하지 않습니다."
    
    # 직무별 관련 스킬
    if job_title == "IT 개발자":
        tech_skills = ["Java", "Python", "JavaScript", "React", "Node.js", "Spring", 
                      "SQL", "AWS", "Git", "Docker", "kubernetes", "C#", "TypeScript"]
        skill_count = 0
        found_skills = []
        
        for skill in tech_skills:
            if skill.lower() in resume_lower:
                skill_count += 1
                found_skills.append(skill)
        
        if skill_count > 0:
            skills_score = 60 + (skill_count * 5)
            skills_description = f"{', '.join(found_skills)} 스킬 보유"
            
    elif job_title == "인사 담당자":
        hr_skills = ["인사관리", "채용", "교육", "평가", "급여", "복리후생", "노무", "조직문화", 
                    "HR", "성과관리", "인재개발", "엑셀", "PowerPoint", "Word"]
        skill_count = 0
        found_skills = []
        
        for skill in hr_skills:
            if skill.lower() in resume_lower:
                skill_count += 1
                found_skills.append(skill)
        
        if skill_count > 0:
            skills_score = 60 + (skill_count * 5)
            skills_description = f"{', '.join(found_skills)} 스킬 보유"
    
    # 최종 스킬 점수 조정 (최대 100점)
    skills_score = min(100, skills_score)
    
    # 자격 요건 점수 설정
    result["qualification_ratings"]["academic"] = {
        "score": academic_score,
        "description": academic_description,
        "meets_requirement": academic_score >= 70
    }
    
    result["qualification_ratings"]["language"] = {
        "score": language_score,
        "description": language_description,
        "meets_requirement": language_score >= 70
    }
    
    result["qualification_ratings"]["certificate"] = {
        "score": certificate_score,
        "description": certificate_description,
        "meets_requirement": certificate_score >= 70
    }
    
    result["qualification_ratings"]["experience"] = {
        "score": experience_score,
        "description": experience_description,
        "meets_requirement": experience_score >= 70
    }
    
    result["qualification_ratings"]["skills"] = {
        "score": skills_score,
        "description": skills_description,
        "meets_requirement": skills_score >= 70
    }
    
    # 역량 평가 - 직무별 설정
    if job_title == "IT 개발자":
        result["competency_ratings"] = {
            "technical_skills": {
                "score": skills_score,
                "description": "기술적 역량: " + skills_description
            },
            "problem_solving": {
                "score": max(65, min(90, skills_score - 5)),
                "description": "문제 해결 능력: 프로젝트 경험에서 문제 해결 역량 확인"
            },
            "system_design": {
                "score": max(60, min(85, skills_score - 10)),
                "description": "시스템 설계 능력: 기본적인 시스템 설계 역량 보유"
            },
            "code_quality": {
                "score": max(65, min(90, skills_score - 5)),
                "description": "코드 품질: 코드 작성 및 품질 관리 역량 확인"
            },
            "teamwork": {
                "score": 75,
                "description": "팀 협업 능력: 프로젝트 및 업무 경험에서 협업 역량 확인"
            },
            "continuous_learning": {
                "score": max(70, certificate_score),
                "description": "지속적 학습 능력: 자격증 및 새로운 기술 습득 노력 확인"
            }
        }
    elif job_title == "인사 담당자":
        result["competency_ratings"] = {
            "hr_knowledge": {
                "score": max(skills_score, certificate_score),
                "description": "인사 지식: 관련 지식 및 자격증 보유"
            },
            "recruitment": {
                "score": skills_score if "채용" in resume_text else 65,
                "description": "채용 역량: 채용 관련 경험 및 지식 보유"
            },
            "employee_relations": {
                "score": 70,
                "description": "직원 관계 관리: 조직 내 인간관계 및 관리 역량"
            },
            "organizational_development": {
                "score": 70,
                "description": "조직 개발 능력: 조직문화 및 개발 역량"
            },
            "communication": {
                "score": 75,
                "description": "커뮤니케이션 능력: 의사소통 및 협업 역량"
            },
            "data_analysis": {
                "score": 65,
                "description": "데이터 분석 능력: 기본적인 데이터 분석 역량"
            }
        }
    else:
        # 다른 직무에 대한 기본 역량 평가
        result["competency_ratings"] = {
            "job_knowledge": {
                "score": max(skills_score, certificate_score),
                "description": "직무 지식: 관련 지식 및 자격증 보유"
            },
            "communication": {
                "score": 75,
                "description": "커뮤니케이션 능력: 의사소통 및 협업 역량"
            },
            "problem_solving": {
                "score": 70,
                "description": "문제 해결 능력: 업무 경험에서의 문제 해결 역량"
            },
            "adaptability": {
                "score": 75,
                "description": "적응력: 새로운 환경 및 변화에 적응하는 역량"
            },
            "teamwork": {
                "score": 75,
                "description": "팀워크: 조직 내 협업 및 팀 프로젝트 역량"
            }
        }
    
    # 강점, 개선사항, 추천사항 설정 (직무별 분기)
    if job_title == "IT 개발자":
        # 강점
        if skills_score >= 80:
            result["strengths"].append("다양한 기술 스택에 대한 이해와 활용 능력이 우수함")
        if certificate_score >= 75:
            result["strengths"].append("관련 자격증 보유로 전문성을 입증함")
        if academic_score >= 80:
            result["strengths"].append("관련 전공과 우수한 학업 성취도를 보여줌")
        if experience_score >= 75:
            result["strengths"].append("실무 경험을 통한 실전 역량을 갖추고 있음")
        if "프로젝트" in resume_text:
            result["strengths"].append("다양한 프로젝트 경험을 보유하고 있음")
        
        # 개선사항
        if skills_score < 75:
            result["improvement_areas"].append("최신 기술 스택에 대한 경험 강화 필요")
        if "테스트" not in resume_lower and "tdd" not in resume_lower:
            result["improvement_areas"].append("테스트 방법론에 대한 경험 부족")
        if certificate_score < 70:
            result["improvement_areas"].append("관련 자격증 추가 취득으로 전문성 강화 필요")
        if "sql" not in resume_lower and "데이터베이스" not in resume_lower:
            result["improvement_areas"].append("데이터베이스 관련 기술 역량 보강 필요")
        if "git" not in resume_lower:
            result["improvement_areas"].append("버전 관리 시스템 경험 강조 필요")
        
        # 추천사항
        if skills_score < 80:
            result["recommendations"].append("최신 개발 트렌드에 맞는 기술 스택 학습 및 프로젝트 경험 추가")
        if certificate_score < 75:
            result["recommendations"].append("직무 관련 자격증 취득으로 전문성 강화")
        if "테스트" not in resume_lower:
            result["recommendations"].append("TDD 등 테스트 방법론 학습 및 프로젝트 적용 경험 추가")
        if experience_score < 75:
            result["recommendations"].append("오픈소스 프로젝트 참여 또는 포트폴리오 강화")
        result["recommendations"].append("프로젝트 경험에서 문제 해결 과정을 구체적으로 기술하여 문제 해결 능력 강조")
    
    elif job_title == "인사 담당자":
        # 강점
        if skills_score >= 80:
            result["strengths"].append("인사 관련 다양한 업무 영역에 대한 이해도가 높음")
        if certificate_score >= 75:
            result["strengths"].append("관련 자격증 보유로 전문성을 입증함")
        if academic_score >= 80:
            result["strengths"].append("관련 전공과 우수한 학업 성취도를 보여줌")
        if experience_score >= 75:
            result["strengths"].append("인사 분야 실무 경험을 통한 실전 역량 보유")
        if "채용" in resume_text:
            result["strengths"].append("채용 프로세스에 대한 이해 및 경험이 있음")
        
        # 개선사항
        if skills_score < 75:
            result["improvement_areas"].append("인사 관리 전반에 대한 경험 강화 필요")
        if "노무" not in resume_lower and "법규" not in resume_lower:
            result["improvement_areas"].append("노동법 및 인사 법규에 대한 지식 보강 필요")
        if certificate_score < 70:
            result["improvement_areas"].append("관련 자격증 추가 취득으로 전문성 강화 필요")
        if "데이터" not in resume_lower and "분석" not in resume_lower:
            result["improvement_areas"].append("데이터 기반 의사결정 역량 강화 필요")
        if "조직문화" not in resume_lower:
            result["improvement_areas"].append("조직문화 개선 관련 경험 부족")
        
        # 추천사항
        if skills_score < 80:
            result["recommendations"].append("인사 관리 다양한 영역(채용, 교육, 평가, 보상 등) 경험 확대")
        if certificate_score < 75:
            result["recommendations"].append("인사 관리사 또는 노무 관련 자격증 취득 고려")
        if "노무" not in resume_lower:
            result["recommendations"].append("노동법 및 인사 관련 법규 이해도 강화")
        if "데이터" not in resume_lower:
            result["recommendations"].append("데이터 분석 도구 활용 및 인사 지표 관리 경험 추가")
        result["recommendations"].append("인사 제도 개선이나 조직문화 활동 경험을 구체적으로 기술")
    
    else:
        # 다른 직무에 대한 기본 강점/개선사항/추천사항
        result["strengths"] = [
            "직무 관련 기본 지식과 역량 보유",
            "학업 및 경험을 통한 역량 개발",
            "기본적인 커뮤니케이션 능력 보유"
        ]
        
        result["improvement_areas"] = [
            "직무 특화 역량 강화 필요",
            "관련 자격증 및 전문성 강화 필요",
            "실무 경험 추가 필요"
        ]
        
        result["recommendations"] = [
            "직무 관련 실무 경험 확대",
            "관련 자격증 취득으로 전문성 강화",
            "직무 특화 기술 및 역량 개발",
            "커뮤니케이션 및 협업 능력 강조"
        ]
    
    # 최종 성공률 계산 (자격 요건 점수 평균)
    qualification_scores = [
        result["qualification_ratings"]["academic"]["score"],
        result["qualification_ratings"]["language"]["score"],
        result["qualification_ratings"]["certificate"]["score"],
        result["qualification_ratings"]["experience"]["score"],
        result["qualification_ratings"]["skills"]["score"]
    ]
    
    result["success_rate"] = int(sum(qualification_scores) / len(qualification_scores))
    
    # 결과에 충분한 항목이 없는 경우 보완
    while len(result["strengths"]) < 3:
        if "직무에 대한 관심과 열정을 보여줌" not in result["strengths"]:
            result["strengths"].append("직무에 대한 관심과 열정을 보여줌")
        elif "기본적인 직무 역량 보유" not in result["strengths"]:
            result["strengths"].append("기본적인 직무 역량 보유")
        elif "학습 의지와 발전 가능성을 갖춤" not in result["strengths"]:
            result["strengths"].append("학습 의지와 발전 가능성을 갖춤")
        else:
            result["strengths"].append("커뮤니케이션 및 협업 능력 보유")
    
    while len(result["improvement_areas"]) < 3:
        if "실무 경험 강화 필요" not in result["improvement_areas"]:
            result["improvement_areas"].append("실무 경험 강화 필요")
        elif "전문성 및 자격증 보강 필요" not in result["improvement_areas"]:
            result["improvement_areas"].append("전문성 및 자격증 보강 필요")
        elif "직무 관련 기술 역량 향상 필요" not in result["improvement_areas"]:
            result["improvement_areas"].append("직무 관련 기술 역량 향상 필요")
        else:
            result["improvement_areas"].append("문제 해결 능력 강화 필요")
    
    while len(result["recommendations"]) < 3:
        if "실무 중심 포트폴리오 구성" not in result["recommendations"]:
            result["recommendations"].append("실무 중심 포트폴리오 구성")
        elif "직무 관련 교육 및 자격증 취득" not in result["recommendations"]:
            result["recommendations"].append("직무 관련 교육 및 자격증 취득")
        elif "직무 역량 강화를 위한 프로젝트 참여" not in result["recommendations"]:
            result["recommendations"].append("직무 역량 강화를 위한 프로젝트 참여")
        else:
            result["recommendations"].append("이력서에 성과와 결과 중심의 경험 기술")
    
    return result


def get_test_analysis(job_title):
    """
    API 키가 없을 때 직무에 맞는 테스트 분석 결과를 반환합니다.

    Args:
        job_title (str): 직무 제목

    Returns:
        dict: 테스트 분석 결과
    """
    # 직무별 테스트 분석 결과
    test_analyses = {
        "IT 개발자": {
            "success_rate":
            75,
            "strengths": [
                "관련 프로그래밍 언어에 대한 깊은 기술적 배경 보유", "실무 적용 능력을 보여주는 다양한 프로젝트 경험",
                "발표 및 문서화를 통해 입증된 효과적인 커뮤니케이션 능력", "협업 팀 환경에서의 업무 경험 풍부",
                "지속적인 역량 개발을 보여주는 자기주도적 학습 능력"
            ],
            "improvement_areas": [
                "직무 요구사항에 언급된 특정 프레임워크에 대한 경험 제한적",
                "특히 NoSQL 기술에 관한 데이터베이스 지식 강화 필요",
                "테스트 방법론에 대한 더 많은 강조가 유익할 것", "문제 해결 접근 방식을 더 명확하게 강조할 필요",
                "버전 관리 시스템에 대한 경험 증명이 제한적"
            ],
            "recommendations": [
                "기술적 넓이를 보여주기 위해 관련 프레임워크 작업의 구체적인 예시 추가",
                "다양한 데이터베이스 유형에 대한 프로젝트나 경험 강조",
                "이전 프로젝트에서 사용한 테스트 방법론에 대한 세부 정보 포함",
                "구체적인 사례를 통해 문제 해결 능력을 강조하는 이력서 재구성",
                "자격 요건을 강화하기 위해 관련 기술 인증 취득 고려"
            ],
            "competency_ratings": {
                "technical_skills": {
                    "score": 80,
                    "description": "다양한 프로그래밍 언어와 도구에 대한 강한 이해도를 보여줌"
                },
                "problem_solving": {
                    "score": 75,
                    "description": "복잡한 문제를 체계적으로 해결하는 능력이 있으나 더 명확한 사례 필요"
                },
                "system_design": {
                    "score": 65,
                    "description": "기본적인 시스템 설계 지식은 있으나 대규모 아키텍처 경험 부족"
                },
                "code_quality": {
                    "score": 70,
                    "description": "깔끔한 코드 작성 능력을 보여주나 테스트 관련 내용 부족"
                },
                "teamwork": {
                    "score": 85,
                    "description": "여러 프로젝트에서 팀 협업 경험이 풍부함"
                },
                "continuous_learning": {
                    "score": 90,
                    "description": "새로운 기술 습득과 자기계발에 대한 높은 의지 보임"
                }
            },
            "qualification_ratings": {
                "academic": {
                    "score": 75,
                    "description": "컴퓨터과학 전공, 학점 3.2로 양호",
                    "meets_requirement": True
                },
                "language": {
                    "score": 80,
                    "description": "TOEIC 830점으로 우수",
                    "meets_requirement": True
                },
                "certificate": {
                    "score": 70,
                    "description": "정보처리기사 보유",
                    "meets_requirement": True
                },
                "experience": {
                    "score": 75,
                    "description": "관련 인턴십 경험 6개월",
                    "meets_requirement": True
                },
                "skills": {
                    "score": 85,
                    "description": "다양한 프로그래밍 언어 및 개발 환경 숙련도 높음",
                    "meets_requirement": True
                }
            }
        },
        "인사 담당자": {
            "success_rate":
            70,
            "strengths": [
                "다양한 채용 프로세스 관리 경험 보유", "인사 시스템 도입 및 운영 경험",
                "직원 교육 프로그램 개발 및 실행 능력", "조직 문화 개선 활동에 적극적 참여",
                "데이터 기반 인사 의사결정 경험"
            ],
            "improvement_areas": [
                "최신 인사 관련 법규 지식 보강 필요", "인력 유지 전략에 대한 경험 제한적",
                "성과 평가 시스템 개발 경험 부족", "다양성 및 포용성 관련 역량 강화 필요",
                "국제적 인사 관리 경험 부족"
            ],
            "recommendations": [
                "최신 노동법 및 인사 규정 관련 교육 이수 및 이력서에 추가",
                "이직률 감소와 관련된 프로젝트나 성과 사례 강조", "성과 관리와 관련된 구체적인 경험이나 교육 과정 추가",
                "다양성 및 포용성 관련 워크숍 참여 또는 관련 활동 경험 강조",
                "글로벌 인사 관리 관련 자격증 또는 교육 고려"
            ],
            "competency_ratings": {
                "hr_knowledge": {
                    "score": 75,
                    "description": "기본적인 인사 제도에 대한 이해는 있으나 최신 법규 지식 보완 필요"
                },
                "recruitment": {
                    "score": 85,
                    "description": "다양한 채용 절차 경험과 선발 기법에 대한 이해도가 높음"
                },
                "employee_relations": {
                    "score": 70,
                    "description": "직원 관계 관리 기본기는 갖추었으나 갈등 관리 경험 부족"
                },
                "organizational_development": {
                    "score": 65,
                    "description": "조직 문화 개선 활동 참여 경험은 있으나 주도적 설계 경험 제한적"
                },
                "communication": {
                    "score": 80,
                    "description": "명확한 소통 능력과 다양한 이해관계자와의 협업 경험 보유"
                },
                "data_analysis": {
                    "score": 60,
                    "description": "기본적인 데이터 분석 경험은 있으나 인사 지표 활용 역량 강화 필요"
                }
            },
            "qualification_ratings": {
                "academic": {
                    "score": 75,
                    "description": "경영학 전공이며 학점 3.1로 기준 충족",
                    "meets_requirement": True
                },
                "language": {
                    "score": 70,
                    "description": "TOEIC 750점으로 기준 미달",
                    "meets_requirement": False
                },
                "certificate": {
                    "score": 60,
                    "description": "관련 자격증 미보유",
                    "meets_requirement": False
                },
                "experience": {
                    "score": 85,
                    "description": "HR 부서 인턴 경험 6개월 보유",
                    "meets_requirement": True
                },
                "skills": {
                    "score": 80,
                    "description": "엑셀 중급 활용 가능, 데이터 분석 도구 사용 경험 있음",
                    "meets_requirement": True
                }
            }
        },
        "재무/회계 담당자": {
            "success_rate":
            80,
            "strengths": [
                "재무제표 작성 및 분석 역량 우수", "회계 규정 및 세법에 대한 깊은 이해",
                "예산 관리 및 재무 계획 수립 경험 풍부", "ERP 시스템 활용 능력 우수",
                "내부 감사 및 통제 시스템 경험"
            ],
            "improvement_areas": [
                "재무 리스크 관리 경험 보강 필요", "국제 회계 기준 적용 경험 제한적",
                "재무 모델링 및 예측 능력 강화 필요", "프로젝트 ROI 분석 경험 부족",
                "디지털 재무 도구 활용 역량 강화 필요"
            ],
            "recommendations": [
                "재무 리스크 관리 관련 프로젝트 경험 또는 교육 강조",
                "IFRS/K-IFRS 관련 지식이나 적용 경험 추가",
                "재무 예측 모델 개발 경험이나 관련 교육 과정 이수 추가",
                "투자 수익률 분석 프로젝트 경험 구체적으로 기술", "최신 재무 분석 도구 활용 능력 습득 및 이력서에 추가"
            ],
            "competency_ratings": {
                "accounting_principles": {
                    "score": 85,
                    "description": "회계 원칙에 대한 탁월한 이해도와 적용 경험 보유"
                },
                "financial_analysis": {
                    "score": 75,
                    "description": "기본적인 재무 분석 역량은 우수하나 고급 모델링 경험 부족"
                },
                "regulatory_compliance": {
                    "score": 80,
                    "description": "국내 회계 법규 준수 능력은 우수하나 국제 기준 경험 제한적"
                },
                "budget_management": {
                    "score": 90,
                    "description": "예산 계획 수립과 실행, 모니터링에 대한 탁월한 경험 보유"
                },
                "risk_assessment": {
                    "score": 65,
                    "description": "기본적인 리스크 평가 능력은 있으나 심화된 분석 경험 필요"
                },
                "reporting_skills": {
                    "score": 85,
                    "description": "명확하고 정확한 재무 보고서 작성 능력과 데이터 시각화 역량 보유"
                }
            },
            "qualification_ratings": {
                "academic": {
                    "score": 85,
                    "description": "회계학 전공이며 학점 3.5로 기준 충족",
                    "meets_requirement": True
                },
                "language": {
                    "score": 75,
                    "description": "TOEIC 720점으로 기준 충족",
                    "meets_requirement": True
                },
                "certificate": {
                    "score": 90,
                    "description": "전산회계 1급 보유",
                    "meets_requirement": True
                },
                "experience": {
                    "score": 80,
                    "description": "회계법인 인턴 6개월 경험 보유",
                    "meets_requirement": True
                },
                "skills": {
                    "score": 85,
                    "description": "엑셀 고급 기술 및 회계 시스템 활용 능력 우수",
                    "meets_requirement": True
                }
            }
        },
        "영업 담당자": {
            "success_rate":
            65,
            "strengths": [
                "고객 관계 구축 및 유지 능력 우수",
                "협상 및 계약 체결 경험 보유",
                "시장 동향 파악 및 경쟁사 분석 능력",
                "목표 지향적인 업무 태도",
                "명확한 커뮤니케이션 능력"
            ],
            "improvement_areas": [
                "영업 전략 수립 경험 강화 필요",
                "고객 니즈 파악을 위한 질문 기술 향상 필요",
                "제안서 작성 능력 개선 필요",
                "거절 처리 및 대응 능력 강화 필요",
                "디지털 마케팅 도구 활용 역량 부족"
            ],
            "recommendations": [
                "다양한 영업 성공 사례 구체적으로 이력서에 추가",
                "고객 유치 및 유지 전략에 대한 성과 수치화하여 제시",
                "영업 관련 교육 과정 이수 또는 관련 자격증 취득 고려",
                "제안서 작성 및 프레젠테이션 역량 강화 활동 추가",
                "CRM 시스템 활용 경험 강조"
            ],
            "competency_ratings": {
                "client_relationship": {
                    "score": 80,
                    "description": "고객과의 관계 형성 및 유지 능력이 우수함"
                },
                "negotiation": {
                    "score": 75,
                    "description": "기본적인 협상 기술은 갖추었으나 복잡한 계약 협상 경험 부족"
                },
                "market_knowledge": {
                    "score": 65,
                    "description": "일반적인 시장 지식은 있으나 산업별 전문 지식 강화 필요"
                },
                "goal_orientation": {
                    "score": 85,
                    "description": "목표 달성을 위한 높은 열정과 꾸준한 성과를 보여줌"
                },
                "presentation_skills": {
                    "score": 60,
                    "description": "기본적인 발표 능력은 있으나 설득력 있는 제안 기술 향상 필요"
                },
                "adaptability": {
                    "score": 70,
                    "description": "다양한 상황에 적응할 수 있는 유연성 보유"
                }
            },
            "qualification_ratings": {
                "academic": {
                    "score": 70,
                    "description": "경영학 전공, 학점 2.9로 기준 근접",
                    "meets_requirement": True
                },
                "language": {
                    "score": 75,
                    "description": "TOEIC 780점으로 기준 충족",
                    "meets_requirement": True
                },
                "certificate": {
                    "score": 60,
                    "description": "관련 자격증 없음",
                    "meets_requirement": True
                },
                "experience": {
                    "score": 65,
                    "description": "판매 관련 아르바이트 경험 있으나 정규 영업 경험 부족",
                    "meets_requirement": False
                },
                "skills": {
                    "score": 75,
                    "description": "소통 능력과 설득력은 우수하나 CRM 시스템 활용 경험 부족",
                    "meets_requirement": True
                }
            }
        }
    }
    
    # 요청된 직무의 분석 결과가 있으면 반환
    if job_title in test_analyses:
        return test_analyses[job_title]
    else:
        # 요청된 직무의 분석 결과가 없는 경우 기본 분석 결과 반환
        st.warning(f"'{job_title}' 직무의 테스트 분석 데이터가 없습니다. 기본 분석 결과를 제공합니다.")
        return test_analyses.get("IT 개발자", {})
