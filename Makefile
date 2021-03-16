# FOLDERS
VENV := venv
PROJECT_NAME := wikidump
DUMP_FOLDER := dumps
CAWIKI := cawiki
ITWIKI := itwiki
DEWIKI := dewiki
ENWIKI := enwiki
ESWIKI := eswiki
FRWIKI := frwiki
JAWIKI := jawiki
NLWIKI := nlwiki
PLWIKI := plwiki
PTWIKI := ptwiki
RUWIKI := ruwiki
SVWIKI := svwiki
ZHWIKI := zhwiki

# PROGRAMS AND FLAGS
PYFLAGS := -m
PROGRAM := wikidump
OUTPUT_FOLDER := output_wikibreaks
PROGRAM_FLAGS := --output-compression gzip
FUNCTION_TO_RUN := extract-wikibreaks
FUNCTION_SUB_COMMANDS := --only-pages-with-wikibreaks --only-revisions-with-wikibreaks
PYTHON := python3
PIP := pip
DUMP_EXT := .7z

# COLORS
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
NONE := \033[0m

# COMMANDS
ECHO := echo -e
MKDIR := mkdir -p
RM := rm -rf

# RULES
.PHONY: help env deleteenv install install-dev run-ca run-it run-all run-de run-es run-fr run-ja run-nl run-pl run-pt run-ru run-sv run-zh 

help:
	@$(ECHO) '$(YELLOW)Makefile help$(NONE)'

env:
	@$(ECHO) '$(GREEN)Creating the virtual environment..$(NONE)'
	@$(MKDIR) $(VENV)
	@$(eval PYTHON_VERSION=$(shell $(PYTHON) --version | tr -d '[:space:]' | tr '[:upper:]' '[:lower:]' | cut -f1,2 -d'.'))
	@$(PYTHON_VERSION) -m venv $(VENV)/$(PROJECT_NAME)
	@$(ECHO) '$(GREEN)Done$(NONE)'

install:
	@$(ECHO) '$(GREEN)Installing requirements..$(NONE)'
	@pip install -r requirements.txt
	@$(ECHO) '$(GREEN)Done$(NONE)'

install-dev:
	@$(ECHO) '$(GREEN)Installing requirements..$(NONE)'
	@$(PIP) install -r requirements.dev.txt
	@$(ECHO) '$(GREEN)Done$(NONE)'

run-ca:
	@$(ECHO) '$(BLUE)Running cawiki datasets..$(NONE)'
	@$(eval FILES=$(wildcard $(DUMP_FOLDER)/$(CAWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-it:
	@$(ECHO) '$(BLUE)Running itwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(ITWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-de:
	@$(ECHO) '$(BLUE)Running dewiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(DEWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-es:
	@$(ECHO) '$(BLUE)Running eswiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(ESWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-en:
	@$(ECHO) '$(BLUE)Running enwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(ENWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-fr:
	@$(ECHO) '$(BLUE)Running frwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(FRWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-ja:
	@$(ECHO) '$(BLUE)Running jawiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(JAWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-nl:
	@$(ECHO) '$(BLUE)Running nlwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(NLWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-pl:
	@$(ECHO) '$(BLUE)Running plwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(PLWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-pt:
	@$(ECHO) '$(BLUE)Running ptwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(PTWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-ru:
	@$(ECHO) '$(BLUE)Running ruwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(RUWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-sv:
	@$(ECHO) '$(BLUE)Running svwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(SVWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-zh:
	@$(ECHO) '$(BLUE)Running zhwiki datasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/$(ZHWIKI)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run-all:
	@$(ECHO) '$(BLUE)Running all the wikidatasets..$(NONE)'
	@$(eval FILES=$(shell find $(DUMP_FOLDER)/**/*$(DUMP_EXT)))
	@$(PYTHON) $(PYFLAGS) $(PROGRAM)  $(PROGRAM_FLAGS) $(FILES) $(OUTPUT_FOLDER) $(FUNCTION_TO_RUN) $(FUNCTION_SUB_COMMANDS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

deleteenv:
	@$(ECHO) '$(RED)Deleting the virtual environment..$(NONE)'
	@$(RM) $(VENV)
	@$(ECHO) '$(RED)Done$(NONE)'

