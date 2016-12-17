#!/usr/bin/env python

"""
Suppress output and prompt numbers in git version control.

This script will tell git to preserve prompt numbers and cell output
only when looking at ipynb files if their metadata contains:

    "git" : { "preserve_output" : true }

The notebooks themselves are not changed.

See also this blogpost: http://pascalbugnion.net/blog/ipython-notebooks-and-git.html.

Modified by Michael S. Hansen (michael.schacht.hansen@gmail.com) to 

1. Filter unless preserve_output is true.
2. Added option to preserve_output on individual cells.
3. Added execution_count to list of of stuff that gets removed. 
4. Changed instructions to add the script to the repo instead. 

Usage instructions
==================

1. Put this script in a directory within the repo, say `scripts/ipynb_drop_output.py`
2. Make sure it is executable by typing the command
   `chmod +x scripts/ipynb_drop_output.py`.
3. Register a filter for ipython notebooks by
   putting the following line in `.gitattributes`:
   `*.ipynb filter=clean_ipynb`
4. Connect this script to the filter by adding the following to `.git/config` in the repo:

   [filter "clean_ipynb"]
	smudge = cat
	clean = $(git rev-parse --git-dir)/../scripts/ipynb_drop_output.py

To tell git to preserve the output and prompts for a notebook,
open the notebook's metadata (Edit > Edit Notebook Metadata). A
panel should open containing the lines:

    {
        "name" : "",
        "signature" : "some very long hash"
    }

Add an extra line so that the metadata now looks like:

    {
        "name" : "",
        "signature" : "don't change the hash, but add a comma at the end of the line",
        "git" : { "preserve_outputs" : true }
    }

You may need to "touch" the notebooks for git to actually register a change, if
your notebooks are already under version control.

To preserve the output for a single cell, edit the cell metadata:

1. (View > Cell Toobar > Edit Metadata)
2. Click edit metadata button
3. Add:
   "git" : { "preserve_output" : true }

Notes
=====

This script is inspired by http://stackoverflow.com/a/20844506/827862, but 
lets the user specify whether the ouptut of a notebook should be suppressed
in the notebook's metadata, and works for IPython v3.0
"""

import sys
import json

nb = sys.stdin.read()

json_in = json.loads(nb)
nb_metadata = json_in["metadata"]
suppress_output = True
if "git" in nb_metadata:
    if "preserve_outputs" in nb_metadata["git"] and nb_metadata["git"]["preserve_outputs"]:
        suppress_output = False
if not suppress_output:
    sys.stdout.write(nb)
    exit() 


ipy_version = int(json_in["nbformat"])-1 # nbformat is 1 more than actual version.

def strip_output_from_cell(cell):
    del_o = True
    if "metadata" in cell and "git" in cell["metadata"] and "preserve_output" in cell["metadata"]["git"] and cell["metadata"]["git"]["preserve_output"]:
        del_o = False
    if "outputs" in cell and del_o:
        cell["outputs"] = []
    if "prompt_number" in cell:
        del cell["prompt_number"]
    if "execution_count" in cell:
        del cell["execution_count"]
            
if ipy_version == 2:
    for sheet in json_in["worksheets"]:
        for cell in sheet["cells"]:
            strip_output_from_cell(cell)
else:
    for cell in json_in["cells"]:
        strip_output_from_cell(cell)

json.dump(json_in, sys.stdout, sort_keys=True, indent=1, separators=(",",": "))
