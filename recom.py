import streamlit as st
from openai import OpenAI
import requests
import json

st.sidebar.title("메뉴")
menu = st.sidebar.selectbox("", ["홈", "설정", "할 짓 추천"])
user_setting = ""


where = "아무데나"
get = ""

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
        print(f"Error: {response.status_code}, {response.text}")
    st.markdown('---')


elif menu == "설정":
    st.header("설정:")
    where = st.selectbox("당신의 위치:",["야외","실내"])
    get = st.text_input("당신이 가지고있는 것:")
    
    mode = st.checkbox("심심이 모드(심약자 및 변태를 제외한 모든 일반인에게 추천되지 않는다.)")
    if mode == True:
        st.markdown("<span style='color:red;'>진심으로?</span>", unsafe_allow_html=True)
        
    passs = st.button("완료")

    if passs == True:
        if get == "":
            user_setting = f"사용자의 위치는 {where}"
        else:
            user_setting = f"사용자의 위치는 {where}이고, 사용자가 가지고 있는건 {get}이다."
    

        st.text("설정이 완료되었습니다!")
        st.text(user_setting)
        
        if mode == True:
            user_setting += '싸가지 없게 말해. 무조건 싸가지 없게. 인성을 국밥 말아먹은 듯이. 세상에서 제일 개쓰레기처럼. 비꼬는 듯이. 세상 만사에 불만이 있는 씨발년처럼. 비속어를 섞어서'
            st.session_state["user_setting"] = user_setting

if menu == '할 짓 추천':
    st.set_page_config(page_title = '할 짓 추천해주는 프로그램', page_icon = "📝")
    setting_prompt = st.session_state.get("user_setting", "설정 정보 없음")
    
    if "messages" not in st.session_state:
        st.session_state["messages"] =  [
            {"role" : "system", "content" : f"너는 할 짓을 추천해 주는 사람이야. 추천은 2~4가지 정도만 해주면 돼. 추천은 무조건적으로 4개 이하로. {setting_prompt}"}
        ]

    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(msg["content"])

    if prompt := st.chat_input("또 다른 정보가 있다면 알려주세요!"):
        st.session_state["messages"].append({"role":"user", "content":prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = ""
            stream = client.chat.completions.create(
                model = "solar-pro2",
                messages = st.session_state["messages"],
                stream = True,
            )

            msg_placeholder = st.empty()
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    response += chunk.choices[0].delta.content
                    msg_placeholder.markdown(response)
            st.session_state["messages"].append({"role":"assistant", "content":response})




























