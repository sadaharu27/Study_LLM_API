import base64
import streamlit as st
from langchain_openai import ChatOpenAI
import openai
import os

GPT4V_PROMPT = """
まず、以下のユーザーのリクエストとアップロードされた画像を注意深く読んでください。

次に、アップロードされた画像に基づいて画像を生成するというユーザーのリクエストに
沿ったDALL-Eプロンプトを作成してください。

ユーザー入力: {user_input}

プロンプトでは、ユーザーがアップロードした写真に何が描かれているか、どのように構成されているかを詳細に説明してください
写真に何が写っているのかはっきり見える場合は、示されている場所や人物の名前を正確に書き留めてください
写真の構図とズームの程度を可能な限り詳しく説明してください。
写真の内容を可能な限り正確に再現することが重要です。

DALL-E 3向けのプロンプトを英語で回答してください:
"""

def init_page():
    st.set_page_config(
        page_title="Image Converter",
        page_icon="😊"
    )
    st.header("Image Converter😊")

def main():
    init_page()

    llm = ChatOpenAI(
        temperature=0,
        model="gpt-4o",
        # 何故かmax_tokensを指定しないとエラーが出る
        max_tokens=512
    )
    
    # OpenAIクライアントを直接初期化
    openai_client = openai.OpenAI()

    dalle3_image_url = None
    uploaded_file = st.file_uploader(
        label="ここに画像をアップロードしてください",
        # GPT-4Vが処理可能な画像ファイルのみを許可する
        type=["png", "jpg", "webp", "gif"],
    )
    if uploaded_file:
        if user_input := st.chat_input("画像をどのように加工したいか教えてください"):
            # 読み取ったファイルをBase64エンコード
            image_base64 = base64.b64encode(uploaded_file.read()).decode()
            image = f"data:image/jpeg;base64,{image_base64}"

            query = [
                (
                    "user",
                    [
                        {
                            "type": "text",
                            "text": GPT4V_PROMPT.format(user_input=user_input)
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image,
                                "detail": "auto"
                            },
                        }
                    ]
                )
            ]

            # GPT-4Vに DALL-E 3 用の画像生成プロンプトを書いてもらう
            st.markdown("### Image Prompt")
            image_prompt = st.write_stream(llm.stream(query))

            # DALL-E 3 による画像生成（OpenAI APIを直接使用）
            with st.spinner("DALL-E 3 による画像生成中..."):
                try:
                    response = openai_client.images.generate(
                        model="dall-e-3",
                        prompt=image_prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    dalle3_image_url = response.data[0].url
                except Exception as e:
                    st.error(f"画像生成中にエラーが発生しました: {str(e)}")
                    st.error("OPENAI_API_KEYが正しく設定されているか確認してください")
    else:
        st.write("まずは画像をアップロードしてください")

    # DALL-E 3 の画像の表示
    if dalle3_image_url:
        st.markdown("### Question")
        st.write(user_input)
        st.image(
            uploaded_file,
            use_column_width="auto"
        )

        st.markdown("### DALL-E 3 Generated Image")
        st.image(
            dalle3_image_url,
            caption=image_prompt,
            use_column_width="auto"
        )

if __name__ == "__main__":
    main()