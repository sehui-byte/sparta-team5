import streamlit as st

st.set_page_config(page_title="채용 상세", layout="wide")

# st.title("채용 상세 페이지 (job_card1.py)")

# 이전 페이지에서 선택된 작업을 가져옴
selected_job = st.session_state.get('selected_job', None)

if selected_job:
    st.title("자세한 채용 정보")
    st.markdown(f"**회사**: {selected_job['company']}")
    st.markdown(f"**직무**: {selected_job['title']}")
    st.markdown(f"**위치**: {selected_job['location']}")
    st.markdown(f"**경력**: {selected_job['experience']}")
    st.markdown(f"**급여**: {selected_job['salary']}")
    st.markdown(f"**기술스택**: {', '.join(selected_job['skills'])}")

    if st.button("지원하기"):
        st.success("지원이 완료되었습니다!")
else:
    st.write("선택된 채용 정보가 없습니다.")
