## Project Overview

This project implements a scalable data science pipeline for analyzing Airbnb
listings and generating **actionable quality-improvement recommendations** for hosts.

Using large-scale data processed in **Databricks with Apache Spark**, we engineer
textual and location-based features to predict whether a listing is likely to be
**high-rated**, and provide **interpretable suggestions** to improve listing quality.
A lightweight web interface is included to demonstrate precomputed results on a
sampled dataset.
## How to Run

### Prerequisites
- A Databricks workspace
- An active Databricks Spark cluster (any standard configuration)

### Databricks Pipeline
The full data processing, feature engineering, and scoring pipeline is
implemented in the notebook located at:

`notebooks/airbnb_quality_fixer.ipynb`

#### Steps
1. Import the notebook into a Databricks workspace.
2. Attach the notebook to any running Spark cluster.
3. Configure data access paths as documented inside the notebook.
4. Run the notebook cells sequentially from top to bottom.

> **Note on Data Access**  
> Due to data licensing and usage restrictions, the Airbnb datasets are  
> **not included** in this repository.  
> Data loading is intentionally excluded and must be configured by the user
> in their own Databricks environment.

---

## Interface (Live Demo)

The project includes a lightweight web interface for exploring the generated
recommendations.

The interface is **already deployed** and can be accessed directly at:

👉 https://airbnbproject-final.onrender.com

---

## Interface Sample Inputs

To help reviewers quickly explore the interface, the following example
inputs are guaranteed to exist in the data sample used by the demo.

### Example Listings

**Input 1 — 
- `seller_id`: 541773287  
- `listing_id`: 1001884630305047646

**Input 2 — 
- `seller_id`: 51508411  
- `listing_id`: 10033310

**Input 3 —
- `seller_id`: 13471111  
- `listing_id`: 1081595343647099000

These inputs can be entered directly into the deployed interface to
inspect different recommendation behaviors.

---

## Data Sample for Interface

A small pre-generated data sample used by the interface is stored in the
**course Azure storage container**, as required by the assignment instructions.

- **Location:** Azure Blob Storage → `submissions` container  
- **Directory:** A folder named after the project group (`Aml_Sham_Nada`)  
- **Contents:** A limited sample derived from the final Databricks output

This sample is provided **only for interface demonstration purposes and visualizations**.
All large-scale processing and model training are performed offline in
Databricks.

---

## Deployment & Repository Structure

- **HTML interface design** is located under the `templates/` directory  
  (`index.html`), which defines the user-facing layout of the demo interface.

- **Backend and deployment logic** is implemented in `app.py`, which serves the
  interface and loads a sampled output dataset to demonstrate the system behavior.

- The application is configured for deployment using the included
  `Procfile` and `requirements.txt`.

> **Important:**  
> The interface is intended as a **demonstration layer** that presents
> **precomputed recommendations** generated offline in Databricks.  
> Model training and large-scale data processing are **not executed at runtime**.

> **Data Availability Note:**  
> The GitHub repository does **not** include raw Airbnb datasets.
> All data access is handled exclusively through the course-provided
> Azure storage environment.
