""" Builds bio-bib from csv files generated by exporting CV.numbers """
from tables import Publications, InPress, Submitted
path = 'tex/'

publication_file = 'CV/Articles-Table.csv'
Publications(category='P', name='Publications',
             csv_file=publication_file).write_table(path=path)
InPress(category='A', name='InPress',
        csv_file=publication_file).write_table(path=path)
Submitted(category='R', name='Submitted',
          csv_file=publication_file).write_table(path=path)

# from tables import Proceedings
# proceedings_file = 'CV/Conference Abstracts-Table 1.csv'
# Proceedings(csv_file=proceedings_file, name='Proceedings').write_table()

from tables import Courses
courses_file = 'CV/Teaching-Table.csv'
Courses(csv_file=courses_file, name='Courses').write_table(path=path)

from tables import GraduateAdvising
graduate_ms_file = 'CV/Graduate MA MS-Table.csv'
GraduateAdvising(csv_file=graduate_ms_file,
                 name='GraduateAdvisingMS').write_table(path=path)
graduate_phd_file = 'CV/Graduate PhD-Table.csv'
GraduateAdvising(csv_file=graduate_phd_file,
                 name='GraduateAdvisingPhD').write_table(path=path)

from tables import PostdoctoralAdvising
postdoctoral_file = 'CV/Postdoc-Table.csv'
PostdoctoralAdvising(csv_file=postdoctoral_file,
                     name='PostdoctoralAdvising').write_table(path=path)


from tables import Lectures
lectures_file = 'CV/Lectures-Table.csv'
Lectures(csv_file=lectures_file, name='Lectures').write_table(path=path)

from tables import Funding
funding_file = 'CV/Grants-Table.csv'
Funding(csv_file=funding_file, name='Funding').write_table(path=path)

from tables import Reviews
reviews_file = 'CV/Reviews-Table.csv'
Reviews(csv_file=reviews_file, name='Reviews').write_table(path=path)

service_file = 'CV/Service-Table.csv'
from tables import ProfessionalService
ProfessionalService(csv_file=service_file,
                    name='ProfessionalService').write_table(path=path)

from tables import UniversityService
UniversityService(csv_file=service_file,
                  name='UniversityService').write_table(path=path)

from tables import DepartmentalService
DepartmentalService(csv_file=service_file,
                    name='DepartmentalService').write_table(path=path)
