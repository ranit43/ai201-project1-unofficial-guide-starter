import os
from html import escape

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import gradio as gr
from ingest import build_chunks, load_documents
from retriever import embed_and_store, retrieve, get_collection
from generator import generate_response


# ---------------------------------------------------------------------------
# Ingestion - runs once on startup
# ---------------------------------------------------------------------------

def run_ingestion():
    """
    Load UCLA dining documents, chunk them, and store them in ChromaDB.

    If the vector store is already populated, ingestion is skipped.
    To re-ingest (e.g. after changing your chunking strategy), delete the
    ./chroma_db folder and restart the app.
    """
    collection = get_collection()

    if collection.count() > 0:
        print(
            f"Vector store already populated ({collection.count()} chunks). "
            "Skipping ingestion."
        )
        print("To re-ingest, delete the ./chroma_db folder and restart.")
        return

    print("Ingesting UCLA dining documents...")
    all_chunks = build_chunks()

    if all_chunks:
        embed_and_store(all_chunks)
        print(f"Ingestion complete. {len(all_chunks)} chunks stored.")
    else:
        print(
            "\nNo chunks produced. Make sure ingest.py can load the UCLA dining corpus.\n"
            "The app will start, but it will not be able to answer questions yet.\n"
        )


# ---------------------------------------------------------------------------
# Chat handler
# ---------------------------------------------------------------------------

def chat(message, history):
    if not message.strip():
        return ""
    retrieved = retrieve(message)
    return generate_response(message, retrieved)


def loaded_sources_html():
    """Render the loaded source list from the current document corpus."""
    documents = load_documents()
    if documents:
        source_items = "\n".join(
            (
                "<li style='margin-bottom:0.45rem;'>"
                f"<span style='color:#0f172a; font-weight:650;'>{escape(doc['title'])}</span>"
                f"<br><span style='color:#334155; font-size:0.78rem;'>"
                f"{escape(doc.get('publication') or doc.get('filename') or 'Source')}"
                "</span></li>"
            )
            for doc in documents
        )
    else:
        source_items = (
            "<li style='color:#0f172a; font-weight:650;'>No source documents found.</li>"
        )

    return f"""
        <div style="background:#ffffff; border:1px solid #64748b;
                    border-radius:8px; padding:1rem; margin-top:0.5rem;">
            <p style="font-size:0.95rem; font-weight:800; color:#0f172a;
                       margin:0 0 0.65rem;">
                LOADED SOURCES
            </p>
            <ul style="font-size:0.9rem; color:#0f172a; padding-left:1.05rem;
                        margin:0; line-height:1.45; font-weight:600;">
                {source_items}
            </ul>
            <hr style="border:none; border-top:1px solid #cbd5e1; margin:0.85rem 0;">
            <p style="font-size:0.82rem; color:#1f2937; margin:0; line-height:1.55;">
                Answers use retrieved chunks only and append source titles and URLs.
                If the answer is not in the corpus, the app should say so.
            </p>
        </div>
    """


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

with gr.Blocks(
    title="The Unofficial UCLA Dining Guide",
) as demo:

    gr.HTML("""
        <div style="padding:1.1rem 0 0.6rem;">
            <h1 style="font-size:1.8rem; font-weight:700; color:#0f766e; margin:0;">
                The Unofficial UCLA Dining Guide
            </h1>
            <p style="color:#475569; font-size:1rem; margin:0.35rem 0 0;">
                Ask student-facing questions about UCLA dining halls, meal plans,
                wait times, food trucks, and dining tradeoffs.
            </p>
        </div>
    """)

    with gr.Row():
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat,
                chatbot=gr.Chatbot(
                    height=440,
                    placeholder=(
                        "<div style='text-align:center; color:#64748b; margin-top:3rem;'>"
                        "Ask a UCLA dining question to get started."
                        "</div>"
                    ),
                ),
                textbox=gr.Textbox(
                    placeholder='e.g. "What makes Bruin Plate good for healthy eating?"',
                    container=False,
                    scale=7,
                ),
                examples=[
                    "What makes Bruin Plate a good option for healthy eating or dietary restrictions?",
                    "How do Regular and Premium meal plans differ?",
                    "When are UCLA dining halls usually busiest?",
                    "What recent dining problems involved strikes, mobile ordering, and food trucks?",
                    "What do the sources say about The Study at Hedrick?",
                    "How much does a 14P meal plan cost in dollars per quarter?",
                ],
                cache_examples=False,
            )

        with gr.Column(scale=1, min_width=180):
            gr.HTML(loaded_sources_html())


if __name__ == "__main__":
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "8502"))
    print("\n" + "="*50)
    print("  The Unofficial UCLA Dining Guide - starting up")
    print("="*50 + "\n")
    run_ingestion()
    demo.launch(
        server_port=server_port,
        theme=gr.themes.Soft(primary_hue="teal", neutral_hue="slate"),
    )
