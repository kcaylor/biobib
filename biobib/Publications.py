# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_Publications.ipynb.

# %% auto 0
__all__ = ['publication_types', 'publication_biobib_template', 'max_author', 'max_editor', 'author_cols', 'editor_cols',
           'decorate_dict', 'publication_cv_template']

# %% ../nbs/04_Publications.ipynb 2
from .table import Table, sh, tex_escape, colonify, to_int
from .sheet import Sheet
from nbdev import show_doc
import pandas as pd
import numpy as np

# %% ../nbs/04_Publications.ipynb 4
publication_types = {
    'P': 'Published',
    'A': 'In Press',
    'R': 'In Review'
}

# %% ../nbs/04_Publications.ipynb 6
publication_biobib_template = r'''% UC Bio-bib Publication Table
% Created on \VAR{created}

\begin{longtable}{p{1cm}p{0.5cm}p{7.75cm}>{\raggedright}p{5.25cm}p{1.75cm}}
\# & Year & Title and Authors & Publisher & Category\\
\\\hline 
\endfirsthead


\multicolumn{5}{c}%
{{\VAR{table_name} - continued from previous page }} \\ \\
\# & Year & Title and Authors & Publisher & Category\\
\hline 
\endhead

\\
\multicolumn{5}{c}%
{{ \VAR{table_name} continued on next page }} \\
\endfoot

\hline \hline
\endlastfoot

\BLOCK{for publication in items}
\BLOCK{if publication['New?'] != 'Y'}
    \VAR{publication|make_row}
\BLOCK{endif}
\BLOCK{endfor}
\\\hline
\\\hline
   &   & {\bf Since Prior Review:} &    &   \\\\
\BLOCK{for publication in items}
\BLOCK{if publication['New?'] == 'Y'}
    \VAR{publication|make_row}
\BLOCK{endif}
\BLOCK{endfor}
\end{longtable}
'''

# %% ../nbs/04_Publications.ipynb 8
max_author = 30
max_editor = 4
author_cols = ['A' + str(i+1) for i in range(max_author)]
editor_cols = ['E' + str(i+1) for i in range(max_editor)]

# %% ../nbs/04_Publications.ipynb 10
decorate_dict = {
    'Undergrad Author': "-UUUU-",
    'Visitor Author': "-VVVV-",
    'PhD Committee Member': "-MMMM-",
    'Graduate Advisee': "-AAAA-",
    'Postdoctoral Advisee': "-PPPP-"
}

# %% ../nbs/04_Publications.ipynb 13
@patch
def clean_df(self:Publications,
             sort_by:str='Year', # variable to sort by
             ascending:bool=True # ascending?
            )->pd.DataFrame:  # cleaned dataframe
    """
    Clean the Service table.
    
    """
    df = Table.table_clean_df(self)
    # Step 1: drop any papers not published
    # Step 1.1: filter to the target publication type, if any.
    if self.kind:
        df = df[df.Kind == self.kind]
    # Step 2: Concatenate authors into a single list, making sure to drop
    # empty author columns
    df['authors'] = list(
            pd.Series(df[author_cols] 
                    .fillna('').values.tolist())
            .apply(lambda x: [i for i in x if i != ''])
            .apply(lambda x: ', '.join(x))
    )
    df['editors'] = list(
            pd.Series(df[editor_cols]
                    .fillna('').values.tolist())
            .apply(lambda x: [i for i in x if i != ''])
            .apply(lambda x: ', '.join(x))
    )
    # Step 3: Cast DOI as a string and remove nan
    df.loc[df['DOI'] == 'nan', 'DOI'] = np.nan

    # Step 4: Cast Pages as a string and remove nan
    df.loc[df['PAGES'] == 'nan', 'PAGES'] = np.nan

    # Step 5: Cast Volume as a string and remove nan
    df.loc[df['VOL'] == 'nan', 'VOL'] = np.nan

    #df = df.sort_values(by=[sort_by], ascending=[ascending])
    return df

# %% ../nbs/04_Publications.ipynb 18
publication_cv_template = r'''% UC CV Publication Table
% Created on \VAR{created}

\BLOCK{ set years = [] }
\BLOCK{ for publication in items if publication.YEAR not in years }
    \BLOCK{ do years.append(publication.YEAR) }
\BLOCK{ endfor }

\BLOCK{ set max_year = years[-1]}

\mbox{\ \ \ \underline{\textbf{\VAR{max_year } }}}

\begin{etaremune}

\BLOCK{for publication in items}
\BLOCK{if (publication.YEAR == max_year) }
\VAR{publication|make_citation}
\BLOCK{ endif }
\BLOCK{ endfor }

\BLOCK{ for year in years|reverse }
\BLOCK{ if (year != max_year) }

\vspace{0.1in}
\mbox{\ \ \ \underline{\textbf{\VAR{year } }}}
\vspace{0.1in}

\BLOCK{for publication in items}
\BLOCK{if (publication.YEAR == year) }
\VAR{publication|make_citation}
\BLOCK{ endif }
\BLOCK{ endfor }
\BLOCK{ endif }
\BLOCK{ endfor }

\end{etaremune}
'''
