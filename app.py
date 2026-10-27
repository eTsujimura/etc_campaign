import streamlit as st
from supabase import create_client
from datetime import datetime
import pandas as pd

# =====================
# 設定
# =====================
MAX_LIMIT = int(st.secrets["LIMIT_CNT"])  # 上限数

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_ANON_KEY"]

# （SSL検証なし）
import ssl
from httpx import Client as HttpxClient
from supabase.client import ClientOptions
import os

http_client = HttpxClient(verify=False)
options = ClientOptions(httpx_client=http_client)


supabase = create_client(SUPABASE_URL, SUPABASE_KEY, options)

# =====================
# Get current count
# =====================
count_response = supabase.table("entries").select("id", count="exact").execute()
current_count = count_response.count or 0

# =====================
# Display
# =====================
st.title("ETCキャンペーン受付状況")
st.warning("対象モデルはScrambler 400X/400XC, SPEED 400, Thruxton 400及びTracker 400です。")


cnt = f"**{current_count} / {MAX_LIMIT}**"
st.metric(label="現在の受付数", value=cnt,)

# =====================
# Input
# =====================
name = st.text_input("ディーラー名(登録済一覧には表示されません)")
vin = st.text_input("VIN(下6桁)")
# st.warning("VIN以外も入力可能ですが、公開URLですのでお客様の名前などは入力しないでください")


# =====================
# 受付可能判定
# =====================
if current_count >= MAX_LIMIT:
    st.error("受付は終了しました。")
    st.stop()

# st.success("受付可能です")

# =====================
# 申込ボタン
# =====================
if st.button("申し込む"):
    
    if not name or not vin:
        st.warning("ディーラー名とVINを入力してください")
        st.stop()

    # --- Double check before execution ---
    latest = supabase.table("entries").select("id", count="exact").execute()
    latest_count = latest.count or 0

    if latest_count >= MAX_LIMIT:
        st.error("申し訳ありません。直前で受付上限に達しました。")
        st.stop()

    # --- INSERT ---

    try:
        # --- INSERT ---
        insert = supabase.table("entries").insert({
            "dlr_name": name,
            "vin": vin,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        if insert.data:
            receipt_id = insert.data[0]["id"]
            st.success("受付が完了しました")
            st.write(f"✅ 受付番号：**{receipt_id}**")
            st.write(f"VIN：{vin}")
            st.write(f"受付日時：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            st.write("専用フォームに受付番号を記載して発注して下さい。")
            st.write("登録の確認はこのページの下記「登録内容一覧」をご確認ください。")
            st.write("誤り・問題等ございましたらTMJまでご連絡ください。")
        else:
            st.error("受付処理に失敗しました")

    except Exception as e:
        st.error(f"エラー: {e}")


# =====================
# 一覧表示
# =====================
st.subheader("登録済み一覧")


list_data = supabase.table("entries").select("id, vin").order("id").execute()

if list_data.data:
    df = pd.DataFrame(list_data.data)
    df = df.rename(columns={
        "id": "受付番号",
        "vin": "VIN"
    })

    st.dataframe(df, height=300)
else:
    st.write("まだ登録がありません")





