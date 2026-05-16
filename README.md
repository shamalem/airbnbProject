# Airbnb Quality Fixer

A scalable data-driven system that analyzes Airbnb listings and generates actionable recommendations to help hosts improve listing quality, visibility, and booking potential.

---

## Project Overview

Airbnb Quality Fixer is a large-scale data science and machine learning project designed to help Airbnb hosts better understand and improve how their listings are presented.

Built using Apache Spark and Databricks, the system analyzes listing descriptions, quality indicators, and location-based signals to identify patterns associated with highly rated listings. Based on this analysis, the system generates interpretable recommendations that can help improve listing presentation and overall quality.

The project also includes a lightweight Flask-based interface for exploring precomputed recommendations and listing analysis results.

---

## Key Features

- Large-scale Airbnb listing analysis using Spark
- Text quality and description scoring
- Location and landmark-based feature engineering
- High-rated listing prediction
- Actionable recommendation generation
- Interactive Flask-based interface
- Responsive dark-themed dashboard
- Offline precomputed recommendation pipeline

---

## Technologies

- Python
- Apache Spark
- Databricks
- Flask
- Machine Learning
- Azure Blob Storage
- Pandas
- Scikit-learn

---

## Skills Demonstrated

- Distributed data processing
- Feature engineering
- Machine learning workflows
- Recommendation systems
- Backend development
- Cloud-based data pipelines
- Data visualization
- System design
- Scalable analytics

---

## System Architecture

The system consists of three main components:

1. **Data Processing Pipeline**
   - Large-scale preprocessing and feature engineering using Spark in Databricks

2. **Recommendation & Scoring Engine**
   - Generates listing quality scores and actionable recommendations

3. **Flask Interface**
   - Displays precomputed analysis results and recommendations through a lightweight web interface

---

## Results

The system successfully generated interpretable recommendation outputs and listing quality scores using large-scale Airbnb listing data processed in Databricks.

Key outcomes included:
- Identification of features associated with highly rated listings
- Automated quality scoring for listing descriptions
- Landmark and location-aware recommendation generation
- Host-facing actionable feedback for improving listing presentation

The project also included visual analysis and evaluation of engineered features and model behavior.

---

## Project Structure

```text
airbnb-quality-fixer/
│
├── notebooks/
│   └── airbnb_quality_fixer.ipynb
│
├── templates/
│   └── index.html
│
├── interface-preview/
│   └── homepage.jpeg
│
├── app.py
├── requirements.txt
├── Procfile
└── README.md
```

---

## Databricks Pipeline

The full data processing, feature engineering, and scoring pipeline is implemented in:

```text
notebooks/airbnb_quality_fixer.ipynb
```

### Running the Pipeline

#### Prerequisites

- Databricks workspace
- Active Spark cluster

#### Steps

1. Import the notebook into Databricks
2. Attach the notebook to a running Spark cluster
3. Configure data access paths
4. Run the notebook sequentially

---

## Interface Preview

The project originally included a Flask-based interface deployed on Render for exploring generated recommendations and listing analysis results.

The interface depended on course-provided cloud resources and Azure Blob Storage used during the academic project lifecycle. Since these resources are no longer active, the live deployment is currently unavailable.

To document the implemented system and user flow, screenshots of the interface are included below.

---

## Interface Screenshots

### Host Report Dashboard

![Host Report Dashboard](interface-preview/homepage.jpeg)

The interface allows hosts to:
- Analyze listing quality
- View description quality scores
- Explore actionable recommendations
- Identify missing amenities and phrases
- Receive interpretable feedback based on highly rated listings

---

## Sample Inputs

The following example listing IDs were included in the demonstration dataset used by the interface.

### Example 1

- seller_id: `541773287`
- listing_id: `1001884630305047646`

### Example 2

- seller_id: `51508411`
- listing_id: `10033310`

### Example 3

- seller_id: `13471111`
- listing_id: `1081595343647099000`

---

## Data Availability

The original Airbnb datasets are not included in this repository due to licensing and course-related storage restrictions.

All large-scale processing and model training were executed offline in Databricks using course-provided Azure storage resources.

The repository focuses on:
- pipeline implementation
- feature engineering
- recommendation logic
- interface implementation
- system architecture

---

## Important Notes

- The interface serves as a demonstration layer for precomputed recommendations
- Model training and Spark processing are not executed at runtime
- The deployment infrastructure originally relied on temporary academic cloud resources

---

## Team

Developed collaboratively as part of a university data science project.

### Authors

- Sham Alem
