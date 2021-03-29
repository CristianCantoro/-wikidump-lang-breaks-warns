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

### Retrieve options and occurences of the user warnings transcluded templates

If you are interested in extracting the options and occurrences of the [`transcluded`](https://en.wikipedia.org/wiki/Wikipedia:Transclusion) user warnings templates (not replaced with the `subst` function) counted by user talk page, you can run the following python command:

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_user_warnings_transcluded --output-compression gzip extract-user-warnings --only-pages-with-user-warnings
```

### Retrieve regular expressions form the user warnings templates

If you are interested in obtaining `regular expressions` to recognize a certain user warnings template [`substituted`](https://en.wikipedia.org/wiki/Wikipedia:Substitution) in a user talk page without `subst-chain handling` you can use the following command:

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_user_warnings_regex --output-compression gzip extract-user-warnings-templates --esclude-template-repetition --set-interval '1 week'
```

The previous command will ignore revisions where the template has not changed and will group the changes for 1 week, i.e. it will return the latest revision for multiple changes within a week.

**Please note: le espressioni regolari non sono state testate su tutto il dump ma solo per alcuni casi di test dai quali risulta funzionare**

### Retrieve the salient words of a user warnings template

If you are interested in finding the words that best characterize the user warnings templates for a certain language, you can run the following command: 

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_user_warnings_tokens --output-compression gzip extract-user-warnings-templates-tokens --esclude-template-repetition --set-interval '1 week' --language catalan
```

The previous command will ignore revisions where the template has not changed and will group the changes for 1 week, i.e. it will return the latest revision for multiple changes within a week.

#### How the algorithm chooses the words

First of all, the punctuation and symbols are removed from each template, then the stopwords of the chosen language are removed. Subsequently every word left is stemmed.
Finally, the value of the [`tf-idf`](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) metric for word and document within the corpus is calculated. 
The corpus considered is made up of the set of template text of the revisions selected for that given template.
At this point we define `N` as the number of words that make up the revision of the template handled and `X` the number of documents in the corpus. 
Let's consider `2*X` documents per template where the other X elements are randomly taken from other templates of the same language to avoid that the `idf` value is not too small or in the worst case 0 for templates that change infrequently. 
The `K` words with the highest `tf-idf` value for revision are then selected, where `K` varies from revision to revision and is equal to `N/2`

## Retrieve the name of a Wikipedia template in different languages

You need to find the Wikidata item code of the template of interest, for example for the `wikibreak` tamplate the code is `Q5652064`, from the corresponding [wikidata page](https://www.wikidata.org/wiki/Q5652064). 

First, you need to install the development dependencies

```sh
pip install -r requirements.dev.txt
```

Then run the following python script giving it as output the wikidata code of the template:

```sh
python utils/get_template_names.py WIKIDATA-TEMPLATE-CODE
```
