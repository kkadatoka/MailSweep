import streamlit as st
from gmail_client import GmailAnalyzer


def analyze_emails_component(analyzer):
    if st.button("Analyze Emails"):
        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current, total):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Processing email {current}/{total}")

        st.session_state.email_data = analyzer.get_sender_statistics(
            st.session_state.max_emails, progress_callback=update_progress
        )

        progress_bar.empty()
        status_text.empty()
        st.rerun()


@st.fragment
def sender_list_for_cleanup_component():
    df = st.session_state.email_data

    # Group by sender and create cards
    for index, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([4, 1], gap="large")

            with col1:
                st.subheader(row["Sender Name"], anchor=False)
                st.caption(row["Email"])

            with col2:
                is_queued = row["Email"] in st.session_state.senders_to_be_cleaned
                if st.checkbox(
                    "Queue for deletion",
                    value=is_queued,
                    key=f"delete_{index}",
                ):
                    st.session_state.senders_to_be_cleaned.add(row["Email"])
                else:
                    st.session_state.senders_to_be_cleaned.discard(row["Email"])
                if row["Unsubscribe Link"]:
                    st.markdown(f"[Unsubscribe]({row['Unsubscribe Link']})")

            st.divider()


def email_cleanup_component():
    analyzer = GmailAnalyzer(
        st.session_state.email_address, st.session_state.app_password
    )
    # Show "Analyze Emails" button only if sender_stats is not populated
    if st.session_state.email_data is None:
        analyze_emails_component(analyzer)

    # Always show the grouped view if email_data is present
    if st.session_state.email_data is not None:
        sender_list_for_cleanup_component()


def sidebar_component():
    st.sidebar.header("Authentication")

    with st.sidebar:
        st.session_state.email_address = st.text_input(
            "Gmail Address", value=st.session_state.email_address, type="default"
        )
        st.session_state.app_password = st.text_input(
            "Gmail App Password", value=st.session_state.app_password, type="password"
        )
        st.session_state.max_emails = st.number_input(
            "Maximum emails to analyze",
            min_value=10,
            max_value=1000,
            value=st.session_state.max_emails,
            step=10,
        )

        if st.button("Connect"):
            if st.session_state.email_address and st.session_state.app_password:
                analyzer = GmailAnalyzer(
                    st.session_state.email_address, st.session_state.app_password
                )
                test_conn = analyzer.connect()
                if test_conn:
                    test_conn.logout()
                    st.success("Successfully connected to Gmail!")
                    st.rerun()

        # Add a button to star the repository
        st.sidebar.markdown(
            """
            ---
            ⭐️ [Star this project on GitHub](https://github.com/BharatKalluri/cleanmail)
            
            🔗 [bharatkalluri.com](https://bharatkalluri.com)
            """
        )


def main():
    st.set_page_config(page_title="CleanMail", layout="wide")

    # Use session state to store email credentials and sender stats
    if "email_address" not in st.session_state:
        st.session_state.email_address = None
    if "app_password" not in st.session_state:
        st.session_state.app_password = None
    if "max_emails" not in st.session_state:
        st.session_state.max_emails = 1000
    if "email_data" not in st.session_state:
        st.session_state.email_data = None
    if "senders_to_be_cleaned" not in st.session_state:
        st.session_state.senders_to_be_cleaned = set()

    # Sidebar for authentication
    sidebar_component()

    # Title row with clean and refresh buttons
    title_col, clean_col, reset_col = st.columns([6, 1, 1])
    with title_col:
        st.title("CleanMail")
    with clean_col:
        if st.button("🧹 Clean", use_container_width=True):
            if not st.session_state.senders_to_be_cleaned:
                st.toast("No senders selected for cleanup!")
            else:
                st.toast(
                    f"{len(st.session_state.senders_to_be_cleaned)} senders' emails are queued to be cleaned. Starting now!"
                )
                st.toast(
                    "This may take a while depending on the number of emails. Please be patient!"
                )
                analyzer = GmailAnalyzer(
                    st.session_state.email_address, st.session_state.app_password
                )
                for sender in st.session_state.senders_to_be_cleaned:
                    deleted_count = analyzer.delete_emails_from_sender(sender)
                    st.toast(f"Moved {deleted_count} emails from {sender} to the bin!")
                st.session_state.senders_to_be_cleaned.clear()
                st.session_state.email_data = None
                st.rerun()
    with reset_col:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.email_data = None
            st.session_state.senders_to_be_cleaned.clear()
            st.rerun()

    if st.session_state.email_address and st.session_state.app_password:
        email_cleanup_component()
    else:
        st.info("Please authenticate using your Gmail credentials in the sidebar.")
        st.markdown(
            """
        ### Instructions:
        1. Enter your Gmail address
        2. Enter your [Gmail App Password](https://myaccount.google.com/apppasswords)
        3. Select the number of recent emails to analyze
        4. Click Connect to start analyzing your inbox
        
        **Note:** This app requires a Gmail App Password, not your regular Gmail password!
        [Learn how to create an App Password](https://support.google.com/accounts/answer/185833)
        """
        )


if __name__ == "__main__":
    main()
