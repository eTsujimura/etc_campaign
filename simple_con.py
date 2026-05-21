
from supabase import create_client
import streamlit as st

# 開発用のカスタムクライアント定義（SSL検証なし）
import ssl
from supabase import create_client
from httpx import Client as HttpxClient
from supabase.client import ClientOptions
import os

http_client = HttpxClient(verify=False)
options = ClientOptions(httpx_client=http_client)



url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_ANON_KEY"]
print(key)
print(url)
print("#######################")

supabase = create_client(url, key, options)

data = supabase.table("entries").select("*").execute()
print(data)

# st.write(data)
