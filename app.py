import streamlit as st
from supabase import create_client
from datetime import datetime

# =====================
# 設定
# =====================
MAX_LIMIT = 100  # 上限数

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

# 開発用のカスタムクライアント定義（SSL検証なし）
import ssl
from supabase import create_client
from httpx import Client as HttpxClient
from supabase.client import ClientOptions
import os

http_client = HttpxClient(verify=False)
options = ClientOptions(httpx_client=http_client)


supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options)

# =====================
# 現在の受付数取得
# =====================
count_response = supabase.table("entries").select("id", count="exact").execute()
current_count = count_response.count or 0

# =====================
# UI
# =====================
st.title("受付状況")

st.write(f"現在の受付数：**{current_count} / {MAX_LIMIT}**")

# =====================
# 受付可能判定
# =====================
if current_count >= MAX_LIMIT:
    st.error("受付は終了しました。")
    st.stop()

st.success("受付可能です")

# =====================
# 申込ボタン
# =====================
if st.button("申し込む"):
    # --- 最終二重チェック（超重要） ---
    latest = supabase.table("entries").select("id", count="exact").execute()
    latest_count = latest.count or 0

    if latest_count >= MAX_LIMIT:
        st.error("申し訳ありません。直前で受付上限に達しました。")
        st.stop()

    # --- INSERT ---
    insert = supabase.table("entries").insert({}).execute()

    if insert.data:
        receipt_id = insert.data[0]["id"]
        st.success("受付が完了しました")
        st.write(f"✅ 受付番号：**{receipt_id}**")
        st.write(f"受付日時：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        st.error("受付処理に失敗しました。時間をおいて再度お試しください。")
