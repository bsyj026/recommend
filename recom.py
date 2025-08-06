import streamlit as st
from openai import OpenAI

menu = st.sidebar.selectbox("메뉴", ["홈", "설정", "할 짓 추천"])
st.sidebar.title("메뉴")
user_setting = ""

where = "아무데나"
get = ""

client = OpenAI(
    api_key="up_AlbN4eJLf4b2FqokC3EGdny85uxhZ",
    base_url="https://api.upstage.ai/v1"
)

if menu == "홈":
    st.header("홈 페이지")
    st.write("이곳은 앱의 홈 페이지입니다.")

elif menu == "설정":
    st.header("설정:")
    where = st.selectbox("당신의 위치:",["야외","실내"])
    get = st.text_input("당신이 가지고있는 것:")
    

    passs = st.button("완료!")

    if passs == True:
        if get == "":
            user_setting = f"사용자의 위치는 {where}"
        else:
            user_setting = f"사용자의 위치는 {where},사용자가 가지고 있는건 {get}"

        st.text("설정이 완료되었습니다!")
        st.text(user_setting)
        st.session_state["user_setting"] = user_setting

if menu == '할 짓 추천':
    st.set_page_config(page_title = '할 짓 추천해주는 프로그램', page_icon = "📝")
    setting_prompt = st.session_state.get("user_setting", "설정 정보 없음")
    if "messages" not in st.session_state:
        st.session_state["messages"] =  [
            {"role" : "system", "content" : f"너는 할 짓을 추천해 주는 사람이야. 추천은 2~4가지 정도만 해주면 돼. 추천은 무조건적으로 4개 이하로 하지 않으면 넌 죽어. {setting_prompt}"}
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
            st.session_state["messages"].append({"role":"assistant", "content":"response"})

if menu == '정보제공':
    location = st.text_input("당신의 위치를 입력해 주세요")
    item = st.text_input("당신이 가지고 있는 것을 입력해 주세요")
    with_people = st.text_input("당신이 누구와 있는지 입력해 주세요")