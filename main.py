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

    with st.form("cleanup_form", border=False):
        # Create display columns with cleanup checkbox as first column
        display_df = df[["Sender Name", "Email", "Unsubscribe Link"]].copy()
        display_df["should_clean_up"] = False
        # Reorder columns to put checkbox first
        display_df = display_df[
            ["should_clean_up", "Sender Name", "Email", "Unsubscribe Link"]
        ]

        # Create the interactive dataframe
        edited_df = st.data_editor(
            display_df,
            column_config={
                "should_clean_up": st.column_config.CheckboxColumn(
                    "Clean up?",
                    help="Select to clean up emails from this sender",
                    default=False,
                ),
                "Unsubscribe Link": st.column_config.LinkColumn(
                    "Unsubscribe link",
                    help="Click to unsubscribe",
                    display_text="🔗 Unsubscribe",
                    validate="https?://.*",
                ),
            },
            hide_index=True,
            use_container_width=True,
            height=500,
        )

        if st.form_submit_button("🧹 Clean Selected Emails", use_container_width=True):
            sender_ids_to_be_cleaned = {
                row["Email"]
                for _, row in edited_df.iterrows()
                if row["should_clean_up"]
            }
            if not sender_ids_to_be_cleaned:
                st.toast("No senders selected for cleanup!")
            else:
                st.write(
                    f"Cleaning up emails from: {', '.join(sender_ids_to_be_cleaned)}"
                )
                st.toast(
                    "This may take a while depending on the number of emails. Please be patient!"
                )
                analyzer = GmailAnalyzer(
                    st.session_state.email_address, st.session_state.app_password
                )
                # TODO: move to bulk delete
                for sender in sender_ids_to_be_cleaned:
                    deleted_count = analyzer.delete_emails_from_sender(sender)
                    st.toast(f"Moved {deleted_count} emails from {sender} to the bin!")
                st.session_state.email_data = None
                st.rerun()


def email_cleanup_component():
    analyzer = GmailAnalyzer(
        st.session_state.email_address, st.session_state.app_password
    )
    # Show "Analyze Emails" button only if sender_stats is not populated
    if st.session_state.email_data is None:
        analyze_emails_component(analyzer)
        return

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

    # Sidebar for authentication
    sidebar_component()

    # Title row with refresh button
    title_col, reset_col = st.columns([7, 1])
    with title_col:
        st.title("CleanMail")
    with reset_col:
        if st.button("🔄 Reset", use_container_width=True):
            st.session_state.email_data = None
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
