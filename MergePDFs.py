#!/usr/bin/env python3
from pypdf import PdfMerger
import argparse


def PDF_merger(FileList, NewFileName):
    """
    Enter pdfs as a list e.g.  ["1.pdf", "2.pdf"]
    Enter NewFileName e.g. "Combined.pdf"

    Note these require correct path to folder.
    """
    merger = PdfMerger()
    for pdf in FileList:
        merger.append(pdf)
    merger.write(NewFileName)
    merger.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge PDF files into a single PDF.")
    parser.add_argument("files", nargs="+", help="List of PDF files to merge.")
    parser.add_argument("output", help="Output file name for the merged PDF.")
    args = parser.parse_args()

    PDF_merger(args.files, args.output)
    print(f"Merged {len(args.files)} PDF files into {args.output}.")
