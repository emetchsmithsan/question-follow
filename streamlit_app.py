import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. 設定・スプレッドシート接続
# ==========================================
URL_BASE = "https://www." + "googleapis.com" + "/auth/"
FINAL_SCOPE = [URL_BASE + "spreadsheets", URL_BASE + "drive"]

def init_sheets():
    try:
        creds_dict = dict(st.secrets["gspread_service_account"])
        CREDS = Credentials.from_service_account_info(creds_dict, scopes=FINAL_SCOPE)
        client = gspread.authorize(CREDS)
    except Exception as e:
        st.error(f"【エラー場所：Googleログイン段階】\n詳細: {e}")
        st.stop()

    INPUT_FILE_ID = '17r20Mrovxy1hLx1taLhHsRZzGKvUf_oZEvI1Z-Vnix0'.strip() 
    OUTPUT_FILE_ID = '1a0v3VCqkpXRtq6gMMfIoQIkUxckxa5Y-wJ0kKcYo3m4'.strip()

    try:
        input_ss = client.open_by_key(INPUT_FILE_ID)
        console_sheet = input_ss.worksheet("コンソール")
        data_sheet = input_ss.worksheet("問題データ")
        output_ss = client.open_by_key(OUTPUT_FILE_ID)
        output_sheet = output_ss.worksheet("問題フォロー出力先")
    except Exception as e:
        st.error(f"【エラー場所：スプレッドシートを開く段階】\n詳細: {e}")
        st.stop()

    return {"console": console_sheet, "data": data_sheet, "output": output_sheet}

sheets = init_sheets()

# ==========================================
# 2. アプリの初期状態（セッション）管理
# ==========================================
if "current_line" not in st.session_state:
    try:
        val_f1 = sheets["console"].acell("F1").value
        st.session_state.current_line = int(val_f1) if val_f1 else 1
    except:
        st.session_state.current_line = 1

# ==========================================
# 3. コアロジック（GASのmoveLine相当）
# ==========================================
def move_line(direction):
    new_line = st.session_state.current_line + direction
    if new_line < 1:
        new_line = 1
        
    st.session_state.current_line = new_line
    
    # 1. 操作コンソールシートのF1セルを更新
    sheets["console"].update_acell("F1", new_line)
    
    # 2. 問題データから2行×3列を取得 (A列~C列)
    range_str = f"A{new_line}:C{new_line + 1}"
    data_matrix = sheets["data"].get(range_str)
    
    # データ数が足りない場合の安全対策
    while len(data_matrix) < 2:
        data_matrix.append(["", "", ""])
    for i in range(2):
        while len(data_matrix[i]) < 3:
            data_matrix[i].append("")

    # 【バグ対策修正：安全なデータ分解抽出】
    # 1行目と2行目を安全に分離
    first_row = data_matrix.pop(0)
    second_row = data_matrix.pop(0)
    
    # 各セルから文字データを確実に1つずつ取り出します
    val_a1 = first_row.pop(0)   # 現在の行のA列
    val_b1 = first_row.pop(0)   # 現在の行のB列
    val_c1 = first_row.pop(0)   # 現在の行のC列
    val_a2 = second_row.pop(0)  # 次の行のA列
    
    # 3. 自分のコンソールシートのA1:C1に一括書き込み
    sheets["console"].update(range_name="A1:C1", values=[[val_a1, val_b1, val_c1]])
    
    # 4. 別ファイル（問題フォロー出力先）に一括書き込み
    body = {
        'valueInputOption': 'USER_ENTERED',
        'data': [
            {'range': 'B1', 'values': [[val_a1]]},
            {'range': 'A2', 'values': [[val_b1]]},
            {'range': 'A3', 'values': [[val_c1]]},
            {'range': 'B4', 'values': [[val_a2]]}
        ]
    }
    sheets["output"].spreadsheet.batch_update(body)

# ==========================================
# 4. 画面レイアウト（UI）の構築
# ==========================================
st.title("問題フォロー 操作コンソール")
st.metric(label="現在の行（問題番号など）", value=st.session_state.current_line)

col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ 前の問題へ", use_container_width=True):
        move_line(-1)
        st.rerun()
with col2:
    if st.button("次の問題へ ➡️", use_container_width=True):
        move_line(1)
        st.rerun()

st.subheader("書き込みデータ確認")
try:
    current_display = sheets["console"].get("A1:C1")
    if current_display and len(current_display) > 0:
        display_row = current_display[0]
        st.write(f"**A1 (問題内容など):** {display_row[0] if len(display_row) > 0 else ''}")
        st.write(f"**B1:** {display_row[1] if len(display_row) > 1 else ''}")
        st.write(f"**C1:** {display_row[2] if len(display_row) > 2 else ''}")
except Exception as e:
    st.info("データの読み込み中、またはデータが空です。")
