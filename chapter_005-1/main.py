import traceback
import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

SUMMARISE_PROMPT = """以下のコンテンツについて、内容を300文字程度でわかりやすく要約してください


======

{content}

======

日本語で書いてください
"""

def init_page():
    st.set_page_config(
        page_title="Website Summarizer",
        page_icon="😊"
    )
    st.header("Website Summarizer 😭")
    st.sidebar.title("Options")

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
    llm = select_model()
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUMMARISE_PROMPT),
    ])
    output_parser = StrOutputParser()
    chain = prompt | llm | output_parser
    return chain

def validate_url(url):
    """ URLが有効かどうかを判定する関数 """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_content(url):
    try:
        with st.spinner("Fetching Website..."):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            # なるべく本文の可能性が高い要素を取得する
            if soup.main:
                return soup.main.get_text()
            elif soup.article:
                return soup.article.get_text()
            else:
                return soup.body.get_text()
    except:
        st.write(traceback.format_exc()) # エラーが発生した場合はエラー内容を表示
        return None
    
def main():
    init_page()
    chain = init_chain()

    # ユーザーの入力を監視
    # 代入と比較を同時に行っている(nullチェックしてる)
    if url := st.text_input("URL : ", key="input"):
        is_valid_url = validate_url(url)

        if not is_valid_url:
            st.write('Please input valid url')
        else:
            if content := get_content(url):
                st.markdown("## Summary")
                st.write_stream(chain.stream({"content": content}))
                st.markdown("---")
                st.markdown("## Original Text")
                st.write(content)
    
    # コストを表示する場合は第3章と同じ実装を追加してください(今回は実装なし)
    # calc_and_display_cost()

if __name__ == "__main__":
    main()