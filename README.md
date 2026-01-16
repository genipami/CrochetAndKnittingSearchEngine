🧶 Crochet & Knitting Pattern Search Engine
A multimodal information retrieval system for PDF-based craft patterns
📌 Overview
The Crochet & Knitting Search Engine is an end‑to‑end information retrieval system designed to index, analyze, and retrieve crochet and knitting patterns from a large collection of PDF files.
The project focuses on applying:

✔ Information Retrieval (IR)
✔ Natural Language Processing (NLP)
✔ Text extraction from PDF patterns
✔ Embeddings & vector similarity search
✔ Basic classification / pattern type detection

…all toward solving a very real problem for crafters:
How do you quickly find patterns that match a stitch, yarn, or design style in a huge personal collection?
This project was built as part of my Master's degree coursework in Information Retrieval and Natural Language Processing, and it reflects both academic concepts and personal interest (crochet is my hobby ♡).

✨ Key Features
🧵 1. PDF Pattern Ingestion

Handles hundreds to thousands of crochet/knitting PDF files.
Extracts both text and images.
Cleans, preprocesses, and structures extracted content.

📚 2. NLP & Text Processing

Tokenization & normalization
Stopword removal
Sentence segmentation
Optional chunking (for better embedding quality)

🧠 3. Embedding Generation
Supports multiple embedding models (depending on your environment):

Sentence Transformers
OpenAI / Azure embeddings
HuggingFace models

Embeddings are stored locally for fast search.
🔍 4. Semantic Search Engine
Users can search patterns by:

Stitch type
Craft name
Technique
Yarn weight
Keywords
Description
Even partial phrases

Similarity search returns the most relevant patterns.
🏷 5. Pattern Metadata Extraction (Optional)
Using heuristics or ML-based techniques to identify:

Crochet vs Knitting
Pattern difficulty
Materials
Hook/needle size
Pattern structure

🌐 6. Clean, Small Git Repo + Data in Releases
All PDFs are stored in a GitHub Release instead of Git or Git LFS.
