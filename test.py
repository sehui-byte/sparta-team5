# app.py
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.title("JD - 이력서 매칭 평가기")

# 입력창 만들기
jd_text = st.text_area("잡 디스크립션 입력", height=200)
resume_text = st.text_area("이력서 입력", height=200)

if st.button("적합도 평가하기"):
    if jd_text and resume_text:
        documents = [jd_text, resume_text]
        tfidf = TfidfVectorizer().fit_transform(documents)
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        st.success(f"📈 매칭률: {similarity * 100:.2f}%")
    else:
        st.warning("JD와 이력서를 모두 입력해 주세요.")

