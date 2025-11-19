import streamlit as st
from openai import OpenAI

st.title("ChatPDF: 업로드한 PDF와 대화하기")

# 1) 메인 페이지에서 API Key 가져오기 --------------------------------
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠ 먼저 메인 페이지에서 OpenAI API Key를 입력해주세요.")
    st.stop()

client = OpenAI(api_key=st.session_state.api_key)

# 2) ChatPDF용 상태 변수들 -------------------------------------------
if "chatpdf_vector_store_id" not in st.session_state:
    st.session_state.chatpdf_vector_store_id = None

if "chatpdf_history" not in st.session_state:
    st.session_state.chatpdf_history = []  # 채팅 로그


# 3) 상단 영역: PDF 업로드 + Clear 버튼 -------------------------------
col1, col2 = st.columns([3, 1])

with col1:
    uploaded_pdf = st.file_uploader(
        "PDF 파일을 업로드하세요 (한 개만)",
        type=["pdf"],
        accept_multiple_files=False,
    )

with col2:
    # Vector store 및 대화 내용 초기화
    if st.button("🧹 Clear", help="Vector store와 대화 내용을 모두 초기화합니다."):
        # 기존 vector store 삭제
        if st.session_state.chatpdf_vector_store_id:
            try:
                client.vector_stores.delete(st.session_state.chatpdf_vector_store_id)
            except Exception:
                # 이미 삭제되었거나 없는 경우는 무시
                pass
        st.session_state.chatpdf_vector_store_id = None
        st.session_state.chatpdf_history = []
        st.success("Vector store와 채팅 기록이 초기화되었습니다.")


# 4) PDF를 Vector Store에 올리기 ------------------------------------
if uploaded_pdf is not None and st.session_state.chatpdf_vector_store_id is None:
    # 아직 vector store가 없고, PDF가 새로 업로드된 경우
    with st.spinner("PDF를 업로드하고 인덱싱 중입니다... (잠시만 기다려주세요)"):
        # vector store 생성
        vector_store = client.vector_stores.create(name="chatpdf-store")

        # 업로드한 pdf 파일을 vector store에 추가 (upload_and_poll 사용)
        file_batch = client.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id,
            files=[uploaded_pdf],  # streamlit UploadedFile 객체 그대로 전달
        )

        st.session_state.chatpdf_vector_store_id = vector_store.id

    st.success("PDF 업로드 및 인덱싱이 완료되었습니다!")

# 5) 대화 UI ---------------------------------------------------------
vs_id = st.session_state.chatpdf_vector_store_id

if vs_id is None:
    st.info("먼저 PDF 파일을 업로드하면, 그 내용을 기반으로 대화할 수 있습니다.")
    st.stop()

st.write("이제 업로드한 PDF 내용에 대해 질문해 보세요!")

# 이전 채팅 로그 출력
for msg in st.session_state.chatpdf_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 새 질문 입력
user_msg = st.chat_input("PDF와 관련해 궁금한 내용을 입력하세요")

if user_msg:
    # (1) user 메시지 화면 + 히스토리에 추가
    st.session_state.chatpdf_history.append({"role": "user", "content": user_msg})
    with st.chat_message("user"):
        st.markdown(user_msg)

    # (2) Responses API + File Search 호출 -------------------------
    with st.chat_message("assistant"):
        with st.spinner("PDF 내용을 검색하는 중입니다..."):
            response = client.responses.create(
                model="gpt-5-mini",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "너는 업로드된 PDF 파일의 내용을 바탕으로만 "
                            "성실하게 답변하는 조교야. PDF 내용과 관련 없는 질문에는 "
                            "'PDF 내용과 직접 관련된 질문을 해 주세요.'라고 답해."
                        ),
                    },
                    *[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.chatpdf_history
                    ],
                ],
                tools=[
                    {
                        "type": "file_search",
                        "vector_store_ids": [vs_id],
                        "max_num_results": 10,
                    }
                ],
                include=["file_search_call.results"],  # 선택사항: 검색 결과도 응답에 포함
            )

            answer = response.output_text
            st.markdown(answer)

    # (3) assistant 답변 저장
    st.session_state.chatpdf_history.append(
        {"role": "assistant", "content": answer}
    )
