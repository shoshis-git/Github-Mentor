# from netfree_unstrict_ssl import unstrict_ssl
# unstrict_ssl()
import httpx
import ssl
import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from tools import list_prs,resolve_github_url
from print_messages import print_messages

# --- מעקף SSL אגרסיבי עבור httpx בנטפרי ---
_original_client_init = httpx.Client.__init__
_original_async_client_init = httpx.AsyncClient.__init__

def _patched_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _original_client_init(self, *args, **kwargs)

def _patched_async_client_init(self, *args, **kwargs):
    kwargs['verify'] = False
    _original_async_client_init(self, *args, **kwargs)

httpx.Client.__init__ = _patched_client_init
httpx.AsyncClient.__init__ = _patched_async_client_init
# -----------------------------------------------
load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

agent = create_agent(model, tools=[list_prs,resolve_github_url])

result = agent.invoke({"messages": [{"role": "user", "content": "what is the title of the newest PR in this repo https://github.com/LibreChat-AI/LibreChat?"}]})

print_messages(result["messages"])


