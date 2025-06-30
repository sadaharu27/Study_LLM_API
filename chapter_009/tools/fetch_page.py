import requests
import html2text
from readability import Document
from langchain_core.tools import tool
from langchain_core.pydantic_v1 import (BaseModel, Field)
from langchain_text_splitters import RecursiveCharacterTextSplitter


class FetchPageInput(BaseModel):
    url: str = Field(description="取得したいWebページのURL")
    page_num: int = Field(default=0, description="ページ番号（0から始まる、負の数は無効）")

# 関数といっても追加プロンプトに近い？
@tool(args_schema=FetchPageInput)
def fetch_page(url, page_num=0, timeout_sec=10):
    """
    指定されたURL(とページ番号から)ウェブページのコンテンツを取得するツール。

    `status` と `page_content` (`title`, `content`, `has_next` インジケーター) を返します。
    statusが200でない場合は、ページの取得時にエラーが発生しています。 (他のページの取得を試みてください)

    デフォルトでは、最大2,000トークンのコンテンツのみが取得されます。
    ページにさらにコンテンツがある場合、 `has_next` の値はTrueになります。
    続きを読むには、同じURLで`page_num`パラメータをインクリメントして、再度入力してください。
    ( ページングは0から始まるので、次のページは1です)

    1ページが長すぎる場合は、**3回以上取得しないでください**(メモリの負荷がかかるため)

    Returns
    -------
    Dict[str, Any]:
    - status: str
    - page_content
        - title: str
        - content: str
        - has_next: bool
    """
    # page_numが負の数の場合のバリデーション
    if page_num < 0:
        return {
            "status": 400,
            "page_content": {'error_message': 'page_num must be 0 or greater. Please provide a valid page number.'}
        }
    
    try:
        response = requests.get(url, timeout=timeout_sec)
        response.encoding = "utf-8"
    except requests.exceptions.Timeout:
        return {
            "status": 500,
            "page_content": {'error_message': 'Could not download page due to Timeout Error. Please try to fetch other pages.'}
        }
    
    if response.status_code != 200:
        return {
            "status": response.status_code,
            "page_content": {'error_message': 'Could not download page. Please try to fetch other pages.'}
        }
    
    try:
        doc = Document(response.text)
        title = doc.title()
        html_content = doc.summary()
        content = html2text.html2text(html_content)
    except Exception as e:
        return {
            "status": 500,
            "page_content": {'error_message': 'Could not parse page content. Please try to fetch other pages.'}
        }
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4o-mini",
        chunk_size=1000,
        chunk_overlap=0,
    )
    chunks = text_splitter.split_text(content)
    if page_num >= len(chunks):
        return {
            "status": 500,
            "page_content": { 'error_message': 'page_num parameter looks invalid Please try to fetch other pages.'}
        }
    elif page_num >= 3:
        return {
            "status": 503,
            "page_content": { 'error_message': 'Reading more of this page_num`s content will overload your memory. Please provide your response based on the information you currently have.'}
        }
    else:
        return {
            "status": 200,
            "page_content": {
                "title": title,
                "content": chunks[page_num],
                "has_next": page_num < len(chunks) - 1
            }
        }