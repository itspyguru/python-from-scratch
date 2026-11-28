# Chat with any PDF in 16 lines

A Streamlit app: upload a PDF, ask questions, and Gemini (through OpenRouter) answers only from that PDF.

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENROUTER_API_KEY=your-key-here
streamlit run app.py
```

Try it with Python's style guide (PEP 8): "Tabs or spaces?" or "How long should a line be?".
The whole PDF goes into the prompt, so it suits documents that fit the model's context window.
