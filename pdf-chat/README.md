# Chat with your PDF

Upload a PDF, ask questions, and get answers only from that PDF, with page numbers.
Built with LangChain, Streamlit and FAISS, using Gemini models through OpenRouter.

## Files

- `rag.py`: the core. It loads the PDF, splits it into chunks, embeds them into FAISS, and answers with page numbers. Run `python rag.py` to test it in the terminal.
- `app.py`: the Streamlit UI (upload + chat). It imports `build_store` and `ask` from `rag.py`.

## Run it

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then put your OpenRouter key in .env
streamlit run app.py
```

Get a key at https://openrouter.ai/keys.

Demo PDF: the US Department of Energy's Energy Saver Guide (public domain):
https://www.energy.gov/sites/default/files/2022-08/energy-saver-guide-2022.pdf
