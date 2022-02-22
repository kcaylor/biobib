# Function to generate a publication markdown file from my exported csv.
#
# Notes: Will need to determine how to generate the abstract text. 
# Options are to try and scrape from the web (ugh), or just 
# dump abstract text into my master database.

import pandas as pd
from jinja2 import Environment, FileSystemLoader
import random
import numpy as np
import datetime
from rich import print

markdown_env = Environment(
    loader=FileSystemLoader('templates'),
    variable_start_string='{@',
    variable_end_string='@}'
)

# List of possible authors:
authors = [
    'Kelly Caylor',
    'Natasha Krell',
    'Cascade Tuholske',
    'Farai Kaseke',
    'Bryn Morgan',
    'Ryan Avery',
    'Rachel Green',
    'Mark Mayes',
    'Marcus Thompson',
    'Kristina Fauss',
    'Anna Boser',
    'Drew Gower'
]

ASSET_DIR = 'assets/images/publications/'
AUTHOR_MAX = 31

def make_authors(pub, max_authors=AUTHOR_MAX):
    Alist = ['A' + str(i) for i in np.arange(1, max_authors)]
    authors = []
    for A in Alist:
        if pub[A] is not np.nan:
            authors.append(pub[A])
    return authors

def make_author_tags(pub):
    last_names = [i.split(',')[0] for i in pub.author_list]
    author_tags = []
    for name in last_names:
        match = [i for i in authors if name in i]
        if match:
            author_tags.append(match[0])
    return author_tags

# def num_authors(pub, max_authors=AUTHOR_MAX):
#     Alist = ['A' + str(i) for i in np.arange(1, max_authors)]
#     n = 0
#     for A in Alist:
#         if pub[A] is not np.nan:
#             n = n + 1
#     return n

def make_citation(pub):
    citation = ', '.join(pub.author_list)
    citation += '(' +str(pub.YEAR) + ') '
    citation += pub.TITLE + '. '
    citation += pub.PUBLISHER + ', '
    citation += pub.DOI 
    return citation

def make_excerpt(pub):
    excerpt = None
    num_authors = len(pub.author_list)
    if num_authors > 2:
        excerpt = pub.A1 + ' et al.'
    elif num_authors == 2:
        excerpt = pub.A1 + ', ' + pub.A2
    else: 
        excerpt = pub.A1 
    excerpt += ' (' + str(pub.YEAR) + ') '
    excerpt += pub.TITLE.strip() + '. '
    excerpt += pub.PUBLISHER + ', '
    excerpt += 'doi:' + str(pub.DOI)
    return excerpt

def make_tags(pub):
    tags = ["'" + str(pub.YEAR) + "'", pub.PUBLISHER]
    return tags

def make_teaser(pub, image_dir=ASSET_DIR, ext='.png'):
    teaser = image_dir + pub.file + ext
    return teaser


def make_figure(pub, image_dir=ASSET_DIR, ext='.png'):
    figure = image_dir + pub.file + '_figure' + ext
    return figure


def make_pub(pub, author=None):
    pub.author_list = make_authors(pub)
    if not author:
        print(pub.author_list)
        author = input(f"Who is the author of this publication? : ")
    pub.AUTHOR = author
    pub.LASTNAME = pub.AUTHOR.split(" ")[-1]
    pub.excerpt = make_excerpt(pub)
    pub.tag_list = make_tags(pub)
    pub.author_tags = make_author_tags(pub)
    pub.ID = random.randint(1000, 9999)
    pub.DATE = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pub.YEAR = str(pub.YEAR)
    pub.URL = 'https://www.doi.org/' + str(pub.DOI)
    pub.file = pub.LASTNAME + str(pub.YEAR) + '_' + str(pub.ID)
    pub.teaser = make_teaser(pub)
    pub.figure = make_figure(pub)
    pub.citation = make_citation(pub)
    return pub


# Load the publication table
# Only need published papers
from tables import Publications  # NOQA
publication_file = 'CV/Publications-Table.csv'
template_file = 'website/Publications.template'
pubs = Publications(category='P', name='Publications',
                    template_file=template_file,
                    env=markdown_env,
                    csv_file=publication_file)

#pub = make_pub(pubs.df.loc[129])
#pub.excerpt = make_excerpt(pub)
#pub.tag_list = make_tags(pub)
#pub.ID = random.randint(1000, 9999)
#pub.DATE = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#pub.YEAR = str(pub.YEAR)
#pub.URL = 'https://www.doi.org/' + str(pub.DOI)
#print(pubs.template.render(pub=pub))


def print_markdown(pub_id=None):
    if not pub_id:
       pub_id = input(f"Which publication ID?: ")
    pub = make_pub(pubs.df.loc[130], author="Natasha Krell")
    print(pubs.template.render(pub=pub))
