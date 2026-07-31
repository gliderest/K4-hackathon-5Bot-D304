"""CLI scaffold: ingest slide PDF và transcript thành chunks JSONL."""

from pathlib import Path


def main() -> None:
    data_root = Path("data/vlearn-pack")
    output_dir = Path("data/processed/chunks")
    raise NotImplementedError(
        f"Implement ingestion from {data_root} to {output_dir} using backend.app.rag.ingestion"
    )


if __name__ == "__main__":
    main()

