"""
PDF WORD FREQUENCY ANALYZER
===========================

PURPOSE
-------
Extracts text from a PDF, removes one-letter words and words
found in an optional reference list, counts the remaining words,
calculates their frequency percentages, and exports everything
to a CSV spreadsheet.

REQUIREMENTS
------------
Python 3.9 or newer
pypdf

INSTALLATION
------------
python -m pip install pypdf

EXAMPLES
--------
Basic analysis:
python pdf_word_frequency.py "document.pdf"

Analysis with reference list:
python pdf_word_frequency.py "document.pdf" -r "common_words.txt"

Custom CSV filename:
python pdf_word_frequency.py "document.pdf" -r "common_words.txt" -o "results.csv"

REFERENCE FILE
--------------
A UTF-8 text file containing words to exclude.
Words can be separated by spaces or placed on separate lines.
Capitalization and surrounding punctuation are ignored.
"""

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

from pypdf import PdfReader


# ---------------------------------------------------------
# SECTION 1: WORD RECOGNITION
# ---------------------------------------------------------

# Recognizes Unicode words and allows internal apostrophes.
# Examples: "hello", "café", "don't".
# Numbers and underscores are excluded.

WORD_PATTERN = re.compile(
    r"[^\W\d_]+(?:['’][^\W\d_]+)*",
    re.UNICODE
)


def get_words(text: str) -> list[str]:
    """
    Extract individual words from text.

    Converts all words to lowercase using casefold().
    This ensures that Python, PYTHON and python
    are treated as the same word.
    """

    return [
        match.group(0).casefold()
        for match in WORD_PATTERN.finditer(text)
    ]


# ---------------------------------------------------------
# SECTION 2: EXTRACT TEXT FROM PDF
# ---------------------------------------------------------

def extract_pdf_text(pdf_path: Path) -> str:
    """
    Opens a PDF and extracts text from every page.

    Returns all extracted text as one string.
    """

    try:
        reader = PdfReader(str(pdf_path))

    except Exception as exc:
        raise RuntimeError(
            f"Could not open PDF: {exc}"
        ) from exc

    # Attempt to open PDFs encrypted with an empty password.
    if reader.is_encrypted:

        try:
            if reader.decrypt("") == 0:
                raise RuntimeError(
                    "PDF is password-protected. "
                    "Unlock it before running the script."
                )

        except Exception as exc:
            raise RuntimeError(
                "Could not open encrypted PDF."
            ) from exc

    extracted_pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        try:
            extracted_pages.append(
                page.extract_text() or ""
            )

        except Exception as exc:
            raise RuntimeError(
                f"Could not extract page {page_number}: {exc}"
            ) from exc

    return "\n".join(extracted_pages)


# ---------------------------------------------------------
# SECTION 3: LOAD REFERENCE WORD LIST
# ---------------------------------------------------------

def load_reference_words(reference_path: Path) -> set[str]:
    """
    Loads an external text file containing words to exclude.

    The reference file can contain:
        One word per line
        Multiple words separated by spaces

    Returns:
        A set of normalized words.

    A set is used because it makes checking whether a word
    exists in the reference list efficient.
    """

    if not reference_path.is_file():
        raise RuntimeError(
            f"Reference file not found: {reference_path}"
        )

    try:
        reference_text = reference_path.read_text(
            encoding="utf-8-sig"
        )

    except (OSError, UnicodeError) as exc:
        raise RuntimeError(
            f"Could not read reference file: {exc}"
        ) from exc

    # Normalize reference words in exactly the same way
    # as words extracted from the PDF.
    return set(get_words(reference_text))


# ---------------------------------------------------------
# SECTION 4: FILTER AND COUNT WORDS
# ---------------------------------------------------------

def count_filtered_words(
    text: str,
    excluded_words: set[str]
) -> tuple[Counter, int, int]:
    """
    Filters and counts words extracted from the PDF.

    FILTER 1:
        Removes every one-letter word.

    FILTER 2:
        Removes every word found in the reference list.

    Returns:
        word_counts:
            Counter containing the remaining words.

        original_word_total:
            Total recognized words before filtering.

        removed_word_total:
            Total word occurrences removed by filtering.
    """

    all_words = get_words(text)

    # Apply both filters.
    kept_words = [
        word
        for word in all_words
        if len(word) > 1
        and word not in excluded_words
    ]

    # Count the remaining words.
    word_counts = Counter(kept_words)

    removed_word_total = (
        len(all_words) - len(kept_words)
    )

    return (
        word_counts,
        len(all_words),
        removed_word_total
    )


# ---------------------------------------------------------
# SECTION 5: EXPORT RESULTS TO CSV
# ---------------------------------------------------------

def save_results(
    word_counts: Counter,
    output_path: Path
) -> int:
    """
    Creates a CSV containing:

        Word
        Count
        Frequency (%)

    Percentages are calculated using the total number
    of words remaining AFTER filtering.

    Results are sorted from most frequent to least frequent.
    """

    total_words = sum(word_counts.values())

    try:

        with output_path.open(
            "w",
            newline="",
            encoding="utf-8-sig"
        ) as csv_file:

            writer = csv.writer(csv_file)

            # CSV column headings.
            writer.writerow([
                "Word",
                "Count",
                "Frequency (%)"
            ])

            # Sort by frequency, then alphabetically.
            sorted_words = sorted(
                word_counts.items(),
                key=lambda item: (
                    -item[1],
                    item[0]
                )
            )

            for word, count in sorted_words:

                percentage = (
                    count / total_words * 100
                    if total_words
                    else 0.0
                )

                writer.writerow([
                    word,
                    count,
                    f"{percentage:.6f}"
                ])

    except OSError as exc:
        raise RuntimeError(
            f"Could not write CSV: {exc}"
        ) from exc

    return total_words


# ---------------------------------------------------------
# SECTION 6: MAIN PROGRAM
# ---------------------------------------------------------

def main() -> int:
    """
    Coordinates the complete PDF analysis process.

    1. Reads the PDF filename.
    2. Reads the optional reference filename.
    3. Checks that the input files exist.
    4. Extracts PDF text.
    5. Removes unwanted words.
    6. Counts the remaining words.
    7. Calculates frequency percentages.
    8. Exports the CSV.
    9. Displays a completion summary.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Analyze PDF word frequencies with "
            "one-letter and reference-list filtering."
        )
    )

    # Required PDF input.
    parser.add_argument(
        "pdf",
        help="Path to the PDF file."
    )

    # Optional reference list.
    parser.add_argument(
        "-r",
        "--exclude-words",
        help=(
            "Optional text file containing words "
            "that should be excluded."
        )
    )

    # Optional output filename.
    parser.add_argument(
        "-o",
        "--output",
        help=(
            "CSV output filename. "
            "Defaults to the PDF filename."
        )
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf).expanduser()

    # Verify PDF exists.
    if not pdf_path.is_file():

        print(
            f"PDF not found: {pdf_path}",
            file=sys.stderr
        )

        return 1

    if pdf_path.suffix.lower() != ".pdf":

        print(
            "Input must be a PDF file.",
            file=sys.stderr
        )

        return 1

    # Determine output filename.
    output_path = (
        Path(args.output).expanduser()
        if args.output
        else pdf_path.with_name(
            f"{pdf_path.stem}_word_frequency.csv"
        )
    )

    try:

        # Load reference words if provided.
        excluded_words = set()

        if args.exclude_words:

            excluded_words = load_reference_words(
                Path(args.exclude_words).expanduser()
            )

        # Extract PDF text.
        pdf_text = extract_pdf_text(pdf_path)

        # Filter and count words.
        (
            word_counts,
            original_total,
            removed_total
        ) = count_filtered_words(
            pdf_text,
            excluded_words
        )

        if not word_counts:

            print(
                "No words remain after filtering. "
                "Check the PDF and reference list.",
                file=sys.stderr
            )

            return 1

        # Export CSV.
        remaining_total = save_results(
            word_counts,
            output_path
        )

    except (OSError, RuntimeError) as exc:

        print(
            f"Error: {exc}",
            file=sys.stderr
        )

        return 1

    # Display completion information.
    print("\nAnalysis complete!")

    print(
        f"Words recognized before filtering: {original_total}"
    )

    print(
        f"Word occurrences removed: {removed_total}"
    )

    print(
        f"Words remaining: {remaining_total}"
    )

    print(
        f"Unique words remaining: {len(word_counts)}"
    )

    print(
        f"Reference words loaded: {len(excluded_words)}"
    )

    print(
        f"CSV saved to: {output_path.resolve()}"
    )

    return 0


# ---------------------------------------------------------
# SECTION 7: START PROGRAM
# ---------------------------------------------------------

if __name__ == "__main__":
    raise SystemExit(main())
