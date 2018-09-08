#! /usr/bin/python3

# System imports
import argparse
import os
import errno
import datetime

# Package imports
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import convert_to_unicode, author, editor, page_double_hyphen

################# Constants #################

month_dict = {
    'January': 1, 'Jan': 1,
    'February': 2, 'Feb': 2,
    'March': 3, 'Mar': 3,
    'April': 4, 'Apr': 4,
    'May': 5,
    'June': 6, 'Jun': 6,
    'July': 7, 'Jul': 7,
    'August': 8, 'Aug': 8,
    'September': 9, 'Sept': 9, 'Sep': 9,
    'October': 10, 'Oct': 10,
    'November': 11, 'Nov': 11,
    'December': 12, 'Dec': 12
}

clr_author = '#900'
# clr_venue_time = '#090'
clr_venue_time = '#666666'
clr_hyperlink = '#1772d0'
bullet_spacing = 8

global br_sym

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


def process_title(title, entrytype, fmt):
    if fmt == 'std':
        if entrytype.lower() in ['inproceedings', 'article']:
            return title
        else:
            return '<i>{}</i>'.format(title)
    elif fmt == 'std_b' or fmt.startswith('str'):
        return '<b>{}</b>'.format(title)
    else:
        print('Incorrect formatting option: {}'.format(fmt))


def process_authors(authors, entrytype, fmt):
    if fmt.startswith('std') or fmt == 'str':
        return authors
    elif fmt == 'str_c':
        return '<span style="color:{}">{}</span>'.format(clr_author, authors)
    else:
        print('Incorrect formatting option: {}'.format(fmt))


def process_venue(venue, entrytype, fmt):
    if fmt.startswith('std'):
        if entrytype.lower() in ['inproceedings', 'article']:
            return '<i>{}</i>'.format(venue)
        else:
            return venue
    elif fmt == 'str':
        return venue
    elif fmt == 'str_c':
        return '<span style="color:{}">{}</span>'.format(clr_venue_time, venue)
    else:
        print('Incorrect formatting option: {}'.format(fmt))


def process_time(time, entrytype, fmt):
    if fmt.startswith('std') or fmt =='str':
        return time
    elif fmt == 'str_c':
        return '<span style="color:{}">{}</span>'.format(clr_venue_time, time)
    else:
        print('Incorrect formatting option: {}'.format(fmt))


def process_hyperlink(url, text, entrytype, fmt):
    return '[<a href={} style="color:{}">{}</a>]'.format(url, clr_hyperlink, text)


def get_html(ref_tuple, fmt):
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
    if bibentry['ENTRYTYPE'].lower() == 'book' and 'subtitle' in bibentry:
        title = title + '. ' + bibentry['subtitle']

    # Process necessary fields
    authors = process_authors(authors, bibentry['ENTRYTYPE'].lower(), fmt)
    title = process_title(title, bibentry['ENTRYTYPE'].lower(), fmt)
    time = process_time(time, bibentry['ENTRYTYPE'].lower(), fmt)

    # Form HTML bibliography entry according to fmt with additional fields
    ## Standard citation format (std)
    if fmt.startswith('std'):
        html = authors + '. ' + title + '. '

        if bibentry['ENTRYTYPE'].lower() == 'book':
            if 'publisher' in bibentry:
                html = html + bibentry['publisher'] + ', '

        elif 'thesis' in bibentry['ENTRYTYPE'].lower():
            if bibentry['ENTRYTYPE'].lower() == 'phdthesis':
                html = html + 'PhD thesis, '
            elif bibentry['ENTRYTYPE'].lower() == 'mastersthesis':
                html = html + 'Masters thesis, '
            if 'school' in bibentry:
                html = html + bibentry['school'] + ', '

        elif bibentry['ENTRYTYPE'].lower() == 'inproceedings':
            html = html + 'In ' + process_venue(bibentry['booktitle'], bibentry['ENTRYTYPE'], fmt) + ', '
            if 'pages' in bibentry:
                html = html + 'pages ' + bibentry['pages'] + ', '

        elif bibentry['ENTRYTYPE'].lower() == 'article':
            html = html + process_venue(bibentry['journal'], bibentry['ENTRYTYPE'], fmt) + ', '
            if 'volume' in bibentry and 'number' in bibentry and 'pages' in bibentry:
                html = html + bibentry['volume'] + '(' + bibentry['number'] + '):' + bibentry['pages'] + ', '

        html = html + time

        # Add paper link if present in bibentry
        if 'url' in bibentry:
            html = html + '\n' + process_hyperlink(bibentry['url'], 'Paper', bibentry['ENTRYTYPE'].lower(), fmt)

    ## Structured citation format (str)
    elif fmt.startswith('str'):
        html = title + '\n{}'.format(br_sym) + authors + '\n{}'.format(br_sym)

        if bibentry['ENTRYTYPE'].lower() == 'inproceedings':
            html = html + process_venue(bibentry['booktitle'], bibentry['ENTRYTYPE'], fmt) + ', '
        elif bibentry['ENTRYTYPE'].lower() == 'article':
            html = html + process_venue(bibentry['journal'], bibentry['ENTRYTYPE'], fmt) + ', '
        elif 'thesis' in bibentry['ENTRYTYPE'].lower() and 'school' in bibentry:
            html = html + process_venue(bibentry['school'], bibentry['ENTRYTYPE'], fmt) + ', '
        elif bibentry['ENTRYTYPE'].lower() == 'book' and 'publisher' in bibentry:
            html = html + process_venue(bibentry['publisher'], bibentry['ENTRYTYPE'], fmt) + ', '
        html = html + time

        # Add paper link if present in bibentry
        if 'url' in bibentry:
            html = html + '\n{}'.format(br_sym) + process_hyperlink(bibentry['url'], 'Paper', bibentry['ENTRYTYPE'].lower(), fmt)

    return html


def bibtex2html(args):
    bib = args.bib
    outfile = args.outfile

    # Extract all references from bib
    refsdict = load_bibtex(bib, customizer=customizations)
    refslist = [(k, v) for k, v in refsdict.items()]

    # Sort by month and year
    sorted_refslist = sorted(refslist, key=comp_time)
    sorted_refslist.reverse()

    # Generate html string
    html_string = '<ul>'
    for ref in sorted_refslist:
        html_string = html_string + '\n<li style="margin: {}px 0">'.format(bullet_spacing) + get_html(ref, args.format) + '</li>'
    html_string = html_string + '\n</ul>'

    # Write html string to file
    with open(outfile, 'w') as outf:
        outf.write(html_string)


if __name__ == "__main__":
    # Generate argument parser
    parser = argparse.ArgumentParser(
        description="Convert a bibtex file or directory containing bibtex files to an HTML bibliography.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # Add and parse arguments
    parser.add_argument("-b", "--bib",
        help="Path to the BibTeX file or directory containing BibTeX files.")
    parser.add_argument("-o", "--outfile",
        help="Path for the output HTML file.")
    parser.add_argument("-f", "--format",
        default="str",
        help="Format of HTML bibliography [std, std_b, str, str_c].")
    parser.add_argument("-nobr", "--no_break",
        help='Flag to prevent any <br> tags in the generated HTML.',
        default=False, action='store_true')
    args = parser.parse_args()

    global br_sym
    br_sym = '' if args.no_break else '<br>'

    # Generate html bibliography from bib file/(s)
    bibtex2html(args)
