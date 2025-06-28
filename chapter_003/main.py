import tiktoken
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

MODEL_PRICES = {
    "input": {
        "gpt-4o-mini": 0.0015,
        "claude-3-5-sonnet-20240620": 0.0015,
    },
    "output": {
        "gpt-4o-mini": 0.003,
        "claude-3-5-sonnet-20240620": 0.006,
    },
}

def init_page():
    st.set_page_config(
        page_title="My Great ChatGPT",
        page_icon="😭",
    )
    st.header("My Great ChatGPT 😭")
    st.sidebar.title("Options")

def init_messages():
    clear_button = st.sidebar.button("Clear Conversation", key="clear")
    # clear_buttonが押された場合や message_historyがまだ存在しない場合に初期化
    if clear_button or "message_history" not in st.session_state:
        st.session_state.message_history = [
            ("system", "You are a helpful assistant."),
        ]

def select_model():
    # スライダーを追加し、temperatureを0から2までの範囲で選択可能にする
    # 初期値は0.0、刻み幅は0.01とする
    temperature = st.sidebar.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.01)
    
    models = ["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
    model = st.sidebar.selectbox("Choose a Model", models)
    if model == "gpt-4o-mini":
        st.session_state.model_name = "gpt-4o-mini"
        return ChatOpenAI(
            temperature=temperature,
            model=st.session_state.model_name
            )
    elif model == "claude-3-5-sonnet-20240620":
        st.session_state.model_name = "claude-3-5-sonnet-20240620"
        return ChatAnthropic(
            temperature=temperature,
            model=st.session_state.model_name
            )

def init_chain():
    st.session_state.llm = select_model()
    prompt = ChatPromptTemplate.from_messages([
        *st.session_state.message_history,
        ("user", "{user_input}") # ここであとでユーザーの入力が入る
    ])
    output_paper = StrOutputParser()
    return prompt | st.session_state.llm | output_paper

def get_message_counts(text):
    if "gpt" in st.session_state.model_name:
        encoding = tiktoken.encoding_for_model(st.session_state.model_name)
    else:
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
    return len(encoding.encode(text))

def calc_and_display_costs():
    output_count = 0
    input_count = 0
    for role, message in st.session_state.message_history:
        # tiktoken でトークン数をカウント
        token_count = get_message_counts(message)
        if role == "ai":
            output_count += token_count
        else:
            input_count += token_count
    
    # 初期状態で System Message のみが履歴に入っている場合はまだAPIコールが行われていない
    if len(st.session_state.message_history) == 1:
        return
    
    input_cost = MODEL_PRICES['input'][st.session_state.model_name] * input_count
    output_cost = MODEL_PRICES['output'][st.session_state.model_name] * output_count

    cost = output_cost + input_cost

    st.sidebar.markdown("## Costs")
    st.sidebar.markdown(f"**Total cost: ${cost: .5f}**")
    st.sidebar.markdown(f"- Input cost: ${input_cost:.5f}")
    st.sidebar.markdown(f"- Output cost: ${output_cost:.5f}")

def main():
    init_page()
    init_messages()
    chain = init_chain()

    # チャット履歴の表示 
    for role,message in st.session_state.get("message_history",[]):
        st.chat_message(role).markdown(message)
    
    # ユーザーの入力を監視
    if user_input := st.chat_input("聞きたいことを入力してね！"):
        st.chat_message("user").markdown(user_input)

        # LLMの返答を Streaming 表示する
        with st.chat_message("ai"):
            # invoke()は回答の一括取得 stream()はストリーミング(リアルタイム)表示ということらしい
            # 他にもbatch()という複数の質問を並列処理できる関数もあるらしい APIならでは
            response = st.write_stream(chain.stream({"user_input": user_input}))
            # invoke()を使って一括でレスポンスを取得
            # response = chain.invoke({"user_input": user_input})
            # st.markdown(response) 

        # チャット履歴に追加
        st.session_state.message_history.append(("user", user_input))
        st.session_state.message_history.append(("ai", response))

    # コストを計算して表示
    calc_and_display_costs()

if __name__ == "__main__":
    main()