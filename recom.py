import streamlit as st
from openai import OpenAI
import requests
import json

st.set_page_config(page_title='할 짓 추천해주는 프로그램', page_icon="📝")

# --- 초기 세션 상태 설정 ---
if "user_location" not in st.session_state:
    st.session_state["user_location"] = '야외'
if "user_item" not in st.session_state:
    st.session_state["user_item"] = ''
if "mode" not in st.session_state:
    st.session_state["mode"] = False
if "really" not in st.session_state:
    st.session_state["really"] = False
if "user_setting" not in st.session_state:
    st.session_state["user_setting"] = ''
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "last_setting" not in st.session_state:
    st.session_state["last_setting"] = ""

# --- API 키 및 URL 설정 ---
upstage_api_key = "up_MrJrannMiFutFLHHuSgG8USjDwzUg"
url = "https://api.upstage.ai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {upstage_api_key}",
    "Content-Type": "application/json"
}

client = OpenAI(
    api_key="up_AlbN4eJLf4b2FqokC3EGdny85uxhZ",
    base_url="https://api.upstage.ai/v1"
)

# --- 사이드바 메뉴 ---
st.sidebar.title("메뉴")
menu = st.sidebar.selectbox("", ["홈", "설정", "할 짓 추천"])

# --- 홈 메뉴 ---
if menu == "홈":
    st.header("홈 페이지")
    st.markdown('---')
    st.markdown("ai의 한마디")

    data = {
        "model": "solar-1-mini-chat",
        "messages": [
            {"role": "user", "content": "할 짓 추천에 대한 사실에 한마디만 해줘 사나이같이!"}
        ]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()
        st.markdown(f"**{result['choices'][0]['message']['content']}**")
    else:
        st.error(f"Error: {response.status_code}, {response.text}")

    st.markdown('---')

# --- 설정 메뉴 ---
elif menu == "설정":
    st.header("설정:")

    options = ['야외', '실내']

    # 기본값 지정해서 이전에 설정한 값 유지
    where = st.selectbox(
        "당신의 위치",
        options,
        index=options.index(st.session_state.get("user_location", "야외")),
        key="user_location"
    )

    user_get = st.text_input(
        "당신이 가지고있는 것",
        value=st.session_state.get("user_item", ""),
        key="user_item"
    )

    mode = st.checkbox(
        "심심이 모드(심약자 및 변태를 제외한 모든 욕을 먹기 싫어하는 일반인에게 추천되지 않는다.)",
        value=st.session_state.get("mode", False),
        key="mode"
    )

    if mode:
        really = st.checkbox(
            "진심으로?",
            value=st.session_state.get("really", False),
            key="really"
        )
        if really:
            st.markdown(
                "<p style='color:red; font-weight:bold;'>⚠ 진심이면 진짜 조심해라.</p>",
                unsafe_allow_html=True
            )

    passs = st.button("완료")

    if passs:
        # 세션 상태에 저장
        st.session_state["user_location"] = where
        st.session_state["user_item"] = user_get
        st.session_state["mode"] = mode
        st.session_state["really"] = st.session_state.get("really", False)

        # 설정 텍스트 생성
        user_setting = f'사용자는 지금 {where}에 있음'
        if user_get != '':
            user_setting = f'사용자는 지금 {where}에 있고 {user_get}을 가지고 있음'

        if mode:
            user_setting += (
                ' 싸가지 없게 말해. 무조건 싸가지 없게. 인성을 국밥 말아먹은 듯이. '
                '세상에서 제일 개쓰레기처럼. 비꼬는 듯이. 세상 만사에 불만이 있는 씨발년처럼. 비속어를 섞어서'
            )

        st.session_state["user_setting"] = user_setting
        st.success("설정이 완료되었습니다!")

# --- 할 짓 추천 메뉴 ---
elif menu == "할 짓 추천":
    st.markdown("<h1 style='font-size:30px;'>ai의 할 짓 추천</h1>", unsafe_allow_html=True)

    setting_prompt = st.session_state.get("user_setting", "설정 정보 없음")

    # 설정이 바뀌었으면 messages 초기화
    if (not st.session_state["messages"]) or (st.session_state.get("last_setting") != setting_prompt):
        st.session_state["messages"] = [
            {"role": "system", "content": f"너는 할 짓을 추천해 주는 사람이야. 추천은 2~4가지 정도만 해주면 돼. 추천은 무조건적으로 4개 이하로. {setting_prompt}"}
        ]
        st.session_state["last_setting"] = setting_prompt

    # 대화 메시지 출력
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    # 유저 입력 받기
    if prompt := st.chat_input("또 다른 정보가 있다면 알려주세요!"):
        st.session_state["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = ""
            stream = client.chat.completions.create(
                model="solar-pro2",
                messages=st.session_state["messages"],
                stream=True,
            )

            msg_placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
                    msg_placeholder.markdown(response)

            st.session_state["messages"].append({"role": "assistant", "content": response})
