import streamlit as st
from openai import OpenAI

st.title("채팅: GPT-5 미니 (응답 API)")

# 1) 메인 페이지에서 API Key 가져오기
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠ 먼저 메인 페이지에서 OpenAI API Key를 입력해주세요.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# 2) 대화 내용 저장
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 3) Clear 버튼: 대화 내용만 비우기 (rerun 안 씀)
if st.button("🧹 맑다"):
    st.session_state.chat_history = []

st.write("아래 입력창에 메시지를 입력하면 GPT-5 Mini와 대화할 수 있습니다.")

# 4) 기존 대화 출력
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5) 새 메시지 입력 & Responses API 호출
user_msg = st.chat_input("메시지를 입력하세요")

if user_msg:
    # (1) user 메시지 저장 + 출력
    st.session_state.chat_history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # (2) 지금까지 대화 + system 프롬프트를 input으로 사용
    inputs = [{"role": "system", "content": "You are a helpful assistant."}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.chat_history
    ]

    # (3) 모델 응답
    with st.chat_message("assistant"):
        with st.spinner("생각 중..."):
            resp = client.responses.create(
                model="gpt-5-mini",
                input=inputs,
            )
            answer = resp.output_text
            st.markdown(answer)

    # (4) assistant 메시지 저장
    st.session_state.chat_history.append(
        {"role": "assistant", "content": answer}
    )
