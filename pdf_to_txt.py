import pdfplumber
import pathlib
from nltk.tokenize import sent_tokenize
import nltk
nltk.download('punkt')
nltk.download('stopwords')

ROOT_DIR = pathlib.Path(".").resolve()
PDF_DIR = ROOT_DIR / "pdfs"
TXT_DIR = ROOT_DIR / "txts"
TXT_DIR.mkdir(parents=True, exist_ok=True)



def turn_pdfs_to_txts() -> None:
    files = sorted(PDF_DIR.glob("*.pdf"))
    print(f"[INFO] Found {len(files)} pdf files in {PDF_DIR}.")
    for i, file in enumerate(files, start=1):
        new_path = TXT_DIR / (file.stem + ".txt")
        with pdfplumber.open(file) as pdf, open(new_path, "w", encoding="utf-8") as f:
            try:
                for page in pdf.pages:
                    t = page.extract_text()
                    if isinstance(t, str):
                        f.write(t + '\n')
                print(f"[{i}/{len(files)}] Turned into txt!")     
            except:
                print(f"ERROR: document {file}")

    print(f"PDF conversion complete!")


def main():
    turn_pdfs_to_txts()

if __name__ == "__main__":
    main()
