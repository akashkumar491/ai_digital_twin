# AI Digital Twin

Streamlit chat app answering questions from a LinkedIn profile summary, backed by OpenRouter.

## Local dev

```bash
uv sync
cp .env.example .env   # or copy .streamlit/secrets.toml.example to .streamlit/secrets.toml
streamlit run app.py
```

Required secrets: `OPENROUTER_API_KEY`, `PUSHOVER_APP_TOKEN`, `PUSHOVER_USER_KEY`.

## Streamlit Cloud deploy

1. Push repo to GitHub.
2. Create app on share.streamlit.io pointing at `app.py`.
3. In app Settings > Secrets, paste:

```toml
OPENROUTER_API_KEY = "sk-or-..."
PUSHOVER_APP_TOKEN = "..."
PUSHOVER_USER_KEY = "..."
```

4. Deploy. `Profile.pdf` must stay in repo root.