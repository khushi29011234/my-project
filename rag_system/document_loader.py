# rag_system/document_loader.py
# LlamaIndex thi badha docs + source code load kare
# Main plugin + Extensions + XLSX + PDF support

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
                    '.html', '.json',
                    '.md', '.txt'
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
    Documentation load kare
    Supported formats:
    - .docx  — Word documents
    - .pdf   — PDF files (NEW)
    - .xlsx  — Excel files (NEW)
    - .txt   — Plain text
    - .md    — Markdown
    - .csv   — CSV data
    - .html  — HTML pages
    - .json  — JSON data
    - .pptx  — PowerPoint
    - .rst   — ReStructuredText
    - .xml   — XML files

    Default paths:
    - data               (main docs)
    - data/extensions_docx  (extension docs)

    Future ma navo type add karvo hoy to:
    supported_exts list ma j add karo
    """
    if paths is None:
        paths = [
            "data",
            "data/extensions_docx",
        ]

    # Future ma navo format aave to
    # sirf yahan add karo — bija koi change nahi
    supported_exts = [
        '.docx',   # Word — woo_project.docx etc.
        '.pdf',    # PDF — sp_tableview_setup_guide.pdf
        '.xlsx',   # Excel — issue_solutions.xlsx etc.
        '.txt',    # Plain text
        '.md',     # Markdown
        '.csv',    # CSV data
        '.html',   # HTML pages
        '.json',   # JSON data
        '.pptx',   # PowerPoint
        '.rst',    # ReStructuredText
        '.xml',    # XML files
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
                required_exts=supported_exts
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