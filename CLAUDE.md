# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

biobib is a Python package built with nbdev that generates academic CVs and biobibs (bibliographies) from structured data sources. It reads data from Apple Numbers documents or Google Sheets and outputs formatted LaTeX files for CV generation and data for website publication lists.

**Key Purpose**: Automate the generation of formatted academic materials (CVs, publication lists, service records) from a single source of truth maintained in spreadsheet format.

## Development Workflow (nbdev)

This project uses **nbdev**, which means:

1. **All source code lives in Jupyter notebooks** in the `nbs/` directory
2. **Never edit files in `biobib/` directly** - they are auto-generated from notebooks
3. **To modify code**: Edit the corresponding notebook in `nbs/` then run `nbdev_export`

### Common Development Commands

```bash
# Export notebooks to Python modules (REQUIRED after editing notebooks)
nbdev_export

# Run tests defined in notebooks
nbdev_test

# Build documentation (Quarto-based)
nbdev_docs

# Preview documentation locally
nbdev_preview

# Clean notebooks (remove outputs, trailing whitespace)
nbdev_clean

# Prepare notebooks for git
nbdev_prepare  # Runs export, test, and clean

# Install package in development mode
pip install -e .
```

### Working with Notebooks

- Each numbered notebook in `nbs/` corresponds to a module in `biobib/`
  - `01_doc.ipynb` → `biobib/doc.py`
  - `02_table.ipynb` → `biobib/table.py`
  - `03_Service.ipynb` → `biobib/Service.py`
  - etc.
- Use `#| export` directive in cells to mark code for export to Python modules
- Use `#| hide` to hide cells from documentation
- `index.ipynb` generates both `README.md` and the documentation homepage

## Architecture

### Core Data Flow

1. **Data Source** → `Doc` or `NumbersDoc` class reads spreadsheet data
2. **Table Classes** → Specialized classes (Publications, Service, Funding, etc.) process and format data
3. **Templates** → Jinja2 templates with LaTeX syntax render formatted output
4. **Output** → Generated `.tex` files in `tex/` directory

### Key Classes and Modules

#### `biobib/doc.py` (from `nbs/01_doc.ipynb`)
- **`Doc`**: Interface to Google Sheets using `gspread` OAuth
- **`NumbersDoc`**: Interface to Apple Numbers documents using `numbers_parser`
- Both provide `get_dataframe(worksheet)` method to extract data as pandas DataFrames
- Requires environment variables (see Configuration below)

#### `biobib/table.py` (from `nbs/02_table.ipynb`)
- **`Table`**: Base class for all CV/biobib tables
- Handles data loading, template rendering, and LaTeX output
- Key methods:
  - `table_clean_df()`: Filters data based on category and review period
  - `render_template()`: Generates formatted text using Jinja2
  - `write_template(path)`: Writes output to `.tex` files
- Provides custom Jinja2 filters for LaTeX formatting:
  - `tex_escape`: Escapes special LaTeX characters
  - `colonify`, `stringify`, `reversed`: String utilities
  - `format_currency`: Formats dollar amounts
  - `make_cell`: Creates LaTeX table cells

#### Specialized Table Classes
Each inherits from `Table` and adds domain-specific logic:
- **`Publications`** (`nbs/04_Publications.ipynb`): Handles author decoration, bold PI names, group affiliations
- **`Service`** (`nbs/03_Service.ipynb`): University/departmental/professional service records
- **`Funding`** (`nbs/08_Funding.ipynb`): Grants and contracts
- **`Lectures`** (`nbs/07_Lectures.ipynb`): Presentations and talks
- **`Awards`** (`nbs/05_Awards.ipynb`): Honors and awards
- **`Proceedings`** (`nbs/11_Proceedings.ipynb`): Conference abstracts
- **`ProfessionalActivities`** (`nbs/12_ProfessionalActivities.ipynb`)

### Template System

Templates are in `templates/` with subdirectories for different output types:
- `templates/biobib/`: UC biobib format templates
- `templates/CV/`: CV-specific templates
- `templates/website/`: Website/Jekyll format

Templates use custom Jinja2 delimiters for LaTeX compatibility:
- `\BLOCK{...}` for control structures (instead of `{% %}`)
- `\VAR{...}` for variables (instead of `{{ }}`)
- `\#{...}` for comments

### Configuration

Required environment variables (stored in `.env`, not version controlled):
```bash
NUMBERS_PATH=/path/to/Numbers/Documents
WEB_DIR=/path/to/website/directory
SCHOLAR_API_KEY=your_semantic_scholar_api_key
BOX_DIR=/path/to/publications/storage  # optional
```

The main data source is typically `CV.numbers` in the `NUMBERS_PATH` directory.

### Data Structure Conventions

Worksheets in the Numbers/Google Sheet document typically include:
- **Publications**: Author columns A1-A30, publication metadata, category (P=Published, A=In Press, R=In Review)
- **Service**: Type (P=Professional, U=University, D=Departmental), Year, Role, Committee
- **Funding**: Grant details with currency formatting
- **Eval column**: Used for filtering review periods (1 = current period) when `cumulative=False`

Author decoration system uses special markers:
- `-UUUU-`: Undergraduate author → `$^{\ddagger}$`
- `-VVVV-`: Visiting author → `$^{\star}$`
- `-AAAA-`: Graduate advisee → `$^{\blacktriangle}$`
- `-PPPP-`: Postdoctoral advisee → `$^{\blacklozenge}$`
- `-MMMM-`: PhD committee member → `$^{\bullet}$`

## Testing and Documentation

Tests are embedded in notebooks and run with `nbdev_test`. The framework uses `fastcore.test` functions like `test_eq`.

Documentation is built with Quarto and configured in `_quarto.yml`:
- Output directory: `_docs/`
- Preview port: 3000
- Deployed to GitHub Pages via `.github/workflows/deploy.yaml`

## Common Tasks

### Generating CV Components

```python
from biobib.doc import NumbersDoc
from biobib.Publications import Publications
from biobib.Service import Service

# Load data
doc = NumbersDoc("CV.numbers")

# Generate publications list
pubs = Publications(doc=doc, worksheet='Publications',
                    bold_author=True, decorate_groups=True,
                    cumulative=True)
pubs.write_template(path='tex/CV/')

# Generate service records
service = Service(doc=doc, worksheet='Service',
                  category='U',  # University service
                  cumulative=False)
service.write_template(path='tex/CV/')
```

### Adding a New Table Type

1. Create new notebook in `nbs/` (e.g., `13_NewType.ipynb`)
2. Define class inheriting from `Table`
3. Create corresponding template in `templates/`
4. Add `#| export` directive to cells that should be exported
5. Run `nbdev_export` to generate Python module
6. Run `nbdev_test` to verify

### LaTeX Compilation

The generated `.tex` files are typically included in a main CV document. The repository contains CV templates in the root (e.g., `CV - Caylor.tex`) that pull in generated content from `tex/CV/`.

## Integration Points

- **Semantic Scholar API** (`biobib/scholar.py`): Fetches citation data and paper metadata
- **Website Generation** (`biobib/website.py`): Outputs publication data for Jekyll-based academic websites
- **Google Sheets**: Alternative to Numbers for collaborative data management (requires OAuth credentials in `credentials.json`)
