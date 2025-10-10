# 🌾 METGO 3D - Sphinx Configuration
# Sistema Meteorológico Agrícola Quillota - Versión Operativa 2.0

# Configuration file for the Sphinx documentation builder.

import os
import sys
sys.path.insert(0, os.path.abspath('.'))

# Project information
project = 'METGO 3D'
copyright = '2025, Sistema Meteorológico Agrícola Quillota'
author = 'METGO 3D Team'
release = '2.0.0'
version = '2.0.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.mathjax',
    'sphinx.ext.ifconfig',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.napoleon',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

# Options for LaTeX output
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    ('index', 'METGO_3D.tex', 'METGO 3D Documentation',
     'METGO 3D Team', 'manual'),
]

# Options for manual page output
man_pages = [
    ('index', 'metgo_3d', 'METGO 3D Documentation',
     [author], 1)
]

# Options for Texinfo output
texinfo_documents = [
    ('index', 'METGO_3D', 'METGO 3D Documentation',
     author, 'METGO_3D', 'Sistema Meteorológico Agrícola Quillota',
     'Miscellaneous'),
]

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
    'seaborn': ('https://seaborn.pydata.org/', None),
    'sklearn': ('https://scikit-learn.org/stable/', None),
    'plotly': ('https://plotly.com/python/', None),
    'streamlit': ('https://docs.streamlit.io/', None),
}

# Napoleon settings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# MyST settings
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Todo extension settings
todo_include_todos = True

# Coverage extension settings
coverage_show_missing_items = True
coverage_ignore_modules = []
coverage_ignore_functions = []
coverage_ignore_classes = []

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Add any paths that contain custom static files
html_static_path = ['_static']

# Custom sidebar templates
html_sidebars = {
    '**': [
        'relations.html',
        'sourcelink.html',
        'searchbox.html',
    ]
}

# Output file base name for HTML help builder
htmlhelp_basename = 'METGO_3Ddoc'
