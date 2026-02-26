# Merged Service and Professional Activities module

from .table import Table, tex_escape
from .doc import Doc, NumbersDoc
from .Service import Service, consolidate_years as service_consolidate_years
from .ProfessionalActivities import (ProfessionalActivities, SpecialAppointments,
                                      combine_years, extract_years)
import pandas as pd
import re

__all__ = ['ServiceActivities', 'service_activities_cv_template', 'service_activities_selected_cv_template', 'filter_selected_activities']

# Keywords for filtering selected/important activities
INCLUDE_KEYWORDS = ['Chair', 'Director', 'Editor', 'Board', 'Lead', 'Vice Chancellor',
                    'Panel', 'Reviewer', 'Convenor', 'Officer', 'President', 'Head',
                    'Co-Convenor', 'Organizer', 'Co-Chair']
EXCLUDE_KEYWORDS = ['Member', 'Mentor', 'Advisor', 'Participating', 'Ex-Officio', 'Faculty Advisor']

# Roles that are single events, not ongoing positions (should not show "Present")
SINGLE_EVENT_ROLES = ['Moderator', 'Panelist', 'Reviewer', 'Convenor', 'Co-Convenor',
                      'Organizer', 'Co-Chair', 'Participant', 'Speaker', 'Keynote']

service_activities_cv_template = r'''% CV Service and Professional Activities Table
% Created on \VAR{created}

\begin{longtable}{l p{5.5in}}

\endfirsthead
\multicolumn{2}{l}{\hspace{.1in} \textsc{\underline{Service \& Professional Activities}} -- continued
\vspace*{.1in} }  \endhead

\BLOCK{for item in items}
\VAR{item.Year} & \VAR{item.Activity|tex_escape} \\
\BLOCK{endfor}

\end{longtable}
'''

service_activities_selected_cv_template = r'''% CV Selected Service and Professional Activities Table
% Created on \VAR{created}

\begin{longtable}{l p{5.5in}}

\endfirsthead
\multicolumn{2}{l}{\hspace{.1in} \textsc{\underline{Selected Service \& Professional Activities}} -- continued
\vspace*{.1in} }  \endhead

\BLOCK{for item in items}
\VAR{item.Year} & \VAR{item.Activity|tex_escape} \\
\BLOCK{endfor}

\end{longtable}
'''


def filter_selected_activities(df, include_keywords=None, exclude_keywords=None):
    """
    Filter activities to only include significant/leadership roles.

    The filter checks the ROLE portion of the activity (before the first comma)
    to determine if it's a leadership/significant role.
    """
    if include_keywords is None:
        include_keywords = INCLUDE_KEYWORDS
    if exclude_keywords is None:
        exclude_keywords = EXCLUDE_KEYWORDS

    def should_include(row):
        activity = str(row.get('Activity', row.get('Role', '')))

        # Extract the role portion (before the first comma) for checking
        # e.g., "Member, Dangermond Chair Search Committee" -> "Member"
        role_part = activity.split(',')[0].strip().lower()

        # Check if role has any include keyword
        has_include = any(kw.lower() in role_part for kw in include_keywords)

        # Check if role has any exclude keyword
        has_exclude = any(kw.lower() in role_part for kw in exclude_keywords)

        # Include if role has an include keyword
        # Exclude if role has an exclude keyword and no include keyword
        if has_include:
            return True
        if has_exclude:
            return False
        # Keep items that are neither (specific named roles)
        return True

    return df[df.apply(should_include, axis=1)]


def consolidate_reviews(df):
    """
    Group tenure/promotion reviews by year into single lines.
    E.g., multiple "Tenure case reviewer" entries in 2021 become:
    "2021 | Tenure reviewer: Duke University, Michigan State University"
    """
    # Identify review entries
    review_keywords = ['Tenure case reviewer', 'Promotion case reviewer',
                       'Tenure reviewer', 'Promotion reviewer', 'External Reviewer']

    # Split into reviews and non-reviews
    def is_review(row):
        role = str(row.get('Role', ''))
        return any(kw.lower() in role.lower() for kw in review_keywords)

    reviews = df[df.apply(is_review, axis=1)].copy()
    non_reviews = df[~df.apply(is_review, axis=1)].copy()

    if len(reviews) == 0:
        return df

    # Normalize review types
    def get_review_type(role):
        role_lower = role.lower()
        if 'tenure' in role_lower:
            return 'Tenure reviewer'
        elif 'promotion' in role_lower:
            return 'Promotion reviewer'
        elif 'external' in role_lower:
            return 'External reviewer'
        return role

    reviews['ReviewType'] = reviews['Role'].apply(get_review_type)

    # Extract year as integer for grouping
    def get_year_int(year_str):
        year_str = str(year_str).strip()
        match = re.match(r'(\d{4})', year_str)
        if match:
            return int(match.group(1))
        return None

    reviews['YearInt'] = reviews['Year'].apply(get_year_int)
    reviews = reviews.dropna(subset=['YearInt'])
    reviews['YearInt'] = reviews['YearInt'].astype(int)

    # Group by year and review type
    grouped_reviews = []
    for (year, review_type), group in reviews.groupby(['YearInt', 'ReviewType']):
        orgs = group['Organization'].tolist()
        # Clean up organization names
        orgs = [str(o).strip() for o in orgs if pd.notna(o) and str(o).strip()]
        if orgs:
            activity = f"{review_type}: {'; '.join(orgs)}"
            grouped_reviews.append({
                'Year': str(year),
                'Activity': activity,
                'SortYear': year
            })

    grouped_df = pd.DataFrame(grouped_reviews)

    # Convert non-reviews to Activity format
    non_reviews_list = []
    for _, row in non_reviews.iterrows():
        role = str(row.get('Role', '')).strip()
        org = str(row.get('Organization', row.get('Committee', ''))).strip()

        if role and org:
            activity = f"{role}, {org}"
        elif role:
            activity = role
        elif org:
            activity = org
        else:
            continue

        year_str = str(row.get('Year', '')).strip()
        year_int = get_year_int(year_str)

        non_reviews_list.append({
            'Year': year_str,
            'Activity': activity,
            'SortYear': year_int if year_int else 0
        })

    non_reviews_df = pd.DataFrame(non_reviews_list)

    # Combine
    result = pd.concat([grouped_df, non_reviews_df], ignore_index=True)
    result = result.sort_values('SortYear', ascending=False)

    return result


class ServiceActivities(Table):
    """
    A merged Service and Professional Activities table for CVs
    """
    def __init__(
            self,
            doc: Doc = None,
            cumulative: bool = True,
            consolidate: bool = True,
            consolidate_reviews: bool = True,
            selected: bool = False,  # If True, filter to only significant/leadership roles
            template = service_activities_cv_template,
            table_name: str = 'ServiceActivities'
    ):
        # Don't call super().__init__ with worksheet since we're loading multiple
        self.doc = doc
        self.cumulative = cumulative
        self.consolidate = consolidate
        self.consolidate_reviews_flag = consolidate_reviews
        self.selected = selected
        self.table_name = table_name
        self.template = template

        # Import the latex environment from table module
        from .table import latex_env
        self.env = latex_env
        self.template = self.env.from_string(template)

        # Load and merge all tables
        self.df = self._load_and_merge()

        # Apply filtering if selected=True
        if self.selected:
            original_count = len(self.df)
            self.df = filter_selected_activities(self.df)
            print(f'Filtered from {original_count} to {len(self.df)} selected entries')

        print(f'Initialized {self.table_name} table with {len(self.df)} entries')

    def _load_and_merge(self):
        """Load Service, Professional Activities, and Special Appointments and merge them."""
        all_data = []

        # Load Service
        try:
            service = Service(
                doc=self.doc,
                worksheet='Service',
                table_name='_temp_service',
                cumulative=self.cumulative,
                consolidate=self.consolidate,
                ascending=False
            )
            # Convert to Activity format
            for _, row in service.df.iterrows():
                role = str(row.get('Role', '')).strip()
                committee = str(row.get('Committee', '')).strip()
                if role and committee:
                    activity = f"{role}, {committee}"
                elif role:
                    activity = role
                elif committee:
                    activity = committee
                else:
                    continue
                all_data.append({
                    'Year': str(row.get('Year', '')),
                    'Role': role,
                    'Organization': committee,
                    'Activity': activity
                })
        except Exception as e:
            print(f"Warning: Could not load Service: {e}")

        # Load Professional Activities
        try:
            prof_act = ProfessionalActivities(
                doc=self.doc,
                worksheet='Additional Professional Activit',
                table_name='_temp_profact',
                cumulative=self.cumulative,
                consolidate=self.consolidate,
                ascending=False
            )
            for _, row in prof_act.df.iterrows():
                role = str(row.get('Role', '')).strip()
                org = str(row.get('Organization', '')).strip()
                if role and org:
                    activity = f"{role}, {org}"
                elif role:
                    activity = role
                elif org:
                    activity = org
                else:
                    continue
                all_data.append({
                    'Year': str(row.get('Year', '')),
                    'Role': role,
                    'Organization': org,
                    'Activity': activity
                })
        except Exception as e:
            print(f"Warning: Could not load Professional Activities: {e}")

        # Load Special Appointments
        try:
            special = SpecialAppointments(
                doc=self.doc,
                worksheet='Special Appointments',
                table_name='_temp_special',
                cumulative=self.cumulative,
                consolidate=self.consolidate,
                ascending=False
            )
            for _, row in special.df.iterrows():
                role = str(row.get('Role', '')).strip()
                org = str(row.get('Organization', '')).strip()
                if role and org:
                    activity = f"{role}, {org}"
                elif role:
                    activity = role
                elif org:
                    activity = org
                else:
                    continue
                all_data.append({
                    'Year': str(row.get('Year', '')),
                    'Role': role,
                    'Organization': org,
                    'Activity': activity
                })
        except Exception as e:
            print(f"Warning: Could not load Special Appointments: {e}")

        df = pd.DataFrame(all_data)

        # Consolidate reviews if requested
        if self.consolidate_reviews_flag and len(df) > 0:
            df = consolidate_reviews(df)

        # Get current year for "Present" conversion and sorting
        import datetime
        current_year = datetime.datetime.now().year

        # Convert current year to "Present" for ranges (ongoing items)
        # but not for single-event roles like Moderator, Panelist, etc.
        def format_year_with_present(row):
            year_str = str(row.get('Year', ''))
            activity = str(row.get('Activity', row.get('Role', '')))

            # Check if this is a single-event role
            role_part = activity.split(',')[0].strip()
            is_single_event = any(kw.lower() in role_part.lower() for kw in SINGLE_EVENT_ROLES)

            # Don't convert to "Present" for single-event roles
            if is_single_event:
                return year_str

            # Replace ending current year with "Present" for ranges
            # e.g., "2023 - 2026" -> "2023 - Present"
            if f" - {current_year}" in year_str:
                return year_str.replace(f" - {current_year}", " - Present")
            # Single current year stays as-is (e.g., "2026" stays "2026")
            return year_str

        # Apply "Present" formatting (pass whole row to check role type)
        df['Year'] = df.apply(format_year_with_present, axis=1)

        # Also update Activity field if it contains the year
        def update_activity_year(row):
            activity = str(row.get('Activity', ''))
            if f" - {current_year}" in activity:
                return activity.replace(f" - {current_year}", " - Present")
            return activity

        if 'Activity' in df.columns:
            df['Activity'] = df.apply(update_activity_year, axis=1)

        # Add sort columns
        df['_is_ongoing'] = df['Year'].apply(lambda x: 1 if "Present" in str(x) else 0)
        df['_start_year'] = df['Year'].apply(lambda x: int(re.match(r'(\d{4})', str(x)).group(1)) if re.match(r'(\d{4})', str(x)) else 0)

        # Sort: ongoing first, then by start year descending
        df = df.sort_values(['_is_ongoing', '_start_year'], ascending=[False, False])
        df = df.drop(columns=['_is_ongoing', '_start_year'])

        return df

    def render_template(self):
        """Generate text for this table using the table's template."""
        import time
        rendered_tex = self.template.render(
            table_name=self.table_name,
            created=time.strftime("%Y-%m-%d %H:%M"),
            items=list(self.df.to_dict('records'))
        )
        return rendered_tex

    def write_template(self, path=None):
        """Write out the contents of this table using the table's template."""
        content = self.render_template()
        if path:
            file = path + self.table_name + '.tex'
        else:
            file = self.table_name + '.tex'

        with open(file, "w") as f:
            print(content, file=f)
