
---
## How to Run

### Prerequisites
- A Databricks workspace
- An active Databricks Spark cluster (any standard configuration)

### Databricks Pipeline
The full data processing and scoring pipeline is implemented in the notebook
located at:

`notebooks/airbnb_quality_fixer.dbc`

#### Steps
1. Import the notebook (`notebooks/airbnb_quality_fixer.ipynb`) into a Databricks workspace.
2. Attach the notebook to any running Spark cluster.
3. Configure data access paths as documented inside the notebook.
4. Run the notebook cells sequentially from top to bottom.

> **Note on Data Access**  
> Due to data licensing and usage restrictions, the Airbnb datasets
> are **not included** in this repository.  
> Data loading is intentionally excluded and must be configured by the user
> in their own Databricks environment.

---

## Interface (Live Demo)

The project includes a lightweight web interface for exploring the generated
recommendations.

The interface is **already deployed** and can be accessed directly at:

👉 https://airbnbproject-final.onrender.com

## Interface Sample Inputs

To help reviewers quickly explore the interface, the following example
inputs are guaranteed to exist in the data sample used by the demo.

### Example Listings

**Input 1 — High-rated listing (Germany)**
- `seller_id`: 541773287
- `listing_id`: 1001884630305047646

**Input 2 — High-rated listing with almost no suggestions**
- `seller_id`: 51508411
- `listing_id`: 10033310

**Input 3 — Different seller with a large listing ID**
- `seller_id`: 13471111
- `listing_id`: 1081595343647099000

These inputs can be entered directly into the deployed interface to
inspect different recommendation behaviors.

---

## Data Sample for Interface

A small data sample used by the interface is stored in the **course Azure
storage container**, as required by the assignment instructions.

- Location: Azure Blob Storage → `submissions` container
- Directory: A folder named after the project group "Aml_Sham_Nada".
- Contents: A limited, pre-generated sample derived from the project output

This sample is provided **only for interface demonstration purposes**.
All raw scraped or external datasets used in the project appear in this
directory, with informative filenames.
##  Deployment
- **HTML interface design** can be found under the `templates/` directory  
  (`index.html`), which defines the user-facing layout of the demo interface.

- **Backend and deployment logic** is implemented in `app.py`, which serves the
  interface and loads a sampled output dataset to demonstrate the system behavior.

- The application is configured for deployment using the included `Procfile`
  and `requirements.txt`.

> Note: The interface is intended as a **demonstration layer** that presents
> precomputed recommendations generated offline in Databricks.  
> Model training and large-scale data processing are not executed at runtime.

> **Note:**  
> The GitHub repository does not include any Airbnb .
> Data access is handled exclusively through the course Azure environment.
