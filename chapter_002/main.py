import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def main():
    st.set_page_config(
        page_title="My Great ChatGPT",
        page_icon="😭",
    )
    st.header("My Great ChatGPT 😭")

    # チャットの履歴の初期化 : message_historyがなければ作成
    if "message_history" not in st.session_state:
        st.session_state.message_history = [
            # Syte Prompt を設定 ('system' はSystem Pronmptを意味する )
            ("system", "You are a helpful assistant."),
        ]
    

    # user_inputの初期値
    user_input = "こんにちは！"

    # ChatGPTに質問を与えて回答を取り出す(パースする)処理を作成
    # モデルの呼び出しを設定(temperature=0は、返答のランダム性を低くするためのパラメータ)
    # novelaiにおける強調のようなイメージ？
    llm = ChatOpenAI(temperature=0)

    # ユーザーの質問を受け取り、ChatGPTに渡すためのテンプレートを作成
    # テンプレートには過去のチャット履歴を含めるように設定
    prompt = ChatPromptTemplate.from_messages([
        *st.session_state.message_history,
        ("system", "絶対に関西弁で返答してください"),
        ("user", "{user_input}"), # ここにあとでユーザーの入力が入る
    ])

    # ChatGPTの返答をパースするための処理を呼出し
    output_parser = StrOutputParser()

    # ユーザーの質問をChatGPTに渡し、返答を取り出す連続的な処理(chain)を作成
    # 各要素をパイプでつなげて連続的な処理を作成するのがLCELの特徴
    chain = prompt | llm | output_parser

    # ユーザーの入力を監視
    if user_input := st.chat_input("聞きたいことを入力してね！"):
        with st.spinner("ChatGPTに聞いています..."):
            response = chain.invoke({"user_input": user_input})

        # ユーザーの質問を履歴に追加 
        st.session_state.message_history.append(("user", user_input))

        # ChatGPTの回答を履歴に追加 ('assistant' はChatGPTの回答を意味する)
        st.session_state.message_history.append(("assistant", response))
    
    # チャット履歴の表示
    for role, message in st.session_state.get("message_history", []):
        with st.chat_message(role):
            st.markdown(message)

if __name__ == "__main__":
    main()