import traceback
import streamlit as st
from urllib.parse import urlparse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# models
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic


from langchain_community.document_loaders import YoutubeLoader

SUMMARISE_PROMPT = """以下のコンテンツについて、内容を300文字程度でわかりやすく要約してください


======

{content}

======

日本語で書いてください
"""

def init_page():
    st.set_page_config(
        page_title="Youtube Summarizer",
        page_icon="😭"
    )
    st.header("Youtube Summarizer 😭😭😭")
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
    """
    Document:
        - page_content: str
        - metadata: dict
        
            - source: str
            - title: str
            - description: Optional[str]
            - view_count: int
            - thumbnail_url: Optional[str]
            - publish_date: str
            - length: int
            - author: str
    """
    # Youtubeの場合は、字幕(transcript)を取得して要約に利用する
    with st.spinner("Fetching Content..."):
        try:
            # まずは日本語字幕を試す
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False, # pytubeのエラーを回避するためFalseに設定
                language=["ja"], # 日本語字幕を優先
            )
            res = loader.load()
            
            if res and res[0].page_content.strip():
                content = res[0].page_content
                title = res[0].metadata.get("title", "YouTube Video")
                st.success("日本語字幕を取得しました")
                return f"title: {title}\n\n{content}"
                
        except Exception as e:
            st.warning(f"日本語字幕の取得に失敗: {str(e)}")
            
        try:
            # 日本語字幕が取得できない場合は英語字幕を試す
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                language=["en"], # 英語字幕
            )
            res = loader.load()
            
            if res and res[0].page_content.strip():
                content = res[0].page_content
                title = res[0].metadata.get("title", "YouTube Video")
                st.success("英語字幕を取得しました")
                return f"title: {title}\n\n{content}"
                
        except Exception as e:
            st.warning(f"英語字幕の取得に失敗: {str(e)}")
            
        try:
            # 両方とも失敗した場合は、すべての利用可能な字幕を試す
            loader = YoutubeLoader.from_youtube_url(
                url,
                add_video_info=False,
                language=None, # すべての利用可能な字幕
            )
            res = loader.load()
            
            if res and res[0].page_content.strip():
                content = res[0].page_content
                title = res[0].metadata.get("title", "YouTube Video")
                st.info("利用可能な字幕を取得しました")
                return f"title: {title}\n\n{content}"
                
        except Exception as e:
            st.error(f"字幕の取得に完全に失敗しました: {str(e)}")
            st.error("この動画には字幕が存在しないか、アクセスできません")
            
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