#!/bin/bash

is_complete_dump() {
    # it checks if the value is a number and if it ends with 01, since
    # the full dump is usually retrieved on the first of each month 
    re='[0-9]+01$'
    if [[ $1 =~ $re ]] ; then
        echo 1
    fi
    echo 0
}

create_folder() {
    mkdir -p $1
}

empty_folder() {
    rm -rf $1
}

get_latest_full_dump() {
    # Saving the HTML page in a temporary file
    curl --silent "${1}" > "${0%.*}.tmp~"
    # href contents, removing the /
    local dates=`sed -n 's/.*href="\([^"]*\).*/\1/p' "${0%.*}.tmp~" | sed 's/\///'`
    # maximum value found
    local max=0
    # loop over the dates
    for v in ${dates[@]}; do
        # check if the value is a number
        local res=$(is_complete_dump $v)
        if [[ $res != 0 ]] ; then
            if [[ $v > $max ]];  then 
                max=$v; 
            fi;
        fi;
    done
    # delete the temporary file
    [ -e "${0%.*}.tmp~" ] && rm "${0%.*}.tmp~"
    # date found
    echo $max
}

# Path of the wikidump-download-tools
readonly WIKIDUMP_DOWLOAD_TOOLS="$(realpath "../wikidump-download-tools" )"
# linked arrays
declare -a wikis=( "cawiki" "enwiki" "itwiki" "eswiki" )
declare -a languages_codes=( "ca" "en" "it" "es" )
declare -a languages=( "catalan" "english" "italian" "spanish" )
declare -a wiki_dates=()
declare -a wiki_url=()

# downloaddump flag
download_dump=0
# delete folder flag
delete_folders=0

if [ ${download_dump} = 1 ]; then
    for wiki in ${wikis[@]} ; do

        echo "Looking for the most recent ${wiki} complete dump"

        date=$(get_latest_full_dump https://dumps.wikimedia.org/eswiki/)

        wiki_dates+=( ${date} )
        
        # error check
        if [[ $date == 0 ]]; then
            echo "There has been an error looking for the most recent dump"
            exit 1
        fi
        
        # add the path to download the elements
        wiki_url+=( "https://dumps.wikimedia.org/${wiki}/${date}" )
    done

    # Download the elements
    parallel -j+0 --progress "./${WIKIDUMP_DOWLOAD_TOOLS}/scripts/wikidump-download.sh" {} ::: "${wiki_url[@]}" 

    # check the download output
    if [[ $? != 0 ]]; then
        echo "Download failed"
        exit 1
    fi

    # Path of the wikidump-download-tools downloaded data
    readonly WIKIDUMP_DATA="$( realpath "../wikidump-download-tools/data" )"

    # Symbolic link creation

    echo "Creating the symbolic link..."

    ln -s "${WIKIDUMP_DATA}" "dumps/"

    # check the download output
    if [[ $? != 0 ]]; then
        echo "Symbolic link creation failed"
        exit 1
    fi
fi

# CREATE FOLDERS
create_folder "output_languages"
create_folder "output_languages_merged"
create_folder "output_languages_refactored"

create_folder "output_wikibreaks"
create_folder "output_wikibreaks_merged"
create_folder "output_wikibreaks_refactored"

create_folder "output_transcluded_warnings"
create_folder "output_transcluded_user_warnings_merged"
create_folder "output_transcluded_user_warning_refactored"

create_folder "output_salient_words"

create_folder "output_substituted_warnings"
create_folder "output_substituted_user_warnings_merged"
create_folder "output_substituted_user_warning_refactored"

create_folder "output_total_user_warning_merged"
create_folder "output_user_warning_refactored"

################################
####    languages           ####
################################

echo 'Extracting languages'

printf "%s\n" ${languages_codes[@]} | xargs -i make run-'{}' OUTPUT_FOLDER="output_languages" FUNCTION_SUB_COMMANDS="--only-pages-with-languages --only-revisions-with-languages --only-last-revision" FUNCTION_TO_RUN='"extract-known-languages"'

if [[ $? != 0 ]]; then
    echo "Failed to retrieve the languages"
    exit 1
fi

echo 'Refactoring languages'

cd utils/dataset_handler; parallel -j+0 --link --progress make run OUTPUT_FOLDER_MERGED="../../output_languages_merged" INPUT_FOLDER_RAW="../../output_languages" MERGER="languages/language_merger.py" SIMPLIFIER="languages/language_simplifier.py"  SCRIPT_REFACTOR_FLAGS='"{1} {2}"' OUTPUT_FOLDER_REFACTORED="../../output_languages_refactored" ::: "${wikis[@]}" ::: "${wiki_dates[@]}"

if [[ $? != 0 ]]; then
    echo "Failed to refactor the languages"
    exit 1
fi

cd ../..

################################
####    wikibreaks          ####
################################

echo 'Extracting wikibreak'

printf "%s\n" ${languages_codes[@]} | xargs -i make run-'{}' OUTPUT_FOLDER="output_wikibreaks" FUNCTION_TO_RUN="extract-wikibreaks" FUNCTION_SUB_COMMANDS='"--only-pages-with-wikibreaks"'

if [[ $? != 0 ]]; then
    echo "Failed to retrieve the wikibreaks"
    exit 1
fi

echo 'Refactoring wikibreak'

cd utils/dataset_handler; parallel -j+0 --link --progress make run OUTPUT_FOLDER_MERGED="../../output_wikibreaks_merged" INPUT_FOLDER_RAW="../../output_wikibreaks" MERGER="wikibreaks/wikibreaks_merger.py" SIMPLIFIER="wikibreaks/wikibreaks_simpilfier.py"  SCRIPT_REFACTOR_FLAGS='"{1} {2}"' OUTPUT_FOLDER_REFACTORED="../../output_wikibreaks_refactored" ::: "${wikis[@]}" ::: "${wiki_dates[@]}" 

if [[ $? != 0 ]]; then
    echo "Failed to refactor the wikibreaks"
    exit 1
fi

cd ../..

################################
####    user warnings       ####
################################

echo 'Extracting user warnings'

printf "%s\n" ${languages_codes[@]} | xargs -i make run-'{}' OUTPUT_FOLDER="output_transcluded_warnings" FUNCTION_TO_RUN="extract-user-warnings" FUNCTION_SUB_COMMANDS='"--only-pages-with-user-warnings"'

if [[ $? != 0 ]]; then
    echo "Failed to retrieve the transcluded user warnings"
    exit 1
fi

echo 'Refactoring user warnings'

# user warning transcluded refactoring
cd utils/dataset_handler; parallel -j+0 --link --progress make run OUTPUT_FOLDER_MERGED="../../output_transcluded_user_warnings_merged" INPUT_FOLDER_RAW="../../output_transcluded_warnings" MERGER="user_warnings/user_warnings_transcluded_merger.py" SIMPLIFIER="user_warnings/user_warnings_transcluded_simplifier.py"  SCRIPT_MERGE_FLAGS='"{1} {2}"' OUTPUT_FOLDER_REFACTORED="../../output_transcluded_user_warning_refactored" ::: "${wikis[@]}" ::: "${wiki_dates[@]}" 

cd ../..

if [[ $? != 0 ]]; then
    echo "Failed to refactor the transcluded user warnings"
    exit 1
fi

echo 'Extracting salient words'

# set up ntlk
python3 utils/set_up_nltk.py

# catalan stopwords
git clone https://github.com/Xangis/extra-stopwords.git
cd extra-stopwords; ./copy.sh
cd ..

# salient words seach
parallel -j+0 --link --progress make run-'{1}' OUTPUT_FOLDER="output_salient_words" FUNCTION_TO_RUN="extract-user-warnings-templates-tokens" FUNCTION_SUB_COMMANDS='"--esclude-template-repetition --language {2} --set-interval 1week"' ::: "${languages_codes[@]}" ::: "${languages[@]}"

if [[ $? != 0 ]]; then
    echo "Failed to retrieve the templates' most salient words"
    exit 1
fi

cd ../..

tokens=()

for el in "${languages_codes[@]}"; do 
    tokens+=("$(ls -d -1 output_salient_words/*.* | grep ${el} | grep features.json | xargs echo | sed 's/ / /g')"); 
done

echo 'Extracting substituted user warnings'

# user warning substituted
parallel -j+0 --link --progress make run-{1} OUTPUT_FOLDER="output_substituted_warnings" FUNCTION_TO_RUN="extract-user-warnings-templates-probabilistic" FUNCTION_SUB_COMMANDS='"--only-pages-with-user-warnings --language {2} {3} --only-last-revision"' ::: "${languages_codes[@]}" ::: "${languages[@]}" ::: "${tokens[@]}"

if [[ $? != 0 ]]; then
    echo "Failed to retrieve the substituted user warnings"
    exit 1
fi

echo 'Refactoring substituted user warnings'

# substituted user warnings refactoring
cd utils/dataset_handler; parallel -j+0 --link --progress make run OUTPUT_FOLDER_MERGED="../output_substituted_user_warnings_merged" INPUT_FOLDER_RAW="../output_substituted_warnings" MERGER="user_warnings/user_warnings_substituted_merger.py" SIMPLIFIER="user_warnings/user_warning_substituted_simplifier.py" SCRIPT_MERGE_FLAGS='"{1} {2}"' OUTPUT_FOLDER_REFACTORED="../output_substituted_user_warning_refactored" ::: "${wikis[@]}" ::: "${wiki_dates[@]}" ; 

if [[ $? != 0 ]]; then
    echo "Failed to refactor the substituted user warnings"
    exit 1
fi

cd ../..

# all user warnings refactoring
cd utils/dataset_handler; parallel -j+0 --link --progress python3 dataset_handler/user_warnings/user_warning_merger.py "../output_transcluded_user_warning_refactored" "../output_substituted_user_warning_refactored" "../output_total_user_warning_merged" "{1}" "{2}" "{3}" ::: "${wikis[@]}" ::: "${wiki_dates[@]}" ::: "${languages_codes[@]}"

if [[ $? != 0 ]]; then
    echo "Failed to merge all the user warnings"
    exit 1
fi

cd ../..

echo 'Clear unwanted folders'

if [ ${delete_folders} = 1 ]; then
    # delete the dumps
    rm -rf dumps
    rm -rf ${WIKIDUMP_DATA}

    # Empty folders
    empty_folder "output_languages"
    empty_folder "output_languages_merged"

    empty_folder "output_wikibreaks"
    empty_folder "output_wikibreaks_merged"

    empty_folder "output_transcluded_warnings"
    empty_folder "output_transcluded_user_warnings_merged"

    empty_folder "output_substituted_warnings"
    empty_folder "output_substituted_user_warnings_merged"
    empty_folder "output_total_user_warning_merged" 
fi