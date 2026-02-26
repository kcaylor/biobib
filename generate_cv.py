#!/usr/bin/env python
"""
Generate all CV components from CV.numbers file
"""

from biobib.doc import NumbersDoc
from biobib.Publications import Publications, publication_cv_template
from biobib.Service import Service, service_template, service_cv_template
from biobib.Awards import Awards, award_cv_template
from biobib.Proceedings import Proceedings, proceedings_cv_template
from biobib.ProfessionalActivities import (ProfessionalActivities, SpecialAppointments,
    professional_activities_template, professional_activities_cv_template, special_appointments_cv_template)
from biobib.Funding import Funding, funding_cv_template
from biobib.Lectures import Lectures, lecture_cv_template
from biobib.ServiceActivities import ServiceActivities, service_activities_cv_template, service_activities_selected_cv_template

# Load the Numbers document
print("Loading CV.numbers...")
sheet_name = "CV.numbers"
num_doc = NumbersDoc(sheet_name, default_table="Table 1")
print(f"✓ Loaded {sheet_name}")

# Output path
path = 'tex/CV/'
cumulative = True

print("\nGenerating CV components...")

# Publications
print("  - Publications (Published)...")
try:
    pubs = Publications(
        doc=num_doc,
        worksheet='Publications',
        table_name='Publications',
        template=publication_cv_template,
        bold_author=True,
        decorate_groups=True,
        cumulative=cumulative,
        category='P'
    )
    pubs.write_template(path=path)
    print("    ✓ Publications generated")
except Exception as e:
    print(f"    ✗ Error: {e}")

# In Press
print("  - In Press publications...")
try:
    in_press = Publications(
        doc=num_doc,
        worksheet='Publications',
        table_name='In Press',
        template=publication_cv_template,
        bold_author=True,
        decorate_groups=True,
        cumulative=cumulative,
        category='A'
    )
    in_press.write_template(path=path)
    print("    ✓ In Press generated")
except Exception as e:
    print(f"    ✗ Error: {e}")

# Proceedings
print("  - Conference Proceedings...")
try:
    proceedings = Proceedings(
        doc=num_doc,
        worksheet='Conference Abstracts',
        table_name='Proceedings',
        template=proceedings_cv_template,
        bold_author=True,
        decorate_groups=False,
        cumulative=cumulative
    )
    proceedings.write_template(path=path)
    print("    ✓ Proceedings generated")
except Exception as e:
    print(f"    ✗ Error: {e}")

# Service and Professional Activities (merged) - Full version
print("  - Service & Professional Activities (full)...")
try:
    service_activities = ServiceActivities(
        doc=num_doc,
        table_name='ServiceActivities',
        template=service_activities_cv_template,
        cumulative=cumulative,
        consolidate=True,
        consolidate_reviews=True,  # Group tenure/promotion reviews by year
        selected=False  # Full version - all entries
    )
    service_activities.write_template(path=path)
    print("    ✓ Service & Professional Activities (full) generated")
except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Service and Professional Activities (merged) - Selected version
print("  - Service & Professional Activities (selected)...")
try:
    service_activities_selected = ServiceActivities(
        doc=num_doc,
        table_name='ServiceActivitiesSelected',
        template=service_activities_selected_cv_template,  # Use selected template with different title
        cumulative=cumulative,
        consolidate=True,
        consolidate_reviews=True,
        selected=True  # Selected version - only leadership/significant roles
    )
    service_activities_selected.write_template(path=path)
    print("    ✓ Service & Professional Activities (selected) generated")
except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Funding
print("  - Funding...")
try:
    funding = Funding(
        doc=num_doc,
        worksheet='Grants',
        table_name='Funding',
        template=funding_cv_template,
        cumulative=True
    )
    funding.write_template(path=path)
    print("    ✓ Funding generated")
except Exception as e:
    print(f"    ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Awards
print("  - Awards...")
try:
    awards = Awards(
        doc=num_doc,
        worksheet='Awards',
        table_name='Awards',
        template=award_cv_template,
        cumulative=cumulative
    )
    awards.write_template(path=path)
    print("    ✓ Awards generated")
except Exception as e:
    print(f"    ✗ Error: {e}")


# Lectures
print("  - Lectures...")
try:
    lectures = Lectures(
        doc=num_doc,
        worksheet='Lectures',
        table_name='Lectures',
        template=lecture_cv_template,
        cumulative=cumulative
    )
    lectures.write_template(path=path)
    print("    ✓ Lectures generated")
except Exception as e:
    print(f"    ✗ Error: {e}")

print(f"\n✓ All CV components generated in {path}")
print("\nNext step: Compile LaTeX CV to PDF")
