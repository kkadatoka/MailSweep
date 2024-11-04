# CleanMail

A tool to quickly clean up your email inbox!

## Demo

<https://github.com/user-attachments/assets/b52220a0-b69e-4dcb-8eb2-f1bbe472d536>

## How to run

1. install uv (if you don't have it)

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

   Make sure you follow the instructions once the installation completes.

1. install dependencies with uv

   ```bash
   uv sync
   ```

1. activate the virtual environment

   ```bash
   source .venv/bin/activate
   ```

1. run streamlit app:

   ```bash
   streamlit run main.py`
   ```

If you are self hosting it yourself, there is a dockerfile as well.

That's it!
