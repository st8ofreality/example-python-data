# Python Data Processing & Training Analytics Toolkit

A modular Python framework designed for extracting, processing, aggregating, and visualizing learner progress, coursework completion, and certification metrics from LMS (Learning Management System) reports and API endpoints.

---

## Features

- **Interactive Orchestrator CLI (`main_v2.py` / `main_combined_script.py`)**: Unified console menu allowing users to run single or multiple data pipelines sequentially.
- **Automated LMS API Report Exporter (`api_report_config.py`)**: Handles asynchronous report generation, polling export completion status, and downloading CSV reports via REST API endpoints.
- **API Observation Checklist Data Pipeline (`api_obschecklist_config.py`)**: Automatically fetches observation checklist items across multiple checklist configurations with retry logic.
- **Program Health Analytics (`program_health_script_v6.py`)**: Computes role-based program health pivot tables categorizing learners by experience tier (`<= 16 weeks` vs. `> 16 weeks`) and status metrics.
- **Training Summary & Visualization (`createtraining_summary_overviewcount.py`)**: Generates summary overview counts and exports visual bar charts (`seaborn`/`matplotlib`).
- **Product Spec & Funnel Analysis (`pivotdata_v2_module.py`)**: Analyzes training funnels, identifies qualified candidates for certification exams/mock technical calls, and pinpoints bottleneck phases.
- **Multi-Dataset Merging (`mergetrainingdata_module.py` & `merge_trainingdataog.py`)**: Merges user course enrolment datasets with granular training material scores, readiness checks, and completion dates.

---

## Prerequisites

- **Python**: 3.8 or higher
- **Required Libraries**:
  ```bash
  pip install pandas openpyxl chardet requests matplotlib seaborn
  ```

---

## Configuration & Environment Variables

For scripts interacting with the LMS API (`api_report_config.py` and `api_obschecklist_config.py`), set the following OS environment variables before running:

| Environment Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `TRAINING_API_TOKEN` | **Required**. Bearer token used for LMS API authentication. | `export TRAINING_API_TOKEN="your_api_token_here"` |
| `TRAINING_API_URL` | Base REST API URL of your LMS endpoint. | `export TRAINING_API_URL="https://your-lms-domain.com/api"` |

---

## Directory Structure

The framework automatically manages input and output directories under `~/python/`:

```
~/python/
├── inputs/       # Place your source .csv, .xlsx, or .json configuration files here
├── outputs/      # Transformed data reports, pivot CSVs, and PNG charts are saved here
├── reports/      # Downloaded LMS API export files
└── checklists/   # Processed observation checklist datasets
```

---

## Usage

### Interactive CLI Menu

Run the primary runner script:

```bash
python main_v2.py
```

You will be presented with an interactive menu:

```
Select the scripts to run (comma-separated numbers for multiple selections):
1. Program Health Script V6
2. Summary Program Overview
3. LMS API Report (.json required)
4. LMS API Observation Checklist (.json required)
5. Product Spec V2
6. Merge Spec and TM reports
```

Enter a single choice (e.g. `1`) or a comma-separated list (e.g. `3,4,5`) to run pipelines back-to-back.

### File Format Requirements

- **Program Health & Summaries**: Supports `.csv` and `.xlsx` inputs. Encoding is automatically detected using `chardet`.
- **API Reports & Checklists**: Requires `.json` configuration files specifying report IDs and target output file names.

---

## Modules Overview

- **`main_v2.py`**: Principal entry point with single and dual-file selection logic for merging spec and training material reports.
- **`api_report_config.py`**: Triggers asynchronous report export requests (`/export/csv`), polls status every 15 seconds until `SUCCEEDED`, and saves the file.
- **`api_obschecklist_config.py`**: Reads JSON checklist configurations and batch-fetches data from the checklist API with exponential retry logic.
- **`pivotdata_v2_module.py`**: Generates `complete_coursework.csv`, `qualified_tickets.csv`, `certified.csv`, `stages_pivot.csv`, `stuck_phases_pivot.csv`, and `overlapping_names.csv`.
- **`createtraining_summary_overviewcount.py`**: Calculates total program health counts per role/status and saves a visualization plot.
- **`mergetrainingdata_module.py`**: Maps certification exams and readiness checks to user course records by matching email addresses/usernames.

---

## Security & Privacy Notice

This repository contains non-proprietary, open script templates. All tokens, secrets, company-specific API endpoints, and internal product strings have been sanitized and configured to load securely via environment variables or configuration files.
