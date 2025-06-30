from langchain.agents import tool
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputToolsParser

llm = ChatOpenAI(model="gpt-4o-mini")

# toolデコレータで関数をラップすることで、その関数をLLMのツールとして使用できるようになる
# つまり自分で定義した関数をLLmが使ってくれるってことらしい
@tool
def get_word_length(word: str) -> int:
    """returns the length of a word."""
    return len(word)

# ここでLLMに対してget_word_length関数をバインドしている
# つまり、LLMがget_word_length関数を使ってくれるようになる
llm_with_tools = llm.bind_tools([get_word_length])
chain = llm_with_tools | JsonOutputToolsParser()
res = chain.invoke("abafefavsaweafve って何文字？")
print(res)