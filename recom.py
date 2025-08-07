import streamlit as st
from openai import OpenAI
import requests
import json

# --- 페이지 기본 설정 ---
st.set_page_config(page_title='할 짓 추천 프로그램', page_icon="📝")

# --- 세션 상태 초기화 ---
if "user_location" not in st.session_state:
    st.session_state["user_location"] = "야외"
if "user_item" not in st.session_state:
    st.session_state["user_item"] = ""
if "mode" not in st.session_state:
    st.session_state["mode"] = False
if "really" not in st.session_state:
    st.session_state["really"] = False
if "user_setting" not in st.session_state:
    st.session_state["user_setting"] = ""
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_setting" not in st.session_state:
    st.session_state["last_setting"] = ""

# --- API 키 및 설정 ---
upstage_api_key = "up_MrJrannMiFutFLHHuSgG8USjDwzUg"
openai_key = "up_AlbN4eJLf4b2FqokC3EGdny85uxhZ"
upstage_url = "https://api.upstage.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {upstage_api_key}",
    "Content-Type": "application/json"
}

client = OpenAI(
    api_key=openai_key,
    base_url="https://api.upstage.ai/v1"
)

# --- 사이드바 메뉴 ---
st.sidebar.title("메뉴")
menu = st.sidebar.selectbox("", ["홈", "설정", "할 짓 추천"])

# --- 홈 메뉴 ---
if menu == "홈":
    st.header("홈 페이지")
    st.markdown("---")
    st.markdown("AI의 한마디:")

    try:
        data = {
            "model": "solar-1-mini-chat",
            "messages": [
                {"role": "user", "content": "할 짓 추천에 대한 한마디만 해줘. 사나이답게."}
            ]
        }
        response = requests.post(upstage_url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            result = response.json()
            st.success(result['choices'][0]['message']['content'])
        else:
            st.error("AI 호출 실패: 응답 코드 " + str(response.status_code))
    except Exception as e:
        st.error(f"API 요청 중 오류 발생: {e}")

    st.markdown("---")

# --- 설정 메뉴 ---
elif menu == "설정":
    st.header("설정")

    location = st.selectbox("당신의 위치는?", ["야외", "실내"], index=["야외", "실내"].index(st.session_state["user_location"]))
    item = st.text_input("가지고 있는 것", value=st.session_state["user_item"])

    mode = st.checkbox("심심이 모드 (비속어 포함)", value=st.session_state["mode"])
    really = False
    if mode:
        really = st.checkbox("진심으로 원함?", value=st.session_state["really"])
        if really:
            st.markdown("<p style='color:red;'>⚠ 조심해, 진심이라면 진짜 각오해.</p>", unsafe_allow_html=True)

    if st.button("설정 완료"):
        # 설정 저장
        st.session_state["user_location"] = location
        st.session_state["user_item"] = item
        st.session_state["mode"] = mode
        st.session_state["really"] = really

        # 설정 프롬프트 구성
        setting_text = f"사용자는 지금 {location}에 있음"
        if item:
            setting_text += f" 그리고 {item}을(를) 가지고 있음"
        if mode:
            setting_text += (
                " 싸가지 없게 말해. 인성은 바닥이고, 국밥 말아먹은 듯한 태도로. "
                "비속어 섞고, 꼽주듯이 말해. 세상에 불만 많은 찌질이처럼 말해줘."
            )

        st.session_state["user_setting"] = setting_text
        st.success("설정이 완료되었습니다!")

# --- 할 짓 추천 메뉴 ---
elif menu == "할 짓 추천":
    st.subheader("AI의 할 짓 추천")

    current_setting = st.session_state.get("user_setting", "")

    # 설정 변경 시 messages 초기화
    # 설정 변경 시 system 메시지만 업데이트 (기존 대화 유지)
    if st.session_state["last_setting"] != current_setting:
        # 기존 대화에서 system 메시지를 제외하고 저장
        old_msgs = [msg for msg in st.session_state["messages"] if msg["role"] != "system"]
        # 새 system 메시지 + 기존 대화 메시지 합치기
        st.session_state["messages"] = [
            {"role": "system", "content": f"너는 할 짓을 추천해 주는 사람이야. 추천은 2~4개 이내로. {current_setting}"}
        ] + old_msgs

        st.session_state["last_setting"] = current_setting


    # 이전 대화 출력
    for msg in st.session_state["messages"]:
        if msg["role"] == "system":
            continue  # system 메시지는 화면에 출력하지 않음
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


    # 사용자 입력
    user_input = st.chat_input("또 다른 정보가 있다면 알려주세요!")
    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})

        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            response_text = ""
            placeholder = st.empty()

            try:
                stream = client.chat.completions.create(
                    model="solar-pro2",
                    messages=st.session_state["messages"],
                    stream=True
                )

                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        response_text += chunk.choices[0].delta.content
                        placeholder.markdown(response_text)

            except Exception as e:
                response_text = "⚠ 오류 발생: " + str(e)
                st.error(response_text)

            st.session_state["messages"].append({
                "role": "assistant",
                "content": response_text
            })


