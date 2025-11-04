# Prompt Design Rationale

This file explains how LLM prompts *would* be used in a hybrid version of the system.

## Why prompts?

If the project is extended to use a Large Language Model (e.g., GPT-4 or Mistral),
these prompts guide the model to focus on relevant legal clauses and extract structured answers.

## Current version (TF-IDF only)

In the current submission, no prompt-based inference or LLM API call is executed.
The prompt files are included **only for completeness**, to show how future versions
can integrate retrieval-augmented generation (RAG) over PDF contract text.
