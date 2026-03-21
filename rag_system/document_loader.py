# rag_system/document_loader.py
# LlamaIndex thi badha docs + source code load kare
# Main plugin + Extensions banne support kare

import os
from llama_index.core import SimpleDirectoryReader


def load_source_code(paths=None):
    """
    Source code load kare — PHP, JS, CSS, etc.
    Main plugin + Extensions banne
    BMAD agent scan karva mate

    Default paths:
    - data/woo-bundle-choice  (main plugin)
    - data/extensions_source_code  (extensions)
    """
    if paths is None:
        paths = [
            "data/woo-bundle-choice",
            "data/extensions_source_code"
        ]

    all_docs = []

    for path in paths:
        if not os.path.exists(path):
            print(f"⚠️ Path not found: {path}")
            continue

        try:
            reader = SimpleDirectoryReader(
                input_dir=path,
                recursive=True,
                required_exts=[
                    '.php', '.js', '.css',
                    '.html', '.json', '.md', '.txt'
                ]
            )
            docs = reader.load_data()
            print(
                f"✅ Source code loaded: "
                f"{len(docs)} files from {path}"
            )
            all_docs.extend(docs)

        except Exception as e:
            print(
                f"⚠️ Source code loading error "
                f"({path}): {e}"
            )

    print(
        f"✅ Total source code: "
        f"{len(all_docs)} files"
    )
    return all_docs


def load_documentation(paths=None):
    """
    Documentation load kare — DOCX, PDF, TXT
    Main docs + Extension docs banne
    RAG (txtai) layer mate

    Default paths:
    - data  (main docs — woo_project.docx etc.)
    - data/extensions_docx  (extension docs)
    """
    if paths is None:
        paths = [
            "data",
            "data/extensions_docx"
        ]

    all_docs = []

    for path in paths:
        if not os.path.exists(path):
            print(f"⚠️ Path not found: {path}")
            continue

        try:
            reader = SimpleDirectoryReader(
                input_dir=path,
                recursive=False,
                required_exts=[
                    '.docx', '.pdf', '.txt'
                ]
            )
            docs = reader.load_data()
            print(
                f"✅ Documentation loaded: "
                f"{len(docs)} files from {path}"
            )
            all_docs.extend(docs)

        except Exception as e:
            print(
                f"⚠️ Documentation loading error "
                f"({path}): {e}"
            )

    print(
        f"✅ Total documentation: "
        f"{len(all_docs)} files"
    )
    return all_docs