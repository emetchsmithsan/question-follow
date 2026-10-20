import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. 設定・スプレッドシート接続
# ==========================================
# 正しいGoogle APIのSCOPEを設定（スプレッドシートとドライブへのアクセス権限）
SCOPE = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

@st.cache_resource
def init_sheets():
    # StreamlitのSecretsから認証情報を安全に読み込みます
    creds_dict = dict(st.secrets["gspread_service_account"])
    CREDS = Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
    client = gspread.authorize(CREDS)

    # ------------------------------------------
    # ご自身のスプレッドシートIDを設定
    # ------------------------------------------
    INPUT_FILE_ID = '17r20Mrovxy1hLx1taLhHsRZzGKvUf_oZEvI1Z-Vnix0' 
    OUTPUT_FILE_ID = '1a0v3VCqkpXRtq6gMMfIoQIkUxckxa5Y-wJ0kKcYo3m4'

    return {
        "console": client.open_by_key(INPUT_FILE_ID).worksheet("コンソール"),
        "data": client.open_by_key(INPUT_FILE_ID).worksheet("問題データ"),
        "output": client.open_by_key(OUTPUT_FILE_ID).worksheet("問題フォロー出力先")
    }

# スプレッドシートの初期化
try:
    sheets = init_sheets()
except Exception as e:
    st.error(f"スプレッドシートの接続に失敗しました。Secretsの設定やスプレッドシートの共有設定を確認してください。\nエラー詳細: {e}")
    st.stop()

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
    
    # 1. スプレッドシートのカウンター(F1)を更新
    sheets["console"].update_acell("F1", new_line)
    
    # 2. 問題データから2行×3列を一発で取得 (A列~C列)
    range_str = f"A{new_line}:C{new_line + 1}"
    data_matrix = sheets["data"].get(range_str)
    
    # データが足りない場合のプレースホルダー処理
    while len(data_matrix) < 2:
        data_matrix.append(["", "", ""])
    for i in range(2):
        while len(data_matrix[i]) < 3:
            data_matrix[i].append("")

    val_a1, val_b1, val_c1 = data_matrix[0][0], data_matrix[0][1], data_matrix[0][2]
    val_a2 = data_matrix[1][0]
    
    # 3. 自分のコンソールシートのA1:C1に書き込み
    sheets["console"].update(range_str="A1:C1", values=[[val_a1, val_b1, val_c1]])
    
    # 4. 別ファイル（問題フォロー出力先）に一括書き込み (batch_updateで高速化)
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

# 現在の状況を表示
st.metric(label="現在の行（問題番号など）", value=st.session_state.current_line)

# ボタンの配置（横並び）
col1, col2 = st.columns(2)
with col1:
    if st.button("⬅️ 前の問題へ", use_container_width=True):
        move_line(-1)
        st.rerun()

with col2:
    if st.button("次の問題へ ➡️", use_container_width=True):
        move_line(1)
        st.rerun()

# 現在の選択データを表示（確認用）
st.subheader("書き込みデータ確認")
try:
    current_display = sheets["console"].get("A1:C1")
    if current_display and len(current_display) > 0:
        st.write(f"**A1 (問題内容など):** {current_display[0][0] if len(current_display[0]) > 0 else ''}")
        st.write(f"**B1:** {current_display[0][1] if len(current_display[0]) > 1 else ''}")
        st.write(f"**C1:** {current_display[0][2] if len(current_display[0]) > 2 else ''}")
except Exception as e:
    st.info("データの読み込み中、またはデータが空です。")
