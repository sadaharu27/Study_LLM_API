import streamlit as st

def init_page():
    st.set_page_config(
        page_title="Ask My PDF(s)",
        page_icon="🥲"
    )

def main():
    init_page()

    # ページ遷移の指定がないが、streamlitは自動的にディレクトリのpyファイルを検出してページ遷移をしてくれるらしい
    # なんて便利
    st.sidebar.success("上のメニューから選んでください")

    st.markdown(
        """
        # Ask My PDF(s) にようこそ

        - このアプリでは、アップロードしたPDFに対して質問をすることができます。
        - まずは左のメニューから `Upload PDF(s)` を選択してPDFをアップロードしてください。
        - PDFをアップロードしたら `PDF QA` を選択して質問をしてみてください


        """
        )

if __name__ == "__main__":
    main()