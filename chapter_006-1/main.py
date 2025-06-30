import base64
import streamlit as st
from langchain_openai import ChatOpenAI

def init_page():
    st.set_page_config(
        page_title="Image Recognizer",
        page_icon=":camera:",
    )
    st.header("Image Recognizer😭")
    st.sidebar.title("Options")

def main():
    init_page()

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        # 何故かmax_tokensを指定しないとエラーが出る
        # 著しく短い回答になったり、途中で回答が途切れたりする
        max_tokens=512
    )

    uploaded_file = st.file_uploader(
        label="Upload your image here",
        # GPT-4Vが処理可能な画像ファイルのみを許可する
        type=["png", "jpg", "webp", "gif"],
    )
    if uploaded_file:
        if user_print := st.chat_input("聞きたいことを入力してください"):
            # 読み取ったファイルをBase64エンコード
            image_base64 = base64.b64encode(uploaded_file.read()).decode()
            image = f"data:image/png;base64,{image_base64}"

            query = [
                (
                    "user",
                    [
                        {
                            "type": "text",
                            "text": user_print
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
            st.markdown("### Question")
            st.write(user_print) # ユーザーの質問
            st.image(uploaded_file) # アップロードした画像を表示
            st.markdown("### Answer")
            st.write_stream(llm.stream(query))

    else:
        st.write("まずは画像をアップロードしてください")

if __name__ == "__main__":
    main()