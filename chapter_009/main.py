import streamlit as st
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langchain_community.callbacks import StreamlitCallbackHandler

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# custom tools
from tools.search_ddg import search_ddg
from tools.fetch_page import fetch_page

CUSTOM_PROMPT = """

あなたは、ユーザーのリクエストに基づいてインターネットで調べ物を行うアシスタントです。
利用可能なツールを私用して、調査した情報を説明してください。
既に知っていることだけに基づいて答えないでください。
回答する前にできる限り検索を行ってください。
(ユーザーが読むページを指定するなど、特別な場合は、検索する必要はありません)

検索ページを見ただけでは情報があまりないと思われる場合は、次の2つのオプションを検討して試してみてください。

- 検索結果のリンクをクリックして、各ページのコンテンツにアクセスし、読んでみてください。
- 1ページが長すぎる場合は、3回以上ページ送りしないでください( メモリの負荷がかかるため )
- 検索クエリを変更して、新しい検索を実行してください。
- 検索する内容に応じて検索に利用する言語を適切に変更してください。
    - 例えば、プログラミング関連の質問については英語で検索するのがいいでしょう。

ユーザーは非常に忙しく、あなたほど自由ではありません。
そのため、ユーザーの労力を節約するために、直接的な回答を提供してください。

=== 悪い回答の例 ===
- これらのページを参照してください。
- これらのページを参照してコードを書くことができます。
- 次のページが役に立つでしょう

=== 良い回答の例 ===
- これはサンプルコードです。 --- サンプルコードをここに ---
- あなたの質問の答えは --- 回答をここに ---

回答の最後には、参照したページのURLを **必ず** 記載してください。(これにより、ユーザーは回答を検証することができます )

ユーザーが使用している言語で回答するようにしてください。
ユーザーが日本語で質問した場合は、日本語で回答してください。
ユーザーがスペイン語で質問した場合は、スペイン語で回答してください。

"""

def init_page():
    st.set_page_config(
        page_title="Web検索エージェント",
        page_icon="😤"
    )
    st.header("Web検索エージェント 😤") 
    st.sidebar.title("オプション")


def init_messages():
    clear_button = st.sidebar.button("会話をクリア", key="clear")

    if clear_button or "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "こんにちは！なんでも質問をどうぞ！"}
        ]
        st.session_state['memory'] = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )

def select_model():
    # スライダーを追加し、temperatureを0から2までの範囲で選択可能にする
    # 初期値は0.0、刻み幅は0.01とする
    temperature = st.sidebar.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.01)
    
    models = ["gpt-4o-mini", "claude-3-5-sonnet-20240620"]
    model = st.sidebar.selectbox("AIモデルを選択", models)
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
    
def create_agent():
    tools = [search_ddg, fetch_page]
    prompt = ChatPromptTemplate.from_messages([
        ("system", CUSTOM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    llm = select_model()
    agent = create_tool_calling_agent(llm,tools,prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=st.session_state['memory']
    )

def main():
    init_page()
    init_messages()
    web_browsing_agent = create_agent()

    for msg in st.session_state['memory'].chat_memory.messages:
        st.chat_message(msg.type).write(msg.content)

    if prompt := st.chat_input(placeholder="2023 FIFA 女子ワールドカップの優勝国は？"):
        st.chat_message("user").write(prompt)
        with st.chat_message("assistant"):
            # コールバック関数の設定 (エージェントの動作の可視化用)
            st_cb = StreamlitCallbackHandler(
                st.container(), expand_new_thoughts=True)

            # エージェントの実行
            response = web_browsing_agent.invoke(
                {"input": prompt},
                config=RunnableConfig({'callbacks': [st_cb]})
            )
            st.write(response['output'])

if __name__ == "__main__":
    main()