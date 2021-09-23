# Function to generate a publication markdown file from my exported csv.
#
# Notes: Will need to determine how to generate the abstract text. 
# Options are to try and scrape from the web (ugh), or just 
# dump abstract text into my master database.

import pandas as pd
from jinja2 import Environment, FileSystemLoader
import random
import numpy as np

markdown_env = Environment(
    loader=FileSystemLoader('templates'),
    variable_start_string='{@',
    variable_end_string='@}'
)

def num_authors(pub, max_authors=31):
    Alist = ['A' + str(i) for i in np.arange(1, max_authors)]
    n = 0
    for A in Alist:
        if pub[A] is not np.nan:
            n = n + 1
    return n

def make_excerpt(pub):
    excerpt = None
    if num_authors(pub) > 2:
        excerpt = pub.A1 + ' et al.'
    elif num_authors(pub) == 2:
        excerpt = pub.A1 + ', ' + pub.A2
    else: 
        excerpt = pub.A1 
    excerpt += ', ' + pub.TITLE.strip() + '.'
    return excerpt

# Load the publication table
# Only need published papers
from tables import Publications # NOQA
publication_file = 'CV/Publications-Table.csv'
template_file = 'website/Publications.template'
pubs = Publications(category='P', name='Publications',
            template_file=template_file,
            env = markdown_env,
            csv_file=publication_file)

pub = pubs.df.loc[0]
pub.excerpt = make_excerpt(pub)
pub.ID = random.randint(1000, 9999)
pub.YEAR = str(pub.YEAR)
pubs.template.render(pub=pub)

