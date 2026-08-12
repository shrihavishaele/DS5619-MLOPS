# NOTES.md — Week 2: Config-Driven Data Pipelines

**Student ID used with `generate_for_student.py`:**
<!-- paste the --student-id value you used -->
142301003


## What was hardcoded, and what would switching it have required?

<!-- What specifically was hardcoded in the original script, and what would
     have had to happen to change the threshold or switch formats before
     your refactor? -->
The first script hardcoded the input path, the threshold, and the output path. To change the threshold or switch from CSV to JSON, we had to edit the Python code itself, save it, and rerun the script after the refactor, the values come from YAML config files
