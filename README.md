# wikidump

Framework for the extraction of features from Wikipedia XML dumps.

## Installation
This project has been tested with Python 3.5.0 and Python 3.8.5.

You need to install dependencies first, as usual.
```sh
pip install -r requirements.txt
```

## Usage

You need to download Wikipiedia dumps first:
```sh
./download.sh
```

Then run the extractor:
```sh
python -m wikidump [PROGRAM_OPTIONS] FILE [FILE ...]  OUTPUT_DIR [PROGRAM_OPTIONS] FUNCTION [FUNCTION_OPTIONS]
```

Or you can change edit the variables in the `Makefile` and use `GNU/Make` to run the program on the dump you are interested in.

For example if you want to launch the program on the English dump, after downloading it you can write:

```sh
make run-en
```

### Examples of use

### Retrieve the languages known by each user according to their last revision

If you are interested in extracting the languages known by the users of the Catalan Wikipedia based on the latest revision of their user page and compress the output using gzip you can type:

```sh
python -m wikidump --output-compression gzip dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output extract-known-languages --only-pages-with-languages --only-revisions-with-languages --only-last-revision
```

### Retrieve the history of wikibreaks by user

If you are interested in the history of [wikibreaks](https://en.wikipedia.org/wiki/Template:Wikibreak), and all its variants, of the revisions of the user pages and of the user talk pages of the Catalan Wikipedia you can type: 

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_wikibreaks --output-compression gzip extract-wikibreaks --only-pages-with-wikibreaks
```

## Retrieve the different names for a particular wikipedia template

Install the development dependencies

```sh
pip install -r requirements.dev.txt
```

Then run the following python script giving it as output the wikidata code of the template:

```sh
python utils/get_template_names.py WIKIDATA-TEMPLATE-CODE
```
