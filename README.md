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
python3 bibtex2html.py -b <bib> -o <outfile> -f <format>
```

It accepts the following command-line arguments:
```
-b, --bib: Path to the BibTeX file or directory containing BibTeX files.
-o, --outfile: Path for the output HTML file.
-f, --format (default=str): Format of HTML bibliography [std, std_b, str, str_c].
-nobr, --no_break (default=False): Flag to prevent any <br> tags in the generated HTML (see **Note 3** below).
```

The HTML bibliography is generated in a reverse chronological order and a paper link is also shown at the end of each reference if the `URL` field is present in the corresponding bibentry.
Note that even though bibtex supports citations for many entry types, this tool mostly focuses on the following entry types: `inproceedings`, `article`, `book`, `phdthesis` and `mastersthesis`. When citing other entry types it still produces a basic citation with the `author`, `title` and `year` fields (see **Note 1** below).

The tool supports four <format> values currently:
```
std: Standard citation style bibliography with a paper link at the end (if URL present in bibentry).
std_b: Same as std, except with a bold title.
str: Structured format with upto four lines. 1st line: bold title, 2nd line: author list, 3rd line: venue and time[, 4th line: paper link, if URL present in bibentry).
str_c: Same as str, but the second and third lines have a color coding.
```

## Example

For a working example which uses the custom syntax with a variety of the above commands, execute the following on the command-line:
```bash
python3 bibtex2html.py -b example/biblio.bib -o example/biblio.html -f str
```
The above uses the sample input file in the example folder. A copy of the generated output file (biblio.html) is already present in the example folder for reference.

## Notes

#### Note 1:
For citation purposes, every bibentry must have at least the following attributes: `author` (or `editor` for entry of type `book`), `title` and `year`. Additionally entries of type `inproceedings` must have a `booktitle` attribute and entries of type `article` must have a `journal` attribute.

#### Note 2:
For bibentries of type `book`, the `editor` attribute in `--bibfile` is checked before the `author` attribute to generate authors in the HTML bibliography. Exactly one of `editor` or `author` attributes is expected for bibentry of type `book`. If both are provided, the `editor` attribute overrides `author`.

#### Note 3:
The `--no_break` argument is sometimes useful while generating reference lists for platforms like Wordpress, which insert `<br>` tags automatically.
