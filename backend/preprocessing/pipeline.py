from backend.preprocessing.extractor import run as extract
from backend.preprocessing.cleaner import run as clean
from backend.preprocessing.chunker import run as chunk
from backend.preprocessing.vector_builder import run as build


def run():

    print("\n========================================")
    print("NyayaAI Preprocessing Pipeline")
    print("========================================\n")

    extract()

    clean()

    chunk()

    build()

    print("\n========================================")
    print("Preprocessing Completed Successfully")
    print("========================================")


if __name__ == "__main__":
    run()