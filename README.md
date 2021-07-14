# Wikidump

Framework for the features extraction from Wikipedia XML dumps.

## Installation

This project has been tested with Python 3.5.0 and Python 3.8.5.

You need to install dependencies first, as usual.
```sh
pip install -r requirements.txt
```

## Usage

First of all, download Wikipiedia dumps:

```sh
./download.sh
```

Then run the extractor:

```sh
python -m wikidump [PROGRAM_OPTIONS] FILE [FILE ...]  OUTPUT_DIR [PROGRAM_OPTIONS] FUNCTION [FUNCTION_OPTIONS]
```

You can also run the program by using the `Makefile` and `GNU/Make` (edit the file in order to run the program with the desired parameters).
For example, you can run the program on the English dumps by typing:

```sh
make run-en
```

### Example of use

### Retrieve the languages known by each user according to the last revision

If you are interested in extracting the languages known by the Catalan Wikipedia's users, you can type:

```sh
python -m wikidump --output-compression gzip dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output extract-known-languages --only-pages-with-languages --only-revisions-with-languages --only-last-revision
```

### Retrieve the wikibreak history

So as to retrieve the [wikibreaks](https://en.wikipedia.org/wiki/Template:Wikibreak) and similar templates associated to the users within their user page and user talk page, you can type:

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_wikibreaks --output-compression gzip extract-wikibreaks --only-pages-with-wikibreaks
```

The example above shows the language extraction considering the Catalan Wikipedia.

### Retrieve options and occurences of the user warnings transcluded templates

In order to retrieve [`transcluded`](https://en.wikipedia.org/wiki/Wikipedia:Transclusion) user warnings templates and their associated parameters within user talk pages, you can run the following Python command:

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_user_warnings_transcluded --output-compression gzip extract-user-warnings --only-pages-with-user-warnings
```
The example, shown above, illustrates the template extraction considering the Catalan Wikipedia.

### Retrieve regular expressions form the user warnings templates

This command aims to produce `regular expressions` to detect a [`substituted`](https://en.wikipedia.org/wiki/Wikipedia:Substitution) user warnings template (using the `subst` function) within user talk pages. 

Unfortunately, for the sake of semplicity, the `subst-chain` is not handled by this Python code.

To run the script, you run the following command:

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_user_warnings_regex --output-compression gzip extract-user-warnings-templates --esclude-template-repetition --set-interval '1 week'
```

The example above shows the regular expressions produced considering the Catalan Wikipedia.

The previous command will ignore revisions, in which the template has not changed. 
The script will group the changes by weeks, therefore, if we consider a single week, the script will return the latest revision among all the ones made within seven days.

**Please note: regular expressions have not been tested, since the work would have been tough and time consuming, therefore I can not assure the outcomes is totally correct**

### Retrieve the salient words of a user warnings template

In order to find the most salient words which best characterize the user warnings templates, you can run the following command:

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_user_warnings_tokens --output-compression gzip extract-user-warnings-templates-tokens --esclude-template-repetition --set-interval '1 week' --language catalan
```
The example above shows the most salient words extraction considering the Catalan Wikipedia.

The previous command will ignore revisions, in which the template has not changed. 
The script will group the changes by weeks, therefore, if we consider a single week, the script will return the latest revision among all the ones made within seven days.

#### How the algorithm chooses the most salient words

First of all, the punctuation and symbols are removed from each template.
Secondly, the stopwords of the chosen language are removed. Subsequently, if the appropriate flag is set, every word left is stemmed.
Finally, the value of the [`tf-idf`](https://en.wikipedia.org/wiki/Tf%E2%80%93idf) metric for each word within all the revisions is calculated. 
The corpus considered is made up of the set of template text of the revisions selected for that template.
At this point, we define `N` as the number of words which makes up the revision of the template and `X` the number of documents in the corpus. 
Let's consider `2*X` documents per template: `X` elements are randomly taken from other templates of the same language to avoid the `idf` value being too small (in the worst case 0) for the templates which change infrequently. 
The `K` words with the highest `tf-idf` value for revision are then selected, where `K` changes from revision to revision and is equal to `N/2`.

### Probabilistic way to retrieve the occurences of user warnings

To find substituted user warnings in a probabilistic way, with the possibility of false positives cases, you can run the following command:

```sh
python -m wikidump dumps/cawiki/20210201/cawiki-20210201-pages-meta-history.xml.7z output_user_warnings_probabilistic --output-compression gzip extract-user-warnings-templates-probabilistic --only-pages-with-user-warnings --language catalan output_tokens/cawiki-20210201-pages-meta-history.xml.7z.features.json.gz --only-last-revision
```

The example above will use of the words extracted from the `extract-user-warnings-templates-tokens` command by passing the output files as a parameter.
The objective is to find all the salient words of a template within the user talk page; if the aim is successfully reached, the template is marked as found and, after that, the salient words found will be printed. 

## Retrieve the name of a Wikipedia template in different languages

Firstly, you need to find the Wikidata item code of the template; for example the code for the `wikibreak` is `Q5652064`(retrieved from the corresponding [wikidata page](https://www.wikidata.org/wiki/Q5652064)). 

Secondly, you need to install the development dependencies

```sh
pip install -r requirements.dev.txt
```

Finally, run the following python command and giving it the template code 

```sh
python utils/get_template_names.py WIKIDATA-TEMPLATE-CODE
```

# Data

The documentation, regarding the the produced data and the refactored one, is shown here [data documentation](https://github.com/WikiCommunityHealth/wikipedia-languages-wikibreaks-user-warnings-analysis/blob/master/docs/data-format.pdf).

## How to merge and refactor the raw data

In order to merge all the fragments, into which the dump is divided and to make the produced file more manageable, you can use the Python scripts, present in the `utils/dataset_handler` folder, in sequence.
As for the previous case, it is possible and recommended to use a `Makefile`;
only after having edited it, can you simply type:

```sh
make run
```

## Run

In order to call the all the scripts on all the Wikipedia dump, you can run the following script

```bash
./run.sh
```

First of all, be sure you have modified all the readonly variables so as to fit your needs; feel free to change whatever you want.

The dependencies of the previously defined script are

* [wikidump-download-tools](https://github.com/CristianCantoro/wikidump-download-tools)
* [curl](https://curl.se/)
* [GNU parallel](https://www.gnu.org/software/parallel/)

## Docker

So as to call the entire program in a [`Docker`](https://www.docker.com/) cotainer, a `Dockerfile` has been provided.

First, you need to change the content of the `run.sh` file in order to fill your requirements, such as the files' locations and which operation should be carried out by the script.

Additionally, make sure you have given the correct reference if you are willing to directly install the dump within the Docker image by using `wikidump-download-tools`.

Then, you can build the Docker image by typing:

```bash
docker build -t wikidump .
```

Lastly, run the docker image:

```bash
docker run wikidump ./run.sh
```

# Authors

This library was created by [Alessio Bogon](https://github.com/youtux) and then expanded by [Cristian Consonni](https://github.com/CristianCantoro).

The here presented project is implemented on the pre-existent structure.