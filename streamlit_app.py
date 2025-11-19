import streamlit as st
from openai import OpenAI

# 페이지 기본 설정
st.set_page_config(page_title="GPT-5 Mini Q&A", page_icon="🤖")

st.title("실습 1: GPT-5 Mini 질문/답변 앱")

# 1) session_state 에 API Key 저장 ------------------------------------------------
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.subheader("1. OpenAI API Key 입력")

st.session_state.api_key = st.text_input(
    "OpenAI API Key를 입력하세요",
    type="password",                   # 비밀번호 형식
    value=st.session_state.api_key,    # 페이지 새로고침/이동 후에도 유지
    placeholder="sk- 로 시작하는 키를 입력하세요",
)

st.caption("⚠️ 과제 제출 전에 API Key는 꼭 지우거나 빈 값으로 바꾸고 제출하세요.")


# 2) 질문 입력 --------------------------------------------------------------------
st.subheader("2. 질문을 입력하세요")

question = st.text_input("질문", placeholder="예) 부산의 날씨를 알려줘")



# 3) gpt-5-mini 호출 함수 (캐시 적용) --------------------------------------------
@st.cache_data(show_spinner=True)
def ask_gpt(api_key: str, user_question: str) -> str:
    """
    같은 API Key + 같은 질문이면
    다시 실행해도 이전 결과를 재사용하도록 캐시하는 함수.
    """
    if not api_key:
        return "⚠️ 먼저 OpenAI API Key를 입력해주세요."
    if not user_question:
        return "⚠️ 질문을 입력해주세요."

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "developer", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_question},
        ],
    )

    return response.choices[0].message.content


# 4) 버튼 눌러서 응답 받기 --------------------------------------------------------
if st.button("질문 보내기"):
    answer = ask_gpt(st.session_state.api_key, question)
    st.markdown("### 💬 모델의 응답")
    st.write(answer)
