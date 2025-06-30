import streamlit as st
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

def init_page():
    st.set_page_config(
        page_title="Ask My PDF(s)",
        page_icon="🧐"
    )
    st.sidebar.title("Options")

def select_model():
    # スライダーを追加し、temperatureを0から2までの範囲で選択可能にする
    # 初期値は0.0、刻み幅は0.01とする
    temperature = st.sidebar.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.01)
    
    models = ["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
    model = st.sidebar.radio("Choose a Model", models)
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
    
def init_qa_chain():
    llm = select_model()
    prompt = ChatPromptTemplate.from_template("""
    以下の前提知識を用いて、ユーザーからの質問に答えてください
    
    ===
    {context}
    ===

    ユーザーの質問
    {question}
    """)
    retriever = st.session_state.vectorstore.as_retriever(
        # "mmr" , "similarity_score_threshold" を指定することもできる
        search_type="similarity",

        # 文書を何個取得するか (default: 4)
        search_kwargs={"k":10}
    )
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain

def page_ask_my_pdfs():
    chain = init_qa_chain()

    if query := st.text_input("PDFへの質問を書いてね: ", key="input"):
        st.markdown("## Answer")
        st.write_stream(chain.stream(query))

def main():
    init_page()
    st.title("PDF QA")
    if "vectorstore" not in st.session_state:
        st.warning("まずはPDFをアップロードしてください")
    else:
        page_ask_my_pdfs()

if __name__ == "__main__":
    main()