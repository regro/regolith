# -*- coding: utf-8 -*-
#
# xo documentation build configuration file, created by
# sphinx-quickstart on Sun Jan 27 00:12:33 2013.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out
# serve to show the default.

import json
import sys
import tempfile
import time
from collections.abc import MutableMapping
from importlib.metadata import version
from pathlib import Path
from subprocess import check_output
from textwrap import indent

from regolith.fsclient import _id_key, dump_json, json_to_yaml
from regolith.main import CONNECTED_COMMANDS, DISCONNECTED_COMMANDS
from regolith.schemas import EXEMPLARS, SCHEMAS

# autodoc_mock_imports = [
#    regolith,
# ]

sys.path.insert(0, str(Path("../..").resolve()))
sys.path.insert(0, str(Path("../../src").resolve()))  # abbreviations
ab_authors = "Billinge Group members and community contributors"


# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('.'))

# -- General configuration -----------------------------------------------------

# If your documentation needs a minimal Sphinx version, state it here.
# needs_sphinx = '1.0'

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "sphinx.ext.mathjax",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_rtd_theme",
    "m2r",
]

napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = [".rst", "md"]

# The encoding of source files.
# source_encoding = 'utf-8-sig'

# The master toctree document.
master_doc = "index"

# General information about the project.
project = "regolith"
copyright = "2015-2017 Anthony Scopatz, 2018-%Y The Trustees of Columbia University in the City of New York"

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
fullversion = version(project)
version = "".join(fullversion.split(".post")[:1])

# The full version, including alpha/beta/rc tags.
release = fullversion

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
# language = None

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
# today = ''
# Else, today_fmt is used as the format for a strftime call.
# today_fmt = '%B %d, %Y'
today = time.strftime("%B %d, %Y", time.localtime())
year = today.split()[-1]
copyright = copyright.replace("%Y", year)

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "build"]

# The reST default role (used for this markup: `text`) to use for all documents.
# default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
# pygments_style = 'sphinx'
pygments_style = "sphinx"

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ["regolith"]
nitpicky = True

# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "sphinx_rtd_theme"
# html_theme = 'blackcloud'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
# html_theme_options = {}
html_theme_options = {"roottarget": "index", "navigation_with_keys": "true"}

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []
# html_theme_path = [csp.get_theme_dir()]
# html_theme_path = ["_themes", csp.get_theme_dir()]

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "regolith - software group content management system"

# A shorter title for the navigation bar.  Default is the same as html_title.
html_short_title = "regolith"

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/regolith-logo.svg"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = "_static/regolith-logo.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
html_domain_indices = False

# If false, no index is generated.
html_use_index = False

# If true, the index is split into individual pages for each letter.
html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = False

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = False

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
# html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Output file base name for HTML help builder.
basename = "regolith-docs".replace(" ", "").replace(".", "")
htmlhelp_basename = basename + "doc"

# -- Options for LaTeX output --------------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    # 'papersize': 'letterpaper',
    # The font size ('10pt', '11pt' or '12pt').
    # 'pointsize': '10pt',
    # Additional stuff for the LaTeX preamble.
    # 'preamble': '',
}

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    (
        "index",
        "regolith.tex",
        "Regolith Documentation",
        ab_authors,
        "manual",
    )
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# If true, show page references after internal links.
# latex_show_pagerefs = False

# If true, show URL addresses after external links.
# latex_show_urls = False

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_domain_indices = True


# -- Options for manual page output --------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [("index", "regolith", "regolith docs", ab_authors, 1)]

# If true, show URL addresses after external links.
# man_show_urls = False


# -- Options for Texinfo output ------------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (
        "index",
        "regolith",
        "regolith Documentation",
        ab_authors,
        "regolith",
        "Research group management software.",
        "Miscellaneous",
    )
]


# Documents to append as an appendix to all manuals.
# texinfo_appendices = []

# If false, no module index is generated.
# texinfo_domain_indices = True

# How to display URL addresses: 'footnote', 'no', or 'inline'.
# texinfo_show_urls = 'footnote'


def format_key(schema, key, indent_str=""):
    s = ""
    if key == "schema" or key == "required":
        return s
    line_format = ":{key}: {type}, {description}, required\n"
    line_format_o = ":{key}: {type}, {description}, optional\n"
    if not schema.get("required", False):
        lf = line_format_o
    else:
        lf = line_format
    if "type" in schema.get(key, {}) or "anyof_type" in schema.get(key, {}):
        schema = schema[key]
    if "type" in schema or "anyof_type" in schema:
        s += indent(
            lf.format(
                key=key,
                description=schema.get("description", ""),
                type=schema.get("type", schema.get("anyof_type", "")),
            ),
            indent_str,
        )
    allowed = schema.get("allowed", "") or schema.get("eallowed", "")
    if allowed:
        s += indent("\nAllowed values: \n", indent_str + "\t")
        for allow in allowed:
            if allow:
                s += indent("* {}\n".format(allow), indent_str + "\t" * 2)
            else:
                s += indent("* ``''``\n", indent_str + "\t" * 2)
    s = s.replace(", , ", ", ")
    if schema.get("schema", False):
        s += "\n"
    for inner_key in schema.get("schema", ()):
        s += format_key(schema["schema"], inner_key, indent_str=indent_str + "\t")

    return s


def build_schema_doc(key):
    fn = "collections/" + key + ".rst"
    with open(fn, "w") as f:
        s = ""
        s += key.title() + "\n"
        s += "=" * len(key) + "\n"
        s += SCHEMAS[key]["_description"]["description"] + "\n\n"
        s += "Schema\n------\nThe following lists key names mapped to its " "type and meaning for each entry.\n\n"
        schema = SCHEMAS[key]
        schema_list = list(schema.keys())
        schema_list.sort()
        for k in schema_list:
            if k not in ["_description"]:
                s += format_key(schema[k], key=k)
        s += "\n\n"
        s += "YAML Example\n------------\n\n"
        s += ".. code-block:: yaml\n\n"
        temp = tempfile.NamedTemporaryFile()
        temp2 = tempfile.NamedTemporaryFile()
        documents = EXEMPLARS[key]
        if isinstance(documents, MutableMapping):
            documents = [documents]
        documents = {doc["_id"]: doc for doc in documents}
        dump_json(temp.name, documents)
        docs = sorted(documents.values(), key=_id_key)
        lines = [json.dumps(doc, sort_keys=True, indent=4, separators=(",", ": ")) for doc in docs]
        jd = "\n".join(lines)
        json_to_yaml(temp.name, temp2.name)
        with open(temp2.name, "r") as ff:
            s += indent(ff.read(), "\t")
        s += "\n\n"
        s += "JSON/Mongo Example\n------------------\n\n"
        s += ".. code-block:: json\n\n"
        s += indent(jd, "\t")
        s += "\n"
        f.write(s)


for k in SCHEMAS:
    build_schema_doc(k)


docs_not_in_schemas = ["citations", "courses", "jobs", "news"]
all_collection_docs = sorted(list(SCHEMAS.keys()) + docs_not_in_schemas)

collections_header = """.. _regolith_collections:

=================
Collections
=================
The following contain the regolith schemas and examples in both YAML and JSON/Mongo.

.. toctree::
    :maxdepth: 1

"""

collections_header += indent("\n".join(all_collection_docs), "    ")

with open("collections/index.rst", "w") as f:
    f.write(collections_header)


def build_cli_doc(cli):
    fn = "commands/" + cli + ".rst"
    out = check_output(["regolith", cli, "-h"]).decode("utf-8")
    s = "{}\n".format(cli) + "=" * len(cli) + "\n\n"
    s += ".. code-block:: bash\n\n"
    s += indent(out, "\t") + "\n"
    if cli == "validate":
        s += """Misc
----

This can also be added as a git hook by adding the following to
``.git/hooks/pre-commit``

.. code-block:: sh

    #!/bin/sh
    regolith validate

This can be enabled with ``chmod +x .git/hooks/pre-commit``"""
    with open(fn, "w") as f:
        f.write(s)


# build CLI docs
clis = sorted(set(CONNECTED_COMMANDS.keys()) | set(DISCONNECTED_COMMANDS.keys()))
for cli in clis:
    build_cli_doc(cli)

cli_index = """.. _commands:

=================
Regolith Commands
=================
Shell commands for regolith

{}

.. toctree::
    :maxdepth: 1

"""
cli_index += indent("\n".join(clis), "    ")
with open("commands/index.rst", "w") as f:
    out = check_output(["regolith", "-h"]).decode("utf-8")
    s = ".. code-block:: bash\n\n"
    s += indent(out, "\t") + "\n"
    f.write(cli_index.format(s))
