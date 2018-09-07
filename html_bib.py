#! /usr/bin/python3

# System imports
import argparse
import os
import errno
import datetime

# Package imports
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode, author, editor, page_double_hyphen


################# Helper Methods #################


def customizations(record):
    ''' Use some customizations for bibtexparser

    Args:
        record: A record

    Returns:
        record: Customized record
    '''
    record = convert_to_unicode(record)
    # record = type(record)
    record = author(record)
    record = editor(record)
    # record = journal(record) # Do not use!
    # record = keyword(record)
    # record = link(record)
    record = page_double_hyphen(record)
    # record = doi(record)
    return record


def load_bibtex(bibpath, customizer=None):
    if os.path.isfile(bibpath):
        # Open and parse the BibTeX file in `bibpath` using `bibtexparser`
        if not bibpath.endswith(".bib"):
            print("INFO: Skipping {} - No .bib extension.".format(bibpath))
            return {}            
        else:
            bp = BibTexParser(open(bibpath, 'r').read(), customization=customizer)
            # Get a dictionary of dictionaries of key, value pairs from the
            # BibTeX file. The structure is {ID:{authors:...},ID:{authors:...}}.
            refsdict = bp.get_entry_dict()
            return refsdict
    elif os.path.isdir(bibpath):
        # Create a joint refsdict for all bibtex files inside this directory
        refsdict = {}
        for name in os.listdir(bibpath):
            # Recursively process all files and subdirectories
            inpath = os.path.join(bibpath, name)
            refdict = load_bibtex(inpath, customizer=customizer)
            refsdict.update(refdict)
        return refsdict


def comp_time(ref_tuple):
    bibID, bibentry = ref_tuple
    assert 'year' in bibentry, "{} is missing field: year".format(bibID)
    year = int(bibentry['year'])
    month = bibentry.get('month', None)
    month_dict = {
        'January': 1,
        'Jan': 1,
        'February': 2,
        'Feb': 2,
        'March': 3,
        'Mar': 3,
        'April': 4,
        'Apr': 4,
        'May': 5,
        'June': 6,
        'Jun': 6,
        'July': 7,
        'Jul': 7,
        'August': 8,
        'Aug': 8,
        'September': 9,
        'Sept': 9,
        'Sep': 9,
        'October': 10,
        'Oct': 10,
        'November': 11,
        'Nov': 11,
        'December': 12,
        'Dec': 12
    }
    month = month_dict[month] if month is not None else 1
    return datetime.datetime(year, month, 1)


def get_authors_list(ref_tuple):
    bibID, bibentry = ref_tuple
    if bibentry['ENTRYTYPE'].lower() == 'book' and 'editor' in bibentry:
        authors_list = [editor['name'] for editor in bibentry['editor']]
    else:
        authors_list = bibentry['author']
    processed_authors_list = []
    for author in authors_list:
        a_name = author.split(',')
        a_name[0] = a_name[0].strip()
        a_name[1] = a_name[1].strip()
        processed_authors_list.append(a_name[1] + ' ' + a_name[0])
    if len(processed_authors_list) == 1:
        return processed_authors_list[0]
    elif len(processed_authors_list) == 2:
        return processed_authors_list[0] + ' and ' + processed_authors_list[1]
    elif len(processed_authors_list) >= 3:
        processed_authors_list[-1] = 'and ' + processed_authors_list[-1]
        return ', '.join(processed_authors_list)


def get_html(ref_tuple):
    bibID, bibentry = ref_tuple

    # Check validity of reference
    assert 'author' in bibentry or 'editor' in bibentry, 'Missing field author/editor in {}'.format(bibID)
    assert 'title' in bibentry, 'Missing field title in {}'.format(bibID)
    assert 'year' in bibentry, 'Missing field year in {}'.format(bibID)

    # Extract necessary fields
    authors = get_authors_list(ref_tuple)
    title = bibentry['title']
    time = bibentry['year']
    if 'month' in bibentry:
        time = bibentry['month'] + ' ' + time

    # Form HTML bibliography entry with additional fields
    if bibentry['ENTRYTYPE'].lower() == 'book':
        if 'subtitle' in bibentry:
            title = title + '. ' + bibentry['subtitle']
        html = authors + '. <i>' + title + '</i>. '
        if 'publisher' in bibentry:
            html = html + bibentry['publisher'] + ', '

    elif 'thesis' in bibentry['ENTRYTYPE'].lower():
        html = authors + '. <i>' + title + '</i>. '
        if bibentry['ENTRYTYPE'].lower() == 'phdthesis':
            html = html + 'PhD thesis, '
        elif bibentry['ENTRYTYPE'].lower() == 'mastersthesis':
            html = html + 'Masters thesis, '
        if 'school' in bibentry:
            html = html + bibentry['school'] + ', '

    elif bibentry['ENTRYTYPE'].lower() == 'inproceedings':
        html = authors + '. ' + title + '. '
        html = html + 'In <i>' + bibentry['booktitle'] + '</i>, '
        if 'pages' in bibentry:
            html = html + 'pages ' + bibentry['pages'] + ', '

    elif bibentry['ENTRYTYPE'].lower() == 'article':
        html = authors + '. ' + title + '. '
        html = html + '<i>' + bibentry['journal'] + '</i>, '
        if 'volume' in bibentry and 'number' in bibentry and 'pages' in bibentry:
            html = html + bibentry['volume'] + '(' + bibentry['number'] + '):' + bibentry['pages'] + ', '

    else:
        html = authors + '. <i>' + title + '</i>. '

    html = html + time + '.'

    # Add paper link if present in bibentry
    if 'url' in bibentry:
        html = html + '\n<a href={}>{}</a>'.format(bibentry['url'], 'Paper')

    return html


# def process_full(self, ref):
#     authors = self.process_authors(ref)[0]
#     title = self.process_title(ref)[0]
#     time = ref['year']

#     if 'month' in ref:
#         time = ref['month'] + ' ' + time
#     if ref['ENTRYTYPE'].lower() == 'book' and 'subtitle' in ref:
#         title = title + '. ' + ref['subtitle'] + '.'

#     citation = '**' + title + '**\n  *' + authors + '*\n  '
#     if ref['ENTRYTYPE'].lower() == 'book':
#         if 'publisher' in ref:
#             citation = citation + ref['publisher'] + ', '
#     elif 'thesis' in ref['ENTRYTYPE'].lower():
#         if ref['ENTRYTYPE'].lower() == 'phdthesis':
#             citation = citation + 'PhD thesis, '
#         elif ref['ENTRYTYPE'].lower() == 'mastersthesis':
#             citation = citation + 'Masters thesis, '
#         if 'school' in ref:
#             citation = citation + ref['school'] + ', '
#     elif ref['ENTRYTYPE'].lower() == 'inproceedings':
#         citation = citation + ref['booktitle'] + ', '            
#     elif ref['ENTRYTYPE'].lower() == 'article':
#         citation = citation + ref['journal'] + ', '
#     citation = citation + time

#     return citation, None


def bib_to_html(args):
    bib = args.bib
    outfile = args.outfile

    # Extract all references from bib
    refsdict = load_bibtex(bib, customizer=customizations)
    refslist = [(k, v) for k, v in refsdict.items()]

    # Sort by month and year
    sorted_refslist = sorted(refslist, key=comp_time)
    sorted_refslist.reverse()

    html_string = ''
    for ref in sorted_refslist:
        html_string = html_string + '\n<p>' + get_html(ref) + '</p>'

    with open(outfile, 'w') as outf:
        outf.write(html_string)


if __name__ == "__main__":
    # Generate argument parser
    arg_parser = argparse.ArgumentParser(
        description="Convert a bibtex file or directory containing bibtex files to an HTML bibliography.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Add and parse arguments
    arg_parser.add_argument("-b", "--bib",
        help="Path to the BibTeX file or directory containing BibTeX files.")
    arg_parser.add_argument("-o", "--outfile",
        help="Path for the output HTML file.")
    args = arg_parser.parse_args()

    # Generate html bibliography from bib file/(s)
    bib_to_html(args)
