# FOLDERS
SCRIPTS_FOLDER := datasets_handler
OUTPUT_FOLDER_MERGED := ../languages_merged
INPUT_FOLDER_RAW := ../output_languages
INPUT_FOLDER_MERGED := $(OUTPUT_FOLDER_MERGED)
OUTPUT_FOLDER_REFACTORED := ../languages_simplified

# PROGRAMS AND FLAGS
MERGER := merger.py
SIMPLIFIER := simplifier.py
ADDITIONAL_PROCESSOR := 
ADDITIONAL_PROCESSOR_FLAGS := 
PYTHON := python3
SCRIPT_MERGE_FLAGS := cawiki 20210201
SCRIPT_REFACTOR_FLAGS := $(SCRIPT_MERGE_FLAGS)

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
.PHONY: help run merge simplify additional-process run-full

help:
	@$(ECHO) '$(YELLOW)Makefile help$(NONE)'

merge:
	@$(ECHO) '$(BLUE)Merging all the pieces of the dump...$(NONE)'
	@$(MKDIR) $(INPUT_FOLDER_RAW)
	@$(MKDIR) $(OUTPUT_FOLDER_MERGED)
	@$(PYTHON) $(SCRIPTS_FOLDER)/$(MERGER) $(INPUT_FOLDER_RAW) $(OUTPUT_FOLDER_MERGED) $(SCRIPT_MERGE_FLAGS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

simplify:
	@$(ECHO) '$(BLUE)Refactoring the dump (it could take a while, depending on the size of the dump)...$(NONE)'
	@$(MKDIR) $(INPUT_FOLDER_MERGED)
	@$(MKDIR) $(OUTPUT_FOLDER_REFACTORED)
	@$(PYTHON) $(SCRIPTS_FOLDER)/$(SIMPLIFIER) $(INPUT_FOLDER_MERGED) $(OUTPUT_FOLDER_REFACTORED) $(SCRIPT_REFACTOR_FLAGS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

additional-process:
	@$(ECHO) '$(BLUE)Additional data process...$(NONE)'
	@$(PYTHON) $(SCRIPTS_FOLDER)/$(ADDITIONAL_PROCESSOR) $(ADDITIONAL_PROCESSOR_FLAGS)
	@$(ECHO) '$(BLUE)Done$(NONE)'

run: merge simplify
	@$(ECHO) '$(BLUE)Merged and refactored$(NONE)'

run-full: merge simplify additional-process
	@$(ECHO) '$(BLUE)Merged, refactored and processed$(NONE)'