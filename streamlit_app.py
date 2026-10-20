import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. 設定・スプレッドシート接続
# ==========================================
URL_BASE = "https://www." + "googleapis.com" + "/auth/"
FINAL_SCOPE = [URL_BASE + "spreadsheets", URL_BASE + "drive"]

GOOGLE_CREDS_INFO = {
    "type": "service_account",
    "project_id": "question-follow",
    "private_key_id": "0bec49dec6e95caf628fca4f40fcadf1936a3642",
    "private_key": (
        "-----BEGIN PRIVATE KEY-----\n"
        "MIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQC+8M+HqseFR7eh\n"
        "hHQqLd6mBUjYIiMffv8UxLf7gsUz7ZLI3c+PfbrNIlxc1Es9vdiEpJIdpue7iOWi\n"
        "j0VPy6uQ5gx3ghq4P7xilLJHRiyQs5SSBnygwXcZnpruH1Y47rOA2mvjA0E2+GQ1\n"
        "O2eUpoSH3JLUaHupa9ZErB+WnNu7YTNxCHUJHikHUX8qlgXsG7pJXkeA/iAVaPkb\n"
        "jo8QHOhn0+XC+nUb9rryivhfzqWMwDT/Hwm568x2hwENQQDoT/B2/IwhBuejZVKK\n"
        "AXB9wRvRhUhe67AJ2fVpdzuXUP6W5ChRBDOH/W6KS+o5JyI5KWHDSuYR7QL8NcR7\n"
        "P1HgccW9AgMBAAECggEADEpe6WouRp97q/tlKNPkCYa8jiEAZsYbcEBLYXak7/dC\n"
        "ZAiXFDLxI8Qq8tS9dR9zwPIA78SvFOy2b1TOjtja1cxhEA5BXwvHOgc9RIY5VyUg\n"
        "Epg1THm3i2Ags+Qzfh2rU0d7+1RZzcqGVMDapYBkdoRVtTN2hkzJMYlszRqSsEhw\n"
        "eyaRaQza6XT5DrqyyH8s3vIPIZrvNwgxUfT0P3YW+6HOiqTWt2YMzUUq8GaeA+oH\n"
        "F0XTm1hYtbc8uqB7qiVghkoVQ2gZVDh0PRGjR8EJcekZSt8muxem3g6NCd0PLxKM\n"
        "b1zD0g0Rer/Qo4q086A9wyH1iMoaF+G3rvjRqeIgsQKBgQDeWp0EqJX8/DwrnVjs\n"
        "JoblYp8jPnDLu63dCBmWFEE+FgiS+pEInThL9xLfmatm70YDezpLIb3f3sfQ2N1W\n"
        "B0NuiNtHE6DXMvoQ5t7RDm6JhsOKa0jE41sy4elmTkEZGFkQJHdme+Trnc1UxIpM\n"
        "5IU6EmlIr3rTIvw8RtZeQLDapQKBgQDb1VT7VrcVeteEiurH1clsXS2F7DF2lDTi\n"
        "HNiyMybrDpkoGAmzmoV/rn3wr/QwOxqsv5USgvFEIJCGWvjf2W4reWVLZQGGbACL\n"
        "TrrUgrEyoAwJ3trstqEcLdYK5+Y7uEVlrJ0dOTEGviyDl6rpo9LUIp8+2jro8GM3\n"
        "/3ZLTTwLOQKBgAi9Zw6X0c1v3K2aMbSWjxbVGYw5GBXp+puFhfvwL+BQ3WVpk+nS\n"
        "xDO4MnW3hJU3MnlQjqoFWYFDMHd1Dr4i6vOdTYEttFTBHDMt3/Q3rQCa23TFYsba\n"
        "aOtHFfV/fe+OlXGc/VR56jWYrkl2sDj1gocV0i2ZOCq0ZVW5MxPhVxJBAoGBANHM\n"
        "7YfZoG19iUXTlnIVVGB5JMMVQbebhkTtptma+9+FVSHwnwGrzRCoJUWZh4CoR7Lq\n"
        "PIkoMr4EHio7lB1+0yfmeYfU4/m4BWTuRFwgRqC8IgEhkOos+eF81TQfUZlZKdH5\n"
        "RRDoziNTSARmsRS95q3SRQylFWfOU8LTqb//+/fxAoGBAJh5J/c3L9qLJinIf2Xj\n"
        "jFVxi/K57PR73HsWcYiSphDyDA+NX36w7wEne6QKQlKsVk88ClWucaLxpviDVMqB\n"
        "EeOUKoHdnbhQJLdqCqtnoseRqU90EpszYFgeZyFmCLSPzqWC4hGHY/BRUJveC5XW\n"
        "hG3maLgnF5Vy9EoF3XJbM5DO\n"
        "-----END PRIVATE KEY-----\n"
    ),
    "client_email": "question-follow" + "@" + "://gserviceaccount.com",
    "client_id": "116952924954061923842",
    "auth_uri": "https://accounts." + "google.com" + "/o/oauth2/auth",
    "token_uri": "https://oauth2." + "googleapis.com" + "/token",
    "auth_provider_x509_cert_url": "https://www." + "googleapis.com" + "/oauth2/v1/certs",
    "client_x509_cert_url": "https://www." + "googleapis.com" + "/robot/v1/metadata/x509/question-follow%40://gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

def init_sheets():
    try:
        CREDS = Credentials.from_service_account_info(GOOGLE_CREDS_INFO, scopes=FINAL_SCOPE)
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

    # 【修正箇所】マトリックス配列から1セルずつバラのテキスト情報として確実に抜き出す仕様に修正
    val_a1 = str(data_matrix[0][0])  # 現在の行のA列
    val_b1 = str(data_matrix[0][1])  # 現在の行のB列
    val_c1 = str(data_matrix[0][2])  # 現在の行のC列
    val_a2 = str(data_matrix[1][0])  # 次の行のA列
    
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
        st.write(f"**A1 (問題内容など):** {current_display[0][0] if len(current_display[0]) > 0 else ''}")
        st.write(f"**B1:** {current_display[0][1] if len(current_display[0]) > 1 else ''}")
        st.write(f"**C1:** {current_display[0][2] if len(current_display[0]) > 2 else ''}")
except Exception as e:
    st.info("データの読み込み中、またはデータが空です。")
