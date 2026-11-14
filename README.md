# PDF Word Frequency Analyzer

A Python tool for extracting, analyzing, and calculating word frequencies in PDF documents.

The program uses **PyPDF** to extract text from PDF files, filters out unwanted words, calculates the frequency of each remaining word, and exports the results into a CSV file.

It also supports an external reference word list, allowing users to exclude common words (such as the 1,000 most frequently used words in a language) from their analysis.

## Features

- **PDF Text Extraction:** Extracts text from all pages of a PDF document using PyPDF.
- **Word Frequency Analysis:** Counts the occurrences of every individual word.
- **Case-Insensitive Processing:** Treats uppercase and lowercase versions of the same word as identical.
- **One-Letter Word Filtering:** Automatically removes all words consisting of only one letter.
- **Custom Reference Word List:** Excludes words found in an external `.txt` file.
- **Frequency Calculation:** Calculates the percentage of the total remaining words represented by each word.
- **CSV Export:** Saves the results in a spreadsheet-compatible CSV file.
- **Frequency Sorting:** Sorts results from most frequent to least frequent.
- **Processing Statistics:** Reports the original word count, number of removed occurrences, remaining word count, and number of unique words.

## Requirements

- Python 3.9 or newer
- PyPDF

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/pdf-word-frequency-analyzer.git
```

Navigate to the project directory:

```bash
cd pdf-word-frequency-analyzer
```

Install the required dependency:

```bash
python -m pip install pypdf
```

## Project Structure

```text
pdf-word-frequency-analyzer/
│
├── pdf_word_frequency.py
├── common_words.txt
├── README.md
└── .gitignore
```

`pdf_word_frequency.py` contains the main program.

`common_words.txt` is an optional reference file containing words that should be excluded from the analysis.

## Usage

### 1. Basic PDF Analysis

To analyze a PDF without using an external reference list:

```bash
python pdf_word_frequency.py "document.pdf"
```

The program automatically creates a CSV file named:

```text
document_word_frequency.csv
```

### 2. Analysis With a Reference Word List

To exclude common words using an external reference file:

```bash
python pdf_word_frequency.py "document.pdf" -r "common_words.txt"
```

The reference file can contain words separated by spaces or placed on separate lines.

Example:

```text
the
and
of
to
in
is
that
it
was
for
on
with
as
```

Every word found in this reference list will be excluded from the PDF analysis.

The comparison is case-insensitive and uses complete-word matching.

For example, excluding `the` will remove `the` but will not remove `there` or `theory`.

### 3. Specify a Custom Output Filename

You can specify the name and location of the generated CSV file using `-o`:

```bash
python pdf_word_frequency.py "document.pdf" -r "common_words.txt" -o "analysis_results.csv"
```

### Command-Line Arguments

| Argument | Description | Required |
|---|---|---|
| `pdf` | PDF document to analyze | Yes |
| `-r`, `--exclude-words` | Reference text file containing excluded words | No |
| `-o`, `--output` | Custom CSV output filename | No |

## How Word Filtering Works

The program applies two filters before calculating word frequencies.

### Filter 1: Remove One-Letter Words

All words consisting of only one letter are removed.

Examples:

| Original word | Result |
|---|---|
| a | Removed |
| I | Removed |
| x | Removed |
| cat | Kept |
| book | Kept |
| research | Kept |

### Filter 2: Remove Reference Words

The program compares the extracted words against the external reference list.

Any matching word is excluded from the analysis.

For example, if the reference list contains:

```text
the
and
with
```

These words will be removed from the PDF, regardless of capitalization.

Words that are not present in the reference list remain in the analysis.

## Frequency Calculation

Word frequencies are calculated using the following formula:

**Frequency (%) = (Word Occurrences / Total Remaining Words) × 100**

For example, assume a document contains 1,000 words after filtering.

The word `research` appears 50 times.

Its frequency is:

```text
(50 / 1000) * 100 = 5%
```

The resulting CSV entry would be:

| Word | Count | Frequency (%) |
|---|---:|---:|
| research | 50 | 5.000000 |

Importantly, percentages are calculated using the total word count **after filtering**, not the original PDF word count.

## CSV Output

The generated CSV contains three columns:

| Column | Description |
|---|---|
| Word | The individual word |
| Count | Number of occurrences in the PDF |
| Frequency (%) | Percentage of total remaining words |

Results are sorted by frequency in descending order.

The CSV uses UTF-8 encoding with a BOM to improve compatibility with spreadsheet applications such as Microsoft Excel.

## Processing Summary

After completing the analysis, the program displays a summary containing:

- Total words recognized before filtering.
- Number of word occurrences removed.
- Total words remaining after filtering.
- Number of unique words remaining.
- Number of unique reference words loaded.
- Location of the generated CSV file.

## Limitations

- **Scanned PDFs:** PyPDF extracts existing text but does not perform OCR. Scanned documents containing only images require OCR processing before analysis.
- **Encrypted PDFs:** The program attempts to open PDFs encrypted with an empty password. Other password-protected documents must be unlocked first.
- **Word Recognition:** Punctuation is ignored, and apostrophes within words are supported. Hyphenated expressions are treated as separate words.
- **Numbers:** Numeric values and standalone numbers are not included in word counts.
- **Language Processing:** The program does not perform stemming, lemmatization, or semantic analysis. Different forms of a word are counted separately.

## Potential Future Improvements

Possible extensions include:

- Support for multiple reference lists.
- Automatic language detection.
- Integration of language-specific stop-word databases.
- OCR support for scanned PDFs.
- Stemming and lemmatization.
- Batch processing of multiple PDF files.
- Additional statistical analysis, including word frequency distributions.
- Exporting results to Excel format.
- Graphical visualization of the most frequent words.

## License

This project is open source. Add a license file to the repository to specify the terms under which others may use, modify, and distribute the code.

## Author

Developed as a Python-based text analysis project focused on extracting and analyzing vocabulary from PDF documents.