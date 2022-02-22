import pandas as pd
import numpy as np
import time
import re
from jinja2 import Environment, FileSystemLoader


latex_env = Environment(
    extensions = ['jinja2.ext.do'],
    block_start_string='\BLOCK{',
    block_end_string='}',
    variable_start_string='\VAR{',
    variable_end_string='}',
    comment_start_string='\#{',
    comment_end_string='}',
    line_statement_prefix='%%',
    line_comment_prefix='%#',
    trim_blocks=True,
    autoescape=False,
    loader=FileSystemLoader('templates'))

max_author = 30
author_cols = ['A' + str(i+1) for i in range(max_author)]

def to_int(value):
    try:
        v = str(int(value))
    except:
        v = value
    return v

def make_cell(text, size=''):
    """
        wrap text in a makecell
    """
    # split text by commas:
    text = ''.join([x + ',\\\\' for x in text.split(',')])
    text = text[:-3]
    text = "{" + size + " \\makecell{ " + text + "} }"
    return text


def tex_escape(text):
    """
        :param text: a plain text message
        :return: the message escaped to appear correctly in LaTeX
    """
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
        'Ω': r'$\Omega$',
        'δ': r'$\delta$',
        '’': r"'",
        '‐': r'--',
        '“': r'``',
        '”': r"''",
        'é': r'\'e',
        'nan': r'--'
    }

    text = str(text)
    regex = re.compile('|'.join(re.escape(key) for key in sorted(conv.keys(), key=lambda item: - len(item))))  # NOQA
    result = regex.sub(lambda match: conv[match.group()], text)
    if result == 'nan':
        result = ''
    return result


def str_join(df, sep, *cols):
    from functools import reduce
    return reduce(lambda x, y: x.astype(str).str.cat(y.astype(str), sep=sep),
                  [df[col] for col in cols])


def stringify(value):
    return str(value)

def colonify(string):
    if string:
        return ": " + string
    else:
        return ""

latex_env.filters['colonify'] = colonify
latex_env.filters['str_join'] = str_join
latex_env.filters['tex_escape'] = tex_escape
latex_env.filters['make_cell'] = make_cell
latex_env.filters['stringify'] = stringify


class Table:

    def __init__(self, name=None, csv_file=None, 
            env=latex_env, table_name=None,
            template_file=None, filters=None):
        self.name = name
        self.table_name = table_name
        self.df = pd.read_csv(csv_file)
        self.columns = ""
        self.type = "longtable"
        self.env = env
        if filters:
            for item in filters:
                self.env.filters[item] = filters[item]
        self.template = self.env.get_template(template_file)
        # self.df = self.clean_df()

    def write_template(self):
        return NotImplementedError

    def clean_df(self):
        return self.df

    def clean_cumulative(self, df):
        if self.cumulative is False:
            df = df[df.Eval == 1]
        return df

    def render_template(self):
        rendered_tex = self.template.render(
            table_name=self.table_name,
            created=time.strftime("%Y-%m-%d %H:%M"),
            items=list(self.df.to_dict('records'))
        )
        return rendered_tex

    def write_template(self, path=None):
        content = self.render_template()
        if path:
            file = path + self.name + '.tex'
        else:
            file = self.name + 'tex'

        with open(file, "w") as f:
            print(content, file=f)
    
    def href(self, this_href):
        if this_href is np.NaN:
            return ""
        else:
            return "\\href{{{href}}}{{[link]}}".format(href=this_href)


class Service(Table):

    def __init__(
            self,
            name='Service',
            table_name='Service',
            csv_file=None,
            category='P',
            cumulative=False,
            template_file='biobib/Service.template'):
        super(Service, self).__init__(
            name=name, csv_file=csv_file, template_file=template_file)
        self.cumulative = cumulative
        self.category = category
        self.df = self.clean_df()
        
    # def render_template(self):
    #     rendered_tex = self.template.render(
    #         created=time.strftime("%Y-%m-%d %H:%M"),
    #         items=self.df.to_dict('records')
    #     )
    #     return rendered_tex

    def clean_df(self):
        df = self.df
        # Step 1: drop any service from before this eval period
        df = self.clean_cumulative(df)
        # Step 2: filter to only the current category (or don't!)
        if self.category:
            df = df[df.Type == self.category]
        df = df.sort_values(by=['Year'], ascending=[True])
        return df


class ProfessionalService(Service):

    def __init__(
            self,
            name='ProfessionalService',
            csv_file=None,
            category='P',
            cumulative=False):
        super(ProfessionalService, self).__init__(
            name=name, csv_file=csv_file,
            category=category, cumulative=cumulative)
        self.category = category


class UniversityService(Service):

    def __init__(
            self,
            name='UniversityService',
            table_name='University Service',
            csv_file=None,
            category='U',
            cumulative=False):
        super(UniversityService, self).__init__(
            name=name, csv_file=csv_file, table_name=table_name,
            category=category, cumulative=cumulative)
        self.category = category


class DepartmentalService(Service):

    def __init__(
            self,
            name='DepartmentalService',
            table_name='Department Service',
            csv_file=None,
            category='D',
            cumulative=False):
        super(DepartmentalService, self).__init__(
            name=name, csv_file=csv_file, table_name=table_name,
            category=category, cumulative=cumulative)
        self.category = category

class Publications(Table):

    def __init__(
            self,
            env=latex_env,
            name='Publications',
            table_name='Cumulative List of Publications',
            csv_file=None,
            category='P',
            type=None,
            template_file='biobib/Publications.template'):
        self.env = env
        self.filters = {
            'make_row': self.make_row,
            'make_citation': self.make_citation,
            'doi': self.doi,
            'doi_link': self.doi_link,
            'href': self.href
        }
        super(Publications, self).__init__(
            name=name, csv_file=csv_file, template_file=template_file, 
            table_name=table_name,
            env=self.env, filters=self.filters)
        self.category = category
        self.type = type
        self.cumulative = True  # Always provide complete publication list
        self.df = self.clean_df()
        
    def clean_df(self):
        df = self.df
        df = self.clean_cumulative(df)
        # Step 1: drop any papers not published
        df = df[df.S == self.category]
        # Step 1.1: filter to the target publication type, if any.
        if self.type:
            df = df[df.Type == self.type]
        
        # Step 2: Concatenate authors into a single list, making sure to drop
        # empty author columns
        df['authors'] = list(
            pd.Series(df[author_cols]  # NOQA
                      .fillna('').values.tolist())
            .apply(lambda x: [i for i in x if i != ''])
            .apply(lambda x: ', '.join(x))
        )
        df['editors'] = list(
            pd.Series(df[['E1', 'E2', 'E3', 'E4']]  # NOQA
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

        return df

    def category_lookup(self, category):
        Categories = {
            'RA': 'Refereed Article',
            'CA': 'Conference Abstract',
            'BC': 'Refereed Book Chapter',
            'CP': 'Refereed Conference Proceedings'
        }
        return Categories[category]

    def doi(self, this_doi):
        if this_doi is np.NaN:
            return ""
        else:
            return "doi:{doi}.".format(doi=this_doi)

    def href(self, this_href, text="[pdf]"):
        if this_href is np.NaN:
            return ""
        else:
            return "\\href{{{href}}}{{{text}}}".format(href=this_href,text=text)

    def doi_link(self, this_doi):
        if this_doi is np.NaN:
            return ""
        else:
            this_href = "https://doi.org/{doi}".format(doi=str(this_doi))
            text = "doi:{doi}".format(doi=str(this_doi).rstrip())
            return "\\href{{{href}}}{{{text}}}".format(href=this_href, text=text)
     
    def make_row(self, row):
        if row['Type'] == 'RA':
            return self.make_article(row)
        elif row['Type'] == 'BC':
            return self.make_chapter(row)
        elif row['Type'] == 'CP':
            return self.make_chapter(row)

    def make_citation(self, this_row):
        citation = "\item "
        citation += "{authors} ({year}) {title}. \\emph{{{publisher}}}, {volume}{pages}. {href}".format( #NOQA
            year=tex_escape(str(this_row['YEAR'])),
            title=tex_escape(this_row['TITLE']),
            authors=tex_escape(this_row['authors']),
            # doi=self.doi(this_row['DOI']),
            href=self.doi_link(this_row['DOI']),
            volume=tex_escape(this_row['VOL']),
            pages=colonify(tex_escape(this_row['PAGES'])),
            publisher=tex_escape(this_row['PUBLISHER'])
        )
        return citation


    def make_article(self, this_row):
        row = ""
        row += "{code} & {year} & {{\\bf {title}}}, {authors} {href} & \\emph{{ {publisher} }} {volume}{pages}. {doi}  & {category}".format(  # NOQA
            code=tex_escape(to_int(this_row['NUM'])),
            year=tex_escape(str(this_row['YEAR'])),
            title=tex_escape(this_row['TITLE']),
            authors=tex_escape(this_row['authors']),
            doi=self.doi(this_row['DOI']),
            href=self.href(this_row['Link']),
            volume=tex_escape(this_row['VOL']),
            pages=colonify(tex_escape(this_row['PAGES'])),
            publisher=tex_escape(this_row['PUBLISHER']),
            category=tex_escape(self.category_lookup(this_row['Type']))
        )
        row += "\\\\"
        return row

    def get_editors(self, editors):
        if editors:
            return editors + " (eds.)."
        else:
            return ""

    def make_chapter(self, this_row):
        row = ""
        row += "{code} & {year} & {{\\bf {title}}}, {authors} & {editors} \\emph{{ {book} }}. {publisher} & {category}".format(  # NOQA
            code=tex_escape(to_int(this_row['NUM'])),
            year=tex_escape(str(this_row['YEAR'])),
            title=tex_escape(this_row['TITLE']),
            authors=tex_escape(this_row['authors']),
            editors=tex_escape(self.get_editors(this_row['editors'])),
            book=tex_escape(this_row['Book Title']),
            publisher=tex_escape(this_row['PUBLISHER']),
            category=tex_escape(self.category_lookup(this_row['Type']))
        )
        row += "\\\\"
        return row


class InPress(Publications):

    def __init__(self, name='InPress',
            csv_file=None,  category='A',
            table_name='Works in Press',
            template_file='biobib/InPressPublications.template'):
        super(InPress, self).__init__(
            name=name, csv_file=csv_file, table_name=table_name,
            template_file=template_file, category=category)
        self.category = category

class Submitted(Publications):

    def __init__(self, name='Submitted', csv_file=None,  category='R',
            template_file='biobib/InPressPublications.template'):
        super(Submitted, self).__init__(
            name=name, csv_file=csv_file,
            template_file=template_file, category=category)
        self.category = category

class Courses(Table):

    def __init__(self, name='Courses', csv_file=None, cumulative=False,
            table_name='Catalog Courses',
            template_file='biobib/Courses.template'):
        self.filters = {
            'href': self.href
        }
        super(Courses, self).__init__(
            name=name, csv_file=csv_file, template_file=template_file,
            table_name=table_name,
            filters=self.filters)
        self.cumulative = cumulative
        self.df = self.clean_df()
        
    # def render_template(self):
    #     rendered_tex = self.template.render(
    #         created=time.strftime("%Y-%m-%d %H:%M"),
    #         courses=self.df.to_dict('records')
    #     )
    #     return rendered_tex

    def clean_df(self):
        df = self.df
        # Step 1: drop any courses from before this eval period
        df = self.clean_cumulative(df)
        df = df.sort_values(['Year', 'Q', 'Course'], ascending=[True, True, True])  # NOQA
        return df

class MESM(Table):

    def __init__(self, name='MESMProject', csv_file=None, cumulative=False,
                 table_name='MESM Projects Advised',
            template_file='biobib/MESMProjects.template'):
        super(MESM, self).__init__(
            name=name, csv_file=csv_file, 
            table_name=table_name, template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df()

    def clean_df(self):
       return self.clean_cumulative(self.df)

class UndergradAdvising(Table):

    def __init__(self, name='Undergradautes', csv_file=None, cumulative=False,
                 table_name='Undergraduate Projects Directed',
                template_file='biobib/UndergradAdvising.template'):
        super(UndergradAdvising, self).__init__(
            table_name=table_name,
            name=name, csv_file=csv_file, template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df()
    
    def clean_df(self):
       return self.clean_cumulative(self.df)


class Visitors(Table):

    def __init__(self, name='Visitors', csv_file=None, cumulative=False):
        super(Visitors, self).__init__(
            name=name, csv_file=csv_file, template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df()


class GraduateAdvising(Table):

    def __init__(self, name='GraduateAdvising', csv_file=None, cumulative=False,   # NOQA
                template_file='biobib/GradAdvising.template', table_name='GraduateAdvising'):
        super(GraduateAdvising, self).__init__(
            name=name, table_name=table_name, 
            csv_file=csv_file, template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df()
        
    def clean_df(self):
        df = self.df
        # Step 1: drop any committee work from prior evaluation
        df = self.clean_cumulative(df)
        df = df.sort_values(
            by=['Year', 'Role', 'Student'], ascending=[True, True, True])
        return df


class PostdoctoralAdvising(Table):

    def __init__(self, name='PostdoctoralAdvising', csv_file=None, cumulative=False,  # NOQA
            table_name='Postdoctoral Scholars Supervised', 
            template_file='biobib/PostdoctoralAdvising.template'):
        self.filters = {
            'make_years': self.make_years
        }
        super(PostdoctoralAdvising, self).__init__(
            name=name, csv_file=csv_file, 
            table_name=table_name, template_file=template_file, filters=self.filters)
        self.cumulative = cumulative
        self.df = self.clean_df()

    def clean_df(self, cumulative=False):
        df = self.df
        # Step 1: drop any advising work from prior evaluation
        df = self.clean_cumulative(df)
        return df
    
    def make_years(self, row):
        if pd.isnull(row['End Year']):
            return "{start} - ".format(
                start=int(row['Start Year']))
        else:
            return "{start}-{end}".format(
                start=int(row['Start Year']),
                end=int(row['End Year']))
        
        

class Lectures(Table):

    def __init__(self, name='Lectures', csv_file=None, cumulative=False,
            template_file='biobib/Lectures.template',
            table_name='Lectures and Seminars Presented'):
        super(Lectures, self).__init__(
            name=name,
            csv_file=csv_file,
            table_name=table_name,
            template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df()

    def clean_df(self, cumulative=False):
        df = self.df
        df = self.clean_cumulative(df)
        df = df.sort_values(by=['Year', 'Month'])
        return df


class Proceedings(Lectures):

    def __init__(self, name='Proceedings', csv_file=None, cumulative=False,
            template_file='biobib/Proceedings.template',
            table_name='Conference Posters and Presentations'):
        super(Lectures, self).__init__(
            name=name,
            table_name=table_name,
            csv_file=csv_file, template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df(cumulative=cumulative)

    def clean_df(self, cumulative=False):
        df = self.df
        df = self.clean_cumulative(df)
        # df['Topic'] = df['Title'] + ". " + df['Authors']
        df = df.sort_values(by=['Year','Month'], ascending=[True, True])
        df.Year = df.Year.astype(int)
        return df


class Funding(Table):

    def __init__(self, name='Funding', csv_file=None, cumulative=False,
            template_file='biobib/Funding.template',
            table_name='Grants and Contracts'):
        self.filters = {
            'make_years': self.make_years
        }
        super(Funding, self).__init__(
            name=name, csv_file=csv_file,
            table_name=table_name,
            template_file=template_file, filters=self.filters)
        self.cumulative = cumulative
        self.df = self.clean_df()
        
    def total(self, new=False):
        if new:
            funds = self.df[self.df['Type'] == 'New']
        else:
            funds = self.df
    
        return {
            'Total Amount': '${:,.0f}'.format(
                funds['Total Amount'].replace('[\$,]', '', regex=True).astype(float).sum()),
            'Total to UCSB': '${:,.0f}'.format(
                funds['Total to UCSB'].replace('[\$,]', '', regex=True).astype(float).sum()),
            'Total Personal Share': '${:,.0f}'.format(
                funds['Personal Share'].replace('[\$,]', '', regex=True).astype(float).sum())
        }

    def clean_df(self):
        df = self.df
        df = self.clean_cumulative(df)
        # Replace NaN with a 'nan' string for checking later
        df['Start Date'].fillna('nan', inplace=True)
        df['End Date'].fillna('nan', inplace=True)
        df = df.sort_values(by=['Start Year', 'Total Amount'],
                            ascending=[True, False])
        return df

    def make_years(self, row):
        if row['Start Date'] != 'nan' and row['End Date'] != 'nan':
            return "{start}-{end}".format(
                start=row['Start Date'],
                end=row['End Date'])
        else:
            return "{start}-{end}".format(
                start=row['Start Year'],
                end=row['End Year'])
    
    def render_template(self):
        rendered_tex = self.template.render(
            table_name=self.table_name,
            created=time.strftime("%Y-%m-%d %H:%M"),
            items=list(self.df.to_dict('records')),
            total=self.total(new=False),
            total_new=self.total(new=True)
        )
        return rendered_tex



class OtherProfessionalActivities(Table):
    def __init__(self, name='OtherProfessionalActivities', csv_file=None, cumulative=False,
            template_file='biobib/OtherProfessionalActivities.template'):
        super(OtherProfessionalActivities, self).__init__(
            name=name, csv_file=csv_file,
            template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df()
    
    def clean_df(self):
        df = self.df
        df = self.clean_cumulative(df)
        df = df.sort_values(by=['Year', 'Role'], ascending=[True, False])
        return df

class SpecialAppointments(Table):
    def __init__(self, name='SpecialAppointments', csv_file=None, cumulative=False,
            template_file='biobib/SpecialAppointments.template',
            table_name='Special Appointments'):
        super(SpecialAppointments, self).__init__(
            name=name, csv_file=csv_file, table_name=table_name,
            template_file=template_file)
        self.cumulative = cumulative
        self.df = self.clean_df()
    
    def clean_df(self):
        df = self.df
        df = self.clean_cumulative(df)
        df = df.sort_values(by=['Year', 'Role'], ascending=[True, False])
        return df

class Reviews(Table):

    def __init__(self, name='Reviews', csv_file=None, cumulative=False,
            template_file='biobib/Reviews.template',
            table_name='Reviewing and Refereeing Activity'):
        self.filters = {
            'add_count': self.add_count
        }
        super(Reviews, self).__init__(
            name=name, csv_file=csv_file, table_name=table_name,
            template_file=template_file, filters=self.filters)
        self.cumulative = cumulative
        self.df = self.clean_df()
        
    def clean_df(self):
        df = self.df
        df = self.clean_cumulative(df)
        df = df.sort_values(by=['Year', 'Role'], ascending=[True, False])
        df = (df.groupby(['Year', 'Role', 'Journal or Agency'])
              .sum('Count')
              .reset_index()
              )
        return df

    def add_count(self, count):
        if count > 1:
            return "({count})".format(count=count)
        else:
            return ""
