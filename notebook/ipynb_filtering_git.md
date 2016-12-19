Filtering output from Jupyter (ipynb) files before committing to git
-------------------------------------------------------------------------------

Jupyter (`*.ipynb`) notebook files are great for storing a mixture of notes, code, and analysis. As such, they form a great basis for an electronic notebook, especially for people doing software development, signal processing, and data science. When using them in a notebook structure, it is desirable to store them in some sort of repository that keeps track of revision history. Git is the source code management tool of choice for many, but ipynb files are not well suited for storing in git repos. The main problem is that all the output is stored inline with the source code (actual code and markdown commentary). The files also store indexes that indicate the order of the cells. If you pick up a note book at run it again, lots of output is likely to change and the file will look as if changed and will get committed again. The quickly bloats the repository. 

What one would like to do is to store only the source changes (unless explicitly stated). There have been multiple solutions to this proposed in various places. Here is one inspired by this [blog post](http://pascalbugnion.net/blog/ipython-notebooks-and-git.html) and associated code. The script and behavior has been modified slightly here. 

The basic idea is to use a git filter. A git filter associates a certain file type to a driver, which can be specified either locally in the `.git/config` file or globally in `~/.gitconfig`. The git filter association is done in the `.gitattributes` file. Specifically, the `.gitattributes` would contain something like:
```
*.ipynb filter=clean_ipynb
```
which means that all notbook files will be passed through a filter driver called `clean_ipynb`. A filter drive has two functions: 1)  a `clean` function, which is the filtering applied to a file in the working repository before it is checked in or staged, and 2) a `smudge` function, which is what happens when the file is checked out and put in the working directory. In the case of the `*.ipynb` files, we want to remove output and some other stuff when checking the file in and when checking it out, we don't need to do anything do it. The filter operations can be specified like this:
```
git config --local filter.clean_ipynb.clean ipynb_drop_output
git config --local filter.clean_ipynb.smudge cat
```
i.e., when checking a file in, it will be passed to a command called `ipynb_drop_output` and when it is checked back out again, it will simply pass through `cat` and nothing will happen to the file. The command `ipynb_drop_output` needs to be somewhere in the `PATH` so that git can find it. Often times the filter script may be part of the actual repo. In that case, one could add something like this to the `.git/config` file:
```
[filter "clean_ipynb"]
	smudge = cat
	clean = $(git rev-parse --git-dir)/../scripts/ipynb_drop_output.py
```
Once such cleaning script can be found in [this gist](https://gist.github.com/pbugnion/ea2797393033b54674af). This script will remove output when the following is found in the notbook metadata:
```
"git" : { "suppress_output" : true }
```
When using this in a notebook, the desired default behavior is to remove most of the output, so the script has been modified so that:
1. It removes output unless `"git" : { "preserve_outputs" : true }` is found in the metadata. 
2. It is possible to add `"git" : { "preserve_output" : true }` to the metadata of a single cell, if only some of the cells should keep their output.
The modified can be found [here](../scripts/ipynb_drop_output.py)

