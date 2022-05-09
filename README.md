# BibCom -- a BibTeX bibliography creator
The Biblography Compiler (BibCom) is a simple tool for automatically populating a BibTeX bibliography file for physics (and possibly other) papers.


## Summary

Creating bibliography for scientific papers or theses can take up significant amounts of time.
In physics, popular data bases such as [ADS](https://adsabs.harvard.edu) or [Inspire HEP](https://inspirehep.net/) with BibTeX have made this task fairly simple.

However, adding new entries one by one or a few at a time from these databases can still be time-consuming. The same is true for choosing citation keys and adjusting the bib file accordingly. Long arguments between co-authors about unique and persistent vs memorable keys can ensue.

This tool can mitigate these problems by automatically generating bib entries for missing citations.
The user may populates a bib file by copying the missing entries to the clipboard (good for online tools such as Overleaf) or appending a bib file on disk.
The only requirement is that the keys used in the file are _any_ the following persistent identifiers:

- an [arXiv](https://arxiv.org/) preprint number (with or without `arXiv:` in front)
- a DOI (with or without `doi:` in front)
- an Inspire key

The preferred database for queries is ADS; Inspire is used as a fallback option. To use ADS you have to create an account and generate an API token for ADS, which [is explained below](#recommend-additional-steps).


## How to install

### Minimal install

To install, simply clone the repository
```
git clone https://github.com/sebhoof/bibcom
```
and make sure that your local Python supports the following packages: `numpy`, `pyperclip`, and `requests`. The only uncommon package is `pyperclip`, which allows the output of a string to be copied into the clipboard. If in doubt, run
```
python -m pip install numpy pyperclip requests
```

### Recommended additional steps

You may create an ADS account following [this link](https://ui.adsabs.harvard.edu/user/account/register).
Apart from getting an API token, this is also useful for creating a custom email alerts for new arXiv papers (no, I am not affiliated with ADS). You can then generate the API token under `Account -> Settings -> API Token`. Paste it into a plain text file and save the file as e.g. `my.token` in your local copy of this repository.

- [ ] Consider adding a `make_install.sh` that appends the path to the `${PATH}` variable

## How to use

Simply invoke the script on the log file created by LaTeX. If you main file is named `main.tex`, a log file named `main.log` should be present in the in the same folder as `main.tex`. Running
```
python compile_bibliography.py main.log
```
will copy the missing bib entries into your clipboard and you can paste them into your bib file.

To use ADS, you need to also supply your ADS token, e.g. named `my.token`.

If you provide the name of a bib file, say `/some/folder/my.bib`, the results will be appended to the file and not just pasted to the clipboard. The code will test your bib file for duplicates afterwards.

The order of the arguments is _not_ relevant as long as the files end in `.log`, `.bib`, and `.token`. For example, you may call
```
python compile_bibliography.py main.log /some/folder/my.bib my.token
```

The ADS BibTeX entries use LaTeX macros to abbreviate some of the commonly encountered journal names, as described [here](https://ui.adsabs.harvard.edu/help/actions/journal-macros).
For convenience, this repo contains the file [jdefs.tex](jdefs.tex), which you can include in your main LaTeX file preamble via `\include{jdefs}` to take care of this.


## Citation
If this tool has saved you some time and enabled your research, please consider acknowledging it in your work using the BibTeX entry below or -- better still! -- by generating it automatically by putting `\cite{doi:}` in your paper and letting the tool do the rest for you.

```
@MISC{doi:,
}
```
