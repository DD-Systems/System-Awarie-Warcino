import streamlit as st
import pandas as pd
import os
import hashlib
import smtplib
import json
from datetime import datetime
from email.message import EmailMessage

# Konfiguracja strony
st.set_page_config(page_title="System Awarii", page_icon="🛠️", layout="wide")

USER_FILE = "uzytkownicy.csv"
REPORT_FILE = "zgloszenia.csv"
RESET_REQUEST_FILE = "reset_hasla.csv"
NOTIFY_EMAIL = "daniel@wmc24.pl"
USER_COLUMNS = ["Email", "Nazwa użytkownika", "Haslo", "Rola"]
RESET_REQUEST_COLUMNS = [
    "ID",
    "Data",
    "Email",
    "Nazwa użytkownika",
    "Powod",
    "Status",
    "Obsluzone przez",
    "Data obslugi",
]
REPORT_COLUMNS = [
    "ID",
    "Data",
    "Email",
    "Nazwa użytkownika",
    "Opis",
    "Urządzenie",
    "Status",
    "Rozwiązanie",
    "Historia zmian",
    "Komentarz",
    "Data aktualizacji",
]

st.markdown(
    "<style>"
    ":root {"
    "  --forest-deep: #1f3b2c;"
    "  --forest: #2f5a3c;"
    "  --forest-soft: #6d866f;"
    "  --paper: #f7f1e6;"
    "  --paper-strong: #fffdf8;"
    "  --line: rgba(49, 77, 57, 0.14);"
    "  --gold: #b78a34;"
    "  --ink: #243427;"
    "  --muted: #647463;"
    "}"
    "body { background: #ece4d7; }"
    ".stApp {"
    "  background:"
    "    radial-gradient(circle at top left, rgba(91, 122, 93, 0.12), transparent 24%),"
    "    radial-gradient(circle at top right, rgba(183, 138, 52, 0.08), transparent 22%),"
    "    linear-gradient(180deg, #ebe2d5 0%, #f3ede4 26%, #eee5da 100%);"
    "  color: var(--ink);"
    "}"
    ".block-container { max-width: 1500px; padding-top: 2.25rem; padding-bottom: 2.4rem; }"
    "h1, h2, h3 {"
    "  font-family: Georgia, 'Times New Roman', serif;"
    "  color: var(--forest-deep);"
    "  letter-spacing: 0.01em;"
    "}"
    "p, label, .stCaption, .stMarkdown, .stText { color: #314536; }"
    "[data-testid='stRadio'] label, [data-testid='stRadio'] div[role='radiogroup'] label {"
    "  color: var(--forest-deep) !important;"
    "  font-weight: 700;"
    "}"
    "[data-testid='stRadio'] div[role='radiogroup'] { gap: 1rem; }"
    "[data-testid='stRadio'] div[role='radiogroup'] > label {"
    "  background: rgba(255, 252, 245, 0.92);"
    "  border: 1px solid rgba(47, 90, 60, 0.14);"
    "  border-radius: 999px;"
    "  padding: 0.55rem 0.95rem;"
    "}"
    "[data-testid='stRadio'] input { accent-color: var(--forest); }"
    "[data-testid='stMetric'] {"
    "  background: linear-gradient(180deg, #fffdf9 0%, #f8f2e8 100%);"
    "  border: 1px solid rgba(183, 138, 52, 0.16);"
    "  border-radius: 1rem;"
    "  padding: 0.9rem 1rem;"
    "  box-shadow: 0 10px 26px rgba(45, 59, 40, 0.05);"
    "}"
    "[data-testid='stMetricLabel'], [data-testid='stMetricValue'] { color: var(--forest-deep); }"
    ".stAlert { border-radius: 1rem; border: 1px solid var(--line); }"
    ".stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {"
    "  border-radius: 1rem;"
    "  border: 1px solid rgba(183, 138, 52, 0.22);"
    "  background: linear-gradient(135deg, #274632 0%, #2f5a3c 55%, #3f6f4c 100%);"
    "  color: #fffef8 !important;"
    "  font-weight: 800;"
    "  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.18);"
    "  letter-spacing: 0.01em;"
    "  line-height: 1.1;"
    "  min-height: 3rem;"
    "  padding: 0.62rem 1.2rem;"
    "  box-shadow: 0 14px 28px rgba(35, 65, 47, 0.14);"
    "  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;"
    "}"
    ".stButton > button span, .stDownloadButton > button span, .stFormSubmitButton > button span,"
    " .stButton > button div, .stDownloadButton > button div, .stFormSubmitButton > button div,"
    " .stButton > button p, .stDownloadButton > button p, .stFormSubmitButton > button p {"
    "  color: #fffef8 !important;"
    "  font-weight: 800 !important;"
    "  opacity: 1 !important;"
    "  text-shadow: 0 1px 1px rgba(0, 0, 0, 0.18) !important;"
    "}"
    ".stButton > button:hover, .stDownloadButton > button:hover, .stFormSubmitButton > button:hover {"
    "  border-color: var(--gold);"
    "  background: linear-gradient(135deg, #23412f 0%, #2f5a3c 60%, #497856 100%);"
    "  box-shadow: 0 18px 34px rgba(35, 65, 47, 0.18);"
    "  transform: translateY(-1px);"
    "}"
    "[data-testid='stTextInput'] input, [data-testid='stTextArea'] textarea {"
    "  background: #fffdf8 !important;"
    "  color: var(--forest-deep) !important;"
    "  border: 1px solid rgba(47, 90, 60, 0.16) !important;"
    "  border-radius: 1rem !important;"
    "  box-shadow: 0 8px 18px rgba(45, 59, 40, 0.05) !important;"
    "  padding-left: 0.2rem !important;"
    "  min-height: 3rem !important;"
    "  text-align: center !important;"
    "  transition: border-color 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;"
    "}"
    "[data-testid='stTextInput'] input:focus, [data-testid='stTextArea'] textarea:focus {"
    "  border-color: rgba(183, 138, 52, 0.85) !important;"
    "  background: #ffffff !important;"
    "  box-shadow: 0 0 0 3px rgba(183, 138, 52, 0.12), 0 14px 28px rgba(45, 59, 40, 0.08) !important;"
    "}"
    "[data-testid='stTextInput'] input::placeholder, [data-testid='stTextArea'] textarea::placeholder {"
    "  color: #7a8678 !important;"
    "  opacity: 1 !important;"
    "  text-align: center !important;"
    "}"
    "[data-testid='stTextInput'] label, [data-testid='stTextArea'] label {"
    "  color: var(--forest-deep) !important;"
    "}"
    "[data-testid='stTextInput'] > div, [data-testid='stTextArea'] > div {"
    "  border-radius: 1rem !important;"
    "}"
    "[data-testid='stDataFrame'] {"
    "  background: var(--paper-strong);"
    "  border: 1px solid var(--line);"
    "  border-radius: 1rem;"
    "  overflow: hidden;"
    "  box-shadow: 0 18px 42px rgba(45, 59, 40, 0.06);"
    "}"
    " #MainMenu {visibility: hidden;}"
    " footer {visibility: hidden;}"
    " header {visibility: hidden;}"
    " .stAppDeployButton {display:none;}"
    " [data-testid='stStatusWidget'] {display:none;}"
    " .viewerBadge_container__1QSob {display:none !important;}"
    ".forest-hero {"
    "  background: linear-gradient(120deg, rgba(28, 55, 40, 0.98), rgba(52, 91, 61, 0.94));"
    "  color: #fffaf0;"
    "  border-radius: 1.5rem;"
    "  padding: 1.7rem 1.8rem;"
    "  box-shadow: 0 24px 50px rgba(34, 48, 29, 0.14);"
    "  margin-top: 0.95rem;"
    "  margin-bottom: 1.7rem;"
    "}"
    ".forest-hero__top {"
    "  display: flex;"
    "  align-items: center;"
    "  justify-content: space-between;"
    "  gap: 1.2rem;"
    "}"
    ".forest-hero__content { flex: 1; min-width: 0; }"
    ".forest-hero__eyebrow {"
    "  text-transform: uppercase;"
    "  letter-spacing: 0.16em;"
    "  font-size: 0.76rem;"
    "  font-weight: 700;"
    "  color: #e7d19b;"
    "  margin-bottom: 0.45rem;"
    "}"
    ".forest-hero__title {"
    "  font-family: Georgia, 'Times New Roman', serif;"
    "  font-size: 2rem;"
    "  line-height: 1.1;"
    "  font-weight: 700;"
    "  margin: 0;"
    "}"
    ".forest-hero__subtitle {"
    "  margin-top: 0.65rem;"
    "  max-width: 760px;"
    "  color: rgba(255, 248, 234, 0.84);"
    "  font-size: 0.98rem;"
    "  line-height: 1.55;"
    "}"
    ".forest-greeting {"
    "  display: flex;"
    "  flex-direction: column;"
    "  align-items: flex-end;"
    "  justify-content: center;"
    "  min-width: 220px;"
    "  text-align: right;"
    "}"
    ".forest-greeting__text {"
    "  margin-top: 0.15rem;"
    "  font-family: Georgia, 'Times New Roman', serif;"
    "  font-size: 1.65rem;"
    "  font-style: italic;"
    "  font-weight: 700;"
    "  color: #fff7e8;"
    "  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.14);"
    "}"
    ".forest-greeting__line {"
    "  width: 92px;"
    "  height: 2px;"
    "  margin-top: 0.55rem;"
    "  border-radius: 999px;"
    "  background: linear-gradient(90deg, rgba(231, 209, 155, 0), rgba(231, 209, 155, 0.9));"
    "}"
    ".section-title {"
    "  display: inline-block;"
    "  margin: 0.1rem 0 0.6rem 0;"
    "  padding-bottom: 0.2rem;"
    "  border-bottom: 2px solid rgba(183, 138, 52, 0.55);"
    "}"
    ".section-note {"
    "  margin: -0.1rem 0 0.9rem 0;"
    "  color: var(--muted);"
    "}"
    ".auth-note {"
    "  color: var(--muted);"
    "  margin: 0 0 1rem 0;"
    "}"
    ".auth-info-card {"
    "  background: linear-gradient(180deg, rgba(255,251,244,0.94), rgba(245,238,226,0.98));"
    "  border: 1px solid rgba(183, 138, 52, 0.16);"
    "  border-radius: 1.35rem;"
    "  padding: 1.35rem 1.2rem;"
    "  box-shadow: 0 18px 38px rgba(45, 59, 40, 0.06);"
    "}"
    ".auth-info-card__title {"
    "  font-family: Georgia, 'Times New Roman', serif;"
    "  font-size: 1.2rem;"
    "  color: var(--forest-deep);"
    "  font-weight: 700;"
    "  margin-bottom: 0.6rem;"
    "}"
    ".auth-info-card__text {"
    "  color: #4d5e4f;"
    "  line-height: 1.6;"
    "  font-size: 0.96rem;"
    "}"
    ".auth-mode-caption {"
    "  font-size: 0.9rem;"
    "  color: var(--muted);"
    "  margin: 0 0 0.85rem 0;"
    "}"
    "@media (max-width: 900px) {"
    "  .forest-hero__top { flex-direction: column; }"
    "  .forest-greeting { align-items: flex-start; text-align: left; min-width: 0; }"
    "  .forest-greeting__line { background: linear-gradient(90deg, rgba(231, 209, 155, 0.9), rgba(231, 209, 155, 0)); }"
    "}"
    "</style>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='forest-hero'>"
    "<div class='forest-hero__top'>"
    "<div class='forest-hero__content'>"
    "<div class='forest-hero__eyebrow'>Panel wewnętrzny • obsługa usterek</div>"
    "<h1 class='forest-hero__title'>Panel zgłoszeniowy awarii</h1>"
    "</div>"
    "<div class='forest-greeting'>"
    "<div class='forest-greeting__text'>Darz Bór</div>"
    "<div class='forest-greeting__line'></div>"
    "</div>"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)


# --- FUNKCJE POMOCNICZE ---

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def load_users() -> pd.DataFrame:
    if os.path.isfile(USER_FILE):
        df = pd.read_csv(USER_FILE)
        for column in USER_COLUMNS:
            if column not in df.columns:
                df[column] = ""
        df = df[USER_COLUMNS].copy()
        df["Rola"] = df["Rola"].replace("", pd.NA).fillna("Użytkownik")
        return df
    return pd.DataFrame(columns=USER_COLUMNS)


def save_users(df: pd.DataFrame) -> None:
    df = df.copy()[USER_COLUMNS]
    df.to_csv(USER_FILE, index=False)


def load_reset_requests() -> pd.DataFrame:
    if os.path.isfile(RESET_REQUEST_FILE):
        df = pd.read_csv(RESET_REQUEST_FILE)
        for column in RESET_REQUEST_COLUMNS:
            if column not in df.columns:
                df[column] = ""
        df = df[RESET_REQUEST_COLUMNS].copy()
        df["Status"] = df["Status"].replace("", pd.NA).fillna("Oczekuje")
        df["Powod"] = df["Powod"].fillna("")
        return df
    return pd.DataFrame(columns=RESET_REQUEST_COLUMNS)


def save_reset_requests(df: pd.DataFrame) -> None:
    df = df.copy()[RESET_REQUEST_COLUMNS]
    df.to_csv(RESET_REQUEST_FILE, index=False)


def update_user_role(email: str, new_role: str) -> tuple[bool, str]:
    users = load_users()
    if users.empty:
        return False, "Brak użytkowników do aktualizacji."

    user_mask = users["Email"].astype(str).str.lower() == email.strip().lower()
    if not user_mask.any():
        return False, "Nie znaleziono użytkownika o wskazanym emailu."

    users.loc[user_mask, "Rola"] = new_role
    save_users(users)
    return True, "Rola użytkownika została zaktualizowana."


def safe_json_loads(value: str, default):
    if not value or pd.isna(value):
        return default
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return default


def dumps_compact(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def load_reports() -> pd.DataFrame:
    if not os.path.isfile(REPORT_FILE):
        return pd.DataFrame(columns=REPORT_COLUMNS)

    df = pd.read_csv(REPORT_FILE)
    if "Priorytet" in df.columns:
        df = df.drop(columns=["Priorytet"])

    for column in REPORT_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    df = df[REPORT_COLUMNS].copy()
    df["Status"] = df["Status"].replace("", pd.NA).fillna("Nowe")
    df["Rozwiązanie"] = df["Rozwiązanie"].fillna("")
    df["Historia zmian"] = df["Historia zmian"].apply(lambda value: dumps_compact(safe_json_loads(value, [])))
    df["ID"] = pd.to_numeric(df["ID"], errors="coerce")
    if df["ID"].isna().any():
        df["ID"] = range(1, len(df) + 1)
    df["ID"] = df["ID"].astype(int)
    return df


def save_reports(df: pd.DataFrame) -> None:
    df = df.copy()[REPORT_COLUMNS]
    df.to_csv(REPORT_FILE, index=False)


def is_admin_user(user_role: str, user_name: str) -> bool:
    return user_role.lower() == "administrator" or user_name.lower() == "admin"


def append_history_entry(history_value: str, actor: str, action: str) -> str:
    history = safe_json_loads(history_value, [])
    history.append(
        {
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "autor": actor,
            "akcja": action,
        }
    )
    return dumps_compact(history)


def format_history(history_value: str) -> str:
    history = safe_json_loads(history_value, [])
    if not history:
        return "Brak historii zmian."
    return "\n".join(f"{item['data']} | {item['autor']} | {item['akcja']}" for item in history)




def send_report_notification(subject: str, body_lines: list[str]) -> tuple[bool, str]:
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM") or smtp_user
    notify_to = os.getenv("REPORT_NOTIFY_TO", NOTIFY_EMAIL)

    if not all([smtp_host, smtp_user, smtp_password, smtp_from]):
        return False, "Powiadomienie email nie zostało wysłane, bo brakuje konfiguracji SMTP."

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = smtp_from
    message["To"] = notify_to
    message.set_content("\n".join(body_lines))

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        return True, f"Powiadomienie email zostało wysłane na {notify_to}."
    except Exception as exc:
        return False, f"Nie udało się wysłać powiadomienia email: {exc}"


def send_new_report_notification(report_row: dict) -> tuple[bool, str]:
    return send_report_notification(
        f"Nowe zgłoszenie awarii #{report_row['ID']} - {report_row['Urządzenie']}",
        [
            "Dodano nowe zgłoszenie awarii.",
            "",
            f"ID: {report_row['ID']}",
            f"Data: {report_row['Data']}",
            f"Użytkownik: {report_row['Nazwa użytkownika']}",
            f"Email: {report_row['Email']}",
            f"Urządzenie: {report_row['Urządzenie']}",
            f"Status: {report_row['Status']}",
            "",
            "Opis:",
            str(report_row["Opis"]),
        ],
    )


def send_status_change_notification(report_row: dict, previous_status: str, actor: str) -> tuple[bool, str]:
    body_lines = [
        "Status zgłoszenia został zmieniony.",
        "",
        f"ID: {report_row['ID']}",
        f"Użytkownik: {report_row['Nazwa użytkownika']}",
        f"Email: {report_row['Email']}",
        f"Urządzenie: {report_row['Urządzenie']}",
        f"Poprzedni status: {previous_status}",
        f"Nowy status: {report_row['Status']}",
        f"Zmienił: {actor}",
        "",
        "Opis:",
        str(report_row["Opis"]),
    ]
    if str(report_row.get("Rozwiązanie", "")).strip():
        body_lines.extend(["", "Rozwiązanie:", str(report_row["Rozwiązanie"])])
    return send_report_notification(
        f"Zmiana statusu zgłoszenia #{report_row['ID']} - {report_row['Status']}",
        body_lines,
    )


def register_user(email: str, username: str, password: str) -> tuple[bool, str]:
    users = load_users()
    if not email.strip() or not username.strip() or not password.strip():
        return False, "Wszystkie pola rejestracji muszą być wypełnione."

    email_lower = email.strip().lower()
    if not email_lower.endswith("@tlwarcino.pl"):
        return False, "Rejestracja jest dostępna tylko dla adresów email w domenie tlwarcino.pl."
    username_lower = username.strip().lower()
    if email_lower in users["Email"].astype(str).str.lower().tolist():
        return False, "Ten email jest już zarejestrowany."
    if username_lower in users["Nazwa użytkownika"].astype(str).str.lower().tolist():
        return False, "Ta nazwa użytkownika jest już zajęta."

    nowy = pd.DataFrame([[email.strip(), username.strip(), hash_password(password), "Użytkownik"]], columns=USER_COLUMNS)
    users = pd.concat([users, nowy], ignore_index=True)
    save_users(users)
    return True, "Rejestracja zakończona sukcesem. Teraz możesz się zalogować."


def create_password_reset_request(email: str, username: str, reason: str) -> tuple[bool, str]:
    users = load_users()
    if users.empty:
        return False, "Baza użytkowników jest pusta."

    if not email.strip() or not new_password.strip() or not confirm_password.strip():
        return False, "Wszystkie pola resetu hasła muszą być wypełnione."

    if new_password != confirm_password:
        return False, "Nowe hasła muszą być identyczne."

    email_lower = email.strip().lower()
    if not email_lower.endswith("@tlwarcino.pl"):
        return False, "Reset hasĹ‚a jest dostÄ™pny tylko dla zarejestrowanych adresĂłw email w domenie tlwarcino.pl."

    user_mask = users["Email"].astype(str).str.lower() == email_lower
    if not user_mask.any():
        return False, "Nie znaleziono użytkownika z takim adresem email."

    users.loc[user_mask, "Haslo"] = hash_password(new_password)
    save_users(users)
    return True, "Hasło zostało zmienione. Możesz się teraz zalogować."


def submit_password_reset_request(email: str, username: str, reason: str) -> tuple[bool, str]:
    users = load_users()
    if users.empty:
        return False, "Baza uzytkownikow jest pusta."

    if not email.strip() or not username.strip():
        return False, "Podaj email oraz nazwe uzytkownika."

    email_lower = email.strip().lower()
    username_lower = username.strip().lower()
    if not email_lower.endswith("@tlwarcino.pl"):
        return False, "Reset hasla jest dostepny tylko dla adresow email w domenie tlwarcino.pl."

    user_mask = (
        (users["Email"].astype(str).str.lower() == email_lower)
        & (users["Nazwa użytkownika"].astype(str).str.lower() == username_lower)
    )
    if not user_mask.any():
        return False, "Nie znaleziono konta z takim emailem i nazwa uzytkownika."

    requests_df = load_reset_requests()
    pending_mask = (
        (requests_df["Email"].astype(str).str.lower() == email_lower)
        & (requests_df["Status"].astype(str) == "Oczekuje")
    )
    if pending_mask.any():
        return False, "Dla tego konta jest juz aktywna prosba o reset hasla."

    next_id = int(pd.to_numeric(requests_df["ID"], errors="coerce").max() + 1) if not requests_df.empty else 1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_request = pd.DataFrame(
        [[next_id, now, email.strip(), username.strip(), reason.strip(), "Oczekuje", "", ""]],
        columns=RESET_REQUEST_COLUMNS,
    )
    requests_df = pd.concat([requests_df, new_request], ignore_index=True)
    save_reset_requests(requests_df)
    return True, "Prosba o reset hasla zostala zapisana. Administrator musi ja zatwierdzic."


def approve_password_reset_request(request_id: int, new_password: str, admin_name: str) -> tuple[bool, str]:
    requests_df = load_reset_requests()
    if requests_df.empty:
        return False, "Brak prosb o reset hasla."

    if not str(new_password).strip():
        return False, "Podaj nowe haslo dla wskazanego konta."

    request_mask = pd.to_numeric(requests_df["ID"], errors="coerce") == int(request_id)
    if not request_mask.any():
        return False, "Nie znaleziono wskazanej prosby."

    request_row = requests_df.loc[request_mask].iloc[0]
    if str(request_row["Status"]) != "Oczekuje":
        return False, "Ta prosba zostala juz obsluzona."

    users = load_users()
    user_mask = users["Email"].astype(str).str.lower() == str(request_row["Email"]).strip().lower()
    if not user_mask.any():
        return False, "Nie znaleziono uzytkownika powiazanego z ta prosba."

    users.loc[user_mask, "Haslo"] = hash_password(new_password)
    save_users(users)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    requests_df.loc[request_mask, "Status"] = "Zatwierdzona"
    requests_df.loc[request_mask, "Obsluzone przez"] = admin_name
    requests_df.loc[request_mask, "Data obslugi"] = now
    save_reset_requests(requests_df)
    return True, "Haslo zostalo zresetowane. Przekaz nowe haslo uzytkownikowi bezpiecznym kanalem."


def reject_password_reset_request(request_id: int, admin_name: str) -> tuple[bool, str]:
    requests_df = load_reset_requests()
    if requests_df.empty:
        return False, "Brak prosb o reset hasla."

    request_mask = pd.to_numeric(requests_df["ID"], errors="coerce") == int(request_id)
    if not request_mask.any():
        return False, "Nie znaleziono wskazanej prosby."

    request_row = requests_df.loc[request_mask].iloc[0]
    if str(request_row["Status"]) != "Oczekuje":
        return False, "Ta prosba zostala juz obsluzona."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    requests_df.loc[request_mask, "Status"] = "Odrzucona"
    requests_df.loc[request_mask, "Obsluzone przez"] = admin_name
    requests_df.loc[request_mask, "Data obslugi"] = now
    save_reset_requests(requests_df)
    return True, "Prosba o reset hasla zostala odrzucona."


def authenticate_user(login: str, password: str) -> tuple[bool, dict]:
    if login.strip().lower() == "admin" and password == "admin":
        return True, {"email": "admin@wmc.local", "username": "admin", "role": "Administrator"}

    users = load_users()
    if users.empty:
        return False, {}

    hashed = hash_password(password)
    login_value = login.strip().lower()
    match = users[
        (((users["Email"].astype(str).str.lower() == login_value) |
          (users["Nazwa użytkownika"].astype(str).str.lower() == login_value)) &
         (users["Haslo"] == hashed))
    ]
    if not match.empty:
        user = match.iloc[0]
        return True, {"email": user["Email"], "username": user["Nazwa użytkownika"], "role": user["Rola"]}
    return False, {}


# --- STAN SESJI ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = ""
    st.session_state.user_name = ""
    st.session_state.user_role = ""


# --- LOGOWANIE I REJESTRACJA ---
if not st.session_state.authenticated:
    spacer_left, auth_col, spacer_right = st.columns([2, 10, 2])
    with auth_col:
        st.markdown("<div class='section-title'><h3>Logowanie i rejestracja</h3></div>", unsafe_allow_html=True)

        info_col, form_col = st.columns([4, 8], gap="large")
        with info_col:
            with st.container(border=True):
                st.markdown(
                    "<div class='auth-info-card'>"
                    "<div class='auth-info-card__title'>Panel zgłaszania awarii</div>"
                    "<div class='auth-info-card__text'>"
                    "Zaloguj się, aby zgłaszać usterki sprzętu i oprogramowania, śledzić historię wpisów oraz aktualizować własne zgłoszenia."
                    "</div>"
                    "</div>",
                    unsafe_allow_html=True,
                )

        with form_col:
            with st.container(border=True):
                auth_mode = st.radio(
                    "Tryb panelu",
                    ["Logowanie", "Rejestracja", "Reset hasła"],
                    index=0,
                    horizontal=True,
                    label_visibility="collapsed",
                )

                if auth_mode == "Logowanie":
                    st.markdown("<div class='auth-mode-caption'>Dostęp do konta użytkownika lub administratora.</div>", unsafe_allow_html=True)
                    with st.form("login_form", clear_on_submit=True):
                        login = st.text_input("Email lub nazwa użytkownika", placeholder="Wpisz email lub nazwę użytkownika")
                        password = st.text_input("Hasło", type="password", placeholder="Wpisz swoje hasło")
                        login_button = st.form_submit_button("Zaloguj się")

                    if login_button:
                        success, user_data = authenticate_user(login, password)
                        if success:
                            st.session_state.authenticated = True
                            st.session_state.user_email = user_data["email"]
                            st.session_state.user_name = user_data["username"]
                            st.session_state.user_role = user_data["role"]
                            st.success(f"Zalogowano jako {st.session_state.user_name}")
                            st.rerun()
                        else:
                            st.error("Nieprawidłowy login lub hasło.")
                elif auth_mode == "Rejestracja":
                    st.markdown("<div class='auth-mode-caption'>Załóż nowe konto, aby zgłaszać i edytować własne awarie.</div>", unsafe_allow_html=True)
                    with st.form("register_form", clear_on_submit=True):
                        reg_email = st.text_input("Email", placeholder="np. jan.kowalski@tlwarcino.pl")
                        reg_username = st.text_input("Nazwa użytkownika", placeholder="Wybierz nazwę użytkownika")
                        reg_password = st.text_input("Hasło", type="password", placeholder="Ustaw hasło")
                        reg_password_confirm = st.text_input("Powtórz hasło", type="password", placeholder="Powtórz hasło")
                        register_button = st.form_submit_button("Zarejestruj się")

                    if register_button:
                        if reg_password != reg_password_confirm:
                            st.error("Hasła muszą być identyczne.")
                        else:
                            success, message = register_user(reg_email.strip(), reg_username.strip(), reg_password)
                            if success:
                                st.success(message)
                            else:
                                st.error(message)
                else:
                    st.markdown("<div class='auth-mode-caption'>Zloz prosbe o reset hasla. Administrator zatwierdzi ja w panelu.</div>", unsafe_allow_html=True)
                    with st.form("reset_password_request_form", clear_on_submit=True):
                        request_email = st.text_input("Email do odzyskania hasla", placeholder="Podaj zarejestrowany adres email")
                        request_username = st.text_input("Nazwa uzytkownika", placeholder="Podaj swoja nazwe uzytkownika")
                        request_reason = st.text_area("Powod resetu", placeholder="Np. nie pamietam hasla", height=100)
                        request_reset_button = st.form_submit_button("Wyslij prosbe o reset")

                    if request_reset_button:
                        success, message = submit_password_reset_request(
                            request_email.strip(),
                            request_username.strip(),
                            request_reason.strip(),
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

                    st.info("Haslo nie jest zmieniane automatycznie. Administrator musi obsluzyc prosbe w panelu.")
                    st.stop()
                    st.markdown("<div class='auth-mode-caption'>Ustaw nowe hasło na podstawie zarejestrowanego adresu email.</div>", unsafe_allow_html=True)
                    with st.form("reset_password_form", clear_on_submit=True):
                        reset_email = st.text_input("Email do odzyskania hasła", placeholder="Podaj zarejestrowany adres email")
                        new_password = st.text_input("Nowe hasło", type="password", placeholder="Wpisz nowe hasło")
                        confirm_new_password = st.text_input("Powtórz nowe hasło", type="password", placeholder="Powtórz nowe hasło")
                        reset_button = st.form_submit_button("Ustaw nowe hasło")

                    if reset_button:
                        success, message = reset_password_by_email(
                            reset_email.strip(),
                            new_password,
                            confirm_new_password,
                        )
                        if success:
                            st.success(message)
                        else:
                            st.error(message)

else:
    is_admin = is_admin_user(st.session_state.user_role, st.session_state.user_name)
    is_staff = is_admin or st.session_state.user_role.lower() == "technik"
    st.success(
        f"Zalogowano jako {st.session_state.user_name} ({st.session_state.user_email})"
        f" | rola: {st.session_state.user_role or 'Użytkownik'}"
    )
    if st.button("Wyloguj się"):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.session_state.user_name = ""
        st.session_state.user_role = ""
        st.rerun()

    reports_source_df = load_reports()
    if not reports_source_df.empty:
        reports_source_df["Data"] = pd.to_datetime(reports_source_df["Data"], errors="coerce")
        reports_source_df["Data aktualizacji"] = pd.to_datetime(reports_source_df["Data aktualizacji"], errors="coerce")

    if is_admin:
        st.markdown("<div class='section-title'><h3>Dashboard administratora</h3></div>", unsafe_allow_html=True)
        if reports_source_df.empty:
            st.info("Dashboard będzie dostępny po dodaniu pierwszych zgłoszeń.")
        else:
            admin_col1, admin_col2, admin_col3, admin_col4 = st.columns(4)
            admin_col1.metric("Nowe", int((reports_source_df["Status"] == "Nowe").sum()))
            admin_col2.metric("W trakcie", int((reports_source_df["Status"] == "W trakcie").sum()))
            admin_col3.metric("Zamknięte", int((reports_source_df["Status"] == "Zamknięte").sum()))
            admin_col4.metric("Łącznie", len(reports_source_df))

            recent_admin_view = reports_source_df.sort_values(by="Data", ascending=False).head(5).copy()
            recent_admin_view["Data"] = recent_admin_view["Data"].dt.strftime("%Y-%m-%d %H:%M").fillna("-")
            st.dataframe(
                recent_admin_view[["ID", "Data", "Nazwa użytkownika", "Urządzenie", "Status"]],
                use_container_width=True,
                hide_index=True,
            )

            users_df = load_users()
            if not users_df.empty:
                with st.expander("Role użytkowników"):
                    st.dataframe(users_df[["Email", "Nazwa użytkownika", "Rola"]], use_container_width=True, hide_index=True)
                    editable_user_emails = users_df["Email"].astype(str).tolist()
                    with st.form("role_management_form"):
                        selected_user_email = st.selectbox("Użytkownik", editable_user_emails)
                        selected_role = st.selectbox("Nowa rola", ["Użytkownik", "Technik", "Administrator"])
                        update_role_button = st.form_submit_button("Zmień rolę")

                    if update_role_button:
                        role_ok, role_message = update_user_role(selected_user_email, selected_role)
                        if role_ok:
                            st.success(role_message)
                            st.rerun()
                        else:
                            st.error(role_message)

    st.markdown("<div class='section-title'><h3>Nowe zgłoszenie</h3></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Dodaj zgłoszenie awarii i przypisz je do właściwej kategorii.</div>", unsafe_allow_html=True)
    if is_admin:
        reset_requests_df = load_reset_requests()
        with st.expander("Prosby o reset hasla"):
            if reset_requests_df.empty:
                st.info("Brak prosb o reset hasla.")
            else:
                st.dataframe(reset_requests_df, use_container_width=True, hide_index=True)
                pending_requests = reset_requests_df[reset_requests_df["Status"].astype(str) == "Oczekuje"].copy()
                if pending_requests.empty:
                    st.caption("Brak oczekujacych prosb.")
                else:
                    pending_requests["request_label"] = pending_requests.apply(
                        lambda row: f"#{int(row['ID'])} | {row['Email']} | {row['Nazwa użytkownika']}",
                        axis=1,
                    )
                    request_options = pending_requests["request_label"].tolist()
                    selected_request_label = st.selectbox("Wybierz prosbe", request_options, key="reset_request_select")
                    selected_request = pending_requests[pending_requests["request_label"] == selected_request_label].iloc[0]
                    selected_request_id = int(selected_request["ID"])

                    with st.form("approve_reset_request_form"):
                        admin_new_password = st.text_input(
                            "Nowe haslo tymczasowe",
                            type="password",
                            placeholder="Ustaw nowe haslo dla uzytkownika",
                        )
                        approve_reset_button = st.form_submit_button("Zatwierdz i ustaw haslo")

                    if approve_reset_button:
                        reset_ok, reset_message = approve_password_reset_request(
                            selected_request_id,
                            admin_new_password,
                            st.session_state.user_name,
                        )
                        if reset_ok:
                            st.success(reset_message)
                            st.rerun()
                        else:
                            st.error(reset_message)

                    if st.button("Odrzuc prosbe", key=f"reject_reset_request_{selected_request_id}"):
                        reject_ok, reject_message = reject_password_reset_request(
                            selected_request_id,
                            st.session_state.user_name,
                        )
                        if reject_ok:
                            st.success(reject_message)
                            st.rerun()
                        else:
                            st.error(reject_message)

    with st.form("formularz_zgloszenia", clear_on_submit=True):
        st.write("Twoje dane użytkownika zostały uzupełnione automatycznie.")

        email = st.text_input("Email", value=st.session_state.user_email, disabled=True)
        nazwa_uzytkownika = st.text_input("Nazwa użytkownika", value=st.session_state.user_name, disabled=True)
        opis = st.text_area("Opis awarii (np. niedziała drukarka)", height=150)
        urzadzenie = st.selectbox("Urządzenie", ["Drukarka", "Komputer", "Przewody", "Oprogramowanie", "Inne"])
        przycisk = st.form_submit_button("Wyślij zgłoszenie")

    if przycisk:
        if opis:
            teraz = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            reports_df = load_reports()
            next_id = int(reports_df["ID"].max() + 1) if not reports_df.empty else 1
            history_value = append_history_entry("", st.session_state.user_name, "Utworzono zgłoszenie")
            nowy_wpis = pd.DataFrame(
                [[next_id, teraz, email, nazwa_uzytkownika, opis, urzadzenie, "Nowe", "", history_value, "", teraz]],
                columns=REPORT_COLUMNS,
            )
            reports_df = pd.concat([reports_df, nowy_wpis], ignore_index=True)
            save_reports(reports_df)
            st.success("✅ Zgłoszenie zostało zapisane pomyślnie!")
            notification_ok, notification_message = send_new_report_notification(nowy_wpis.iloc[0].to_dict())
            if notification_ok:
                st.info(notification_message)
            else:
                st.warning(notification_message)
        else:
            st.error("⚠️ Musisz podać opis awarii!")

    st.divider()
    st.markdown("<div class='section-title'><h3>Rejestr zgłoszeń</h3></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-note'>Przeglądaj historię zgłoszeń, filtruj wpisy i aktualizuj własne zgłoszenia.</div>", unsafe_allow_html=True)

    if os.path.exists(REPORT_FILE):
        df = reports_source_df.copy()
        df = df.sort_values(by="Data", ascending=False).reset_index(drop=True)

        total_reports = len(df)
        devices_count = df["Urządzenie"].nunique() if "Urządzenie" in df.columns else 0
        latest_date = df["Data"].dropna().max()

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Wszystkie zgłoszenia", total_reports)
        metric_col2.metric("Typy urządzeń", devices_count)
        metric_col3.metric(
            "Ostatnie zgłoszenie",
            latest_date.strftime("%Y-%m-%d %H:%M") if pd.notna(latest_date) else "brak",
        )

        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns([1, 1, 1, 1, 2])
        with filter_col1:
            device_options = ["Wszystkie"] + sorted(df["Urządzenie"].dropna().astype(str).unique().tolist())
            device_filter = st.selectbox(
                "Urządzenie",
                device_options,
                key="report_device_filter",
            )
        with filter_col2:
            status_filter = st.selectbox(
                "Status",
                ["Wszystkie", "Nowe", "W trakcie", "Zamknięte"],
                key="report_status_filter",
            )
        with filter_col3:
            view_filter = st.selectbox(
                "Widok",
                ["Wszystkie", "Moje zgłoszenia", "Otwarte", "Archiwum"],
                key="report_view_filter",
            )
        with filter_col4:
            sort_filter = st.selectbox(
                "Sortowanie",
                ["Najnowsze", "Najstarsze", "Status A-Z"],
                key="report_sort_filter",
            )
        with filter_col5:
            search_query = st.text_input(
                "Szukaj w zgłoszeniach",
                placeholder="Wpisz email, użytkownika albo fragment opisu",
                key="report_search_query",
            ).strip()

        filtered_df = df.copy()
        if view_filter == "Moje zgłoszenia":
            filtered_df = filtered_df[
                (filtered_df["Email"].astype(str).str.lower() == st.session_state.user_email.lower())
                | (filtered_df["Nazwa użytkownika"].astype(str).str.lower() == st.session_state.user_name.lower())
            ]
        elif view_filter == "Otwarte":
            filtered_df = filtered_df[filtered_df["Status"] != "Zamknięte"]
        elif view_filter == "Archiwum":
            filtered_df = filtered_df[filtered_df["Status"] == "Zamknięte"]
        if device_filter != "Wszystkie":
            filtered_df = filtered_df[filtered_df["Urządzenie"] == device_filter]
        if status_filter != "Wszystkie":
            filtered_df = filtered_df[filtered_df["Status"] == status_filter]
        if search_query:
            search_mask = (
                filtered_df["Email"].astype(str).str.contains(search_query, case=False, na=False)
                | filtered_df["Nazwa użytkownika"].astype(str).str.contains(search_query, case=False, na=False)
                | filtered_df["Opis"].astype(str).str.contains(search_query, case=False, na=False)
                | filtered_df["Komentarz"].astype(str).str.contains(search_query, case=False, na=False)
                | filtered_df["Rozwiązanie"].astype(str).str.contains(search_query, case=False, na=False)
            )
            filtered_df = filtered_df[search_mask]

        if sort_filter == "Najstarsze":
            filtered_df = filtered_df.sort_values(by="Data", ascending=True)
        elif sort_filter == "Status A-Z":
            filtered_df = filtered_df.sort_values(by=["Status", "Data"], ascending=[True, False])
        else:
            filtered_df = filtered_df.sort_values(by="Data", ascending=False)

        st.caption(f"Wyświetlane zgłoszenia: {len(filtered_df)} z {total_reports}")

        display_df = filtered_df.copy()
        display_df["Data"] = display_df["Data"].dt.strftime("%Y-%m-%d %H:%M").fillna("-")
        display_df["Data aktualizacji"] = display_df["Data aktualizacji"].dt.strftime("%Y-%m-%d %H:%M").fillna("-")
        display_df["Historia zmian"] = display_df["Historia zmian"].apply(lambda value: len(safe_json_loads(value, [])))
        display_df.index = range(1, len(display_df) + 1)
        st.dataframe(
            display_df,
            use_container_width=True,
            column_config={
                "ID": st.column_config.NumberColumn(
                    "ID",
                    width="small",
                ),
                "Data": st.column_config.TextColumn(
                    "Data",
                    width="medium",
                ),
                "Email": st.column_config.TextColumn(
                    "Email",
                    width="medium",
                ),
                "Nazwa użytkownika": st.column_config.TextColumn(
                    "Nazwa użytkownika",
                    width="medium",
                ),
                "Status": st.column_config.TextColumn(
                    "Status",
                    width="small",
                ),
                "Rozwiązanie": st.column_config.TextColumn(
                    "Rozwiązanie",
                    width="medium",
                ),
                "Historia zmian": st.column_config.NumberColumn(
                    "Historia",
                    width="small",
                ),
                "Komentarz": st.column_config.TextColumn(
                    "Komentarz",
                    width="medium",
                    help="Szersza kolumna dla dłuższych komentarzy do zgłoszeń.",
                ),
                "Opis": st.column_config.TextColumn(
                    "Opis",
                    width="medium",
                ),
                "Urządzenie": st.column_config.TextColumn(
                    "Urządzenie",
                    width="small",
                ),
                "Data aktualizacji": st.column_config.TextColumn(
                    "Data aktualizacji",
                    width="medium",
                ),
            },
            height=420,
        )
        st.caption("Cały rejestr jest widoczny dla wszystkich zalogowanych użytkowników.")

        if filtered_df.empty:
            st.info("Brak zgłoszeń pasujących do wybranych filtrów.")
        else:
            st.markdown("### Edycja zgłoszenia")
            st.caption("Edytować zgłoszenie może tylko jego autor albo administrator.")
            editable_reports = df[
                (df["Email"].astype(str).str.lower() == st.session_state.user_email.lower())
                | (df["Nazwa użytkownika"].astype(str).str.lower() == st.session_state.user_name.lower())
            ].copy()

            if is_staff:
                editable_reports = df.copy()

            if editable_reports.empty:
                st.info("Nie masz uprawnień do edycji zgłoszeń z aktualnie wyświetlanej listy.")
            else:
                edit_options = {
                    f"#{int(row['ID'])} | {row['Urządzenie']} | {row['Nazwa użytkownika']} | "
                    f"{row['Data'].strftime('%Y-%m-%d %H:%M') if pd.notna(row['Data']) else 'brak daty'}": int(row["ID"])
                    for _, row in editable_reports.iterrows()
                }
                selected_label = st.selectbox(
                    "Wybierz zgłoszenie do edycji",
                    list(edit_options.keys()),
                    key="edit_report_select",
                )
                selected_id = edit_options[selected_label]
                selected_report = editable_reports[editable_reports["ID"] == selected_id].iloc[0]

                with st.form(f"edit_report_form_{selected_id}"):
                    edited_status = st.selectbox(
                        "Status zgłoszenia",
                        ["Nowe", "W trakcie", "Zamknięte"],
                        index=["Nowe", "W trakcie", "Zamknięte"].index(str(selected_report["Status"])),
                    )
                    edited_description = st.text_area(
                        "Opis zgłoszenia",
                        value=str(selected_report["Opis"]),
                        height=140,
                    )
                    solution_default = "" if pd.isna(selected_report["Rozwiązanie"]) else str(selected_report["Rozwiązanie"])
                    edited_solution = st.text_area(
                        "Rozwiązanie / podsumowanie",
                        value=solution_default,
                        height=100,
                        help="Przy zamknięciu zgłoszenia wpisz krótki opis rozwiązania.",
                    )
                    edited_comment = st.text_area(
                        "Komentarz / opis dodatkowy",
                        value="" if pd.isna(selected_report["Komentarz"]) else str(selected_report["Komentarz"]),
                        height=120,
                        help="Tutaj admin lub zgłaszający może dopisać uzupełnienia do zgłoszenia.",
                    )
                    save_edit_button = st.form_submit_button("Zapisz zmiany")

                with st.expander("Historia zmian"):
                    st.text(format_history(selected_report["Historia zmian"]))

                if save_edit_button:
                    if not edited_description.strip():
                        st.error("Opis zgłoszenia nie może być pusty.")
                    elif edited_status == "Zamknięte" and not edited_solution.strip():
                        st.error("Przy zamykaniu zgłoszenia podaj rozwiązanie.")
                    else:
                        reports_df = load_reports()
                        report_index = reports_df.index[reports_df["ID"] == selected_id]
                        if len(report_index) == 0:
                            st.error("Nie udało się odnaleźć wskazanego zgłoszenia.")
                        else:
                            idx = report_index[0]
                            previous_status = str(reports_df.at[idx, "Status"])
                            previous_description = str(reports_df.at[idx, "Opis"])
                            previous_comment = str(reports_df.at[idx, "Komentarz"])
                            previous_solution = str(reports_df.at[idx, "Rozwiązanie"])
                            action_parts = []
                            if previous_status != edited_status:
                                action_parts.append(f"Status: {previous_status} -> {edited_status}")
                            if previous_description != edited_description.strip():
                                action_parts.append("Zmieniono opis")
                            if previous_comment != edited_comment.strip():
                                action_parts.append("Zmieniono komentarz")
                            if previous_solution != edited_solution.strip():
                                action_parts.append("Zmieniono rozwiązanie")
                            action_label = ", ".join(action_parts) if action_parts else "Zapisano bez zmian"
                            reports_df.at[idx, "Status"] = edited_status
                            reports_df.at[idx, "Opis"] = edited_description.strip()
                            reports_df.at[idx, "Rozwiązanie"] = edited_solution.strip()
                            reports_df.at[idx, "Historia zmian"] = append_history_entry(
                                reports_df.at[idx, "Historia zmian"],
                                st.session_state.user_name,
                                action_label,
                            )
                            reports_df.at[idx, "Komentarz"] = edited_comment.strip()
                            reports_df.at[idx, "Data aktualizacji"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            save_reports(reports_df)
                            if previous_status != edited_status:
                                notify_ok, notify_message = send_status_change_notification(
                                    reports_df.iloc[idx].to_dict(),
                                    previous_status,
                                    st.session_state.user_name,
                                )
                                if notify_ok:
                                    st.info(notify_message)
                                else:
                                    st.warning(notify_message)
                            st.success("Zmiany w zgłoszeniu zostały zapisane.")
                            st.rerun()
    else:
        st.info("Baza danych jest pusta. Dodaj pierwsze zgłoszenie.")


st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#666; padding:0.5rem 0;'>© 2026 Panel zgłoszeniowy awarii</div>",
    unsafe_allow_html=True,
)
