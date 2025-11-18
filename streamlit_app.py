import streamlit as st
from openai import OpenAI
import base64

st.title("GPT-5-mini 질문 + 이미지 생성 웹앱")

# 1. API Key 입력
api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")

# API Key가 있을 때만 클라이언트 생성
client = OpenAI(api_key=api_key) if api_key else None

# -----------------------
# 1) 텍스트 질문 → gpt-5-mini 답변
# -----------------------
st.subheader("1) 텍스트 질문 보내기 (gpt-5-mini)")

question = st.text_area(
    "무엇이든 물어보세요",
    placeholder="예: 부경대학교에 대해 간단히 소개해 줘",
    height=120,
)

if st.button("질문 보내기"):
    if not api_key:
        st.error("먼저 OpenAI API Key를 입력하세요.")
    elif not question.strip():
        st.error("질문을 입력하세요.")
    else:
        try:
            chat = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {"role": "system", "content": "당신은 친절한 한국어 도우미입니다."},
                    {"role": "user", "content": question},
                ],
            )
            answer = chat.choices[0].message.content
            st.subheader("→ 모델의 답변")
            st.write(answer)
        except Exception as e:
            st.error(f"에러가 발생했습니다: {e}")

# -----------------------
# 2) 이미지 프롬프트 → gpt-image-1-mini 이미지 생성
# -----------------------
st.markdown("---")
st.subheader("2) 이미지 생성하기 (gpt-image-1-mini)")

image_prompt = st.text_input(
    "이미지 프롬프트를 입력하세요",
    placeholder="예: 부산 바다 앞에서 춤추는 북극곰 일러스트",
)

if st.button("이미지 생성"):
    if not api_key:
        st.error("먼저 OpenAI API Key를 입력하세요.")
    elif not image_prompt.strip():
        st.error("이미지 프롬프트를 입력하세요.")
    else:
        try:
            # gpt-image-1-mini 모델로 이미지 생성
            img = client.images.generate(
                model="gpt-image-1-mini",
                prompt=image_prompt,
                size="1024x1024",  # ✅ 지원되는 사이즈
            )

            # b64_json 을 디코딩해서 이미지 바이트로 변환
            image_bytes = base64.b64decode(img.data[0].b64_json)

            # 메모리 상의 이미지를 화면에 표시
            st.image(image_bytes, caption="생성된 이미지", use_column_width=True)

        except Exception as e:
            st.error(f"이미지 생성 중 에러가 발생했습니다: {e}")
