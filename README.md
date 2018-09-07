# bibtex2html

This tool converts a bibtex file or a folder with multiple bibtex files into an HTML bibliography.

## Compatibility

The tool has been written for Ubuntu and tested on Python v3.5 and above but is also compatible with previous and newer versions of python3.

## Dependencies

Requires python3, the `argparse` package from Python Standard Library and the `bibtexparser` package (available via pip):

```
pip install bibtexparser
```

## Usage

This tool has been written primarily for the purpose of generating a list of publications for websites from bibtex files. The tool can be run as a Python script, e.g.:
```bash
python3 html_bib.py -b <bib> -o <outfile>
```

It accepts the following command-line arguments:
```
-b, --bib: Path to the BibTeX file or directory containing BibTeX files.
-o, --outfile: Path for the output HTML file.
```

The HTML bibliography is generated in a reverse chronological order and a paper link is also shown at the end of each reference if the `URL` field is present in the corresponding bibentry.
Note that even though bibtex supports citations for many entry types, this tool mostly focuses on the following entry types: `inproceedings`, `article`, `book`, `phdthesis` and `mastersthesis`. When citing other entry types it still produces a basic citation with the `author`, `title` and `year` fields (see **Note 1** below).

## Example

For a working example which uses the custom syntax with a variety of the above commands, execute the following on the command-line:
```bash
python3 html_bib.py -b example/biblio.bib -o example/biblio.html
```
The above uses the sample input file in the example folder. A copy of the generated output file (biblio.html) is already present in the example folder for reference.

## Notes

#### Note 1:
For citation purposes, every bibentry must have at least the following attributes: `author` (or `editor` for entry of type `book`), `title` and `year`. Additionally entries of type `inproceedings` must have a `booktitle` attribute and entries of type `article` must have a `journal` attribute.

#### Note 2:
For bibentries of type `book`, the `editor` attribute in `--bibfile` is checked before the `author` attribute to generate authors in the HTML bibliography. Exactly one of `editor` or `author` attributes is expected for bibentry of type `book`. If both are provided, the `editor` attribute overrides `author`.
