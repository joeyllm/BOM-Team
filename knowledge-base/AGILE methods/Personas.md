## Persona 1: The End-User / Decision Maker

**Name:** Samira, the Operational Forecaster  
**Role:** Data Analyst / Operational Meteorologist

**Background:** Samira relies on real-time data to make rapid, high-stakes decisions. She isn't building the backend infrastructure, but she completely depends on the outputs of those pipelines being reliable, accurate, and easy to interpret. She needs to know exactly how well the models are performing before she trusts them with operational calls.

**Goals:**
* Access clean, structured forecasting data without having to manually scrub or format it.
* Quickly view baseline nowcasting models to understand immediate, short-term trends.
* Review automated performance reports to see the accuracy, error margins, and confidence intervals of the forecasts.

**Pain Points:**
* Raw data feeds are often messy, missing values, or delayed, which stalls her analysis workflow.
* Lack of transparency regarding how a model was evaluated makes it hard to trust the outputs.
* Manually compiling validation metrics takes time away from actual forecasting and analysis.

**Example Agile User Story:**
> *"As an Operational Forecaster, I want to access automated performance reports for the baseline nowcasting models so that I can confidently gauge their accuracy before making operational decisions."*

---

## Persona 2: The Infrastructure Builder / Learner

**Name:** Marcus, the Junior Data Engineer  
**Role:** Third-Year Software Engineering Student / System Maintainer

**Background:** Marcus is getting hands-on experience building real-world data pipelines and infrastructure for a course project. He is responsible for setting up the ingestion workflows and ensuring the baseline models run smoothly through the evaluation and validation pipelines. He needs the system architecture to be logical, well-documented, and modular so he can apply software engineering best practices to operational forecasting.

**Goals:**
* Successfully build and trigger automated, robust workflows for data ingestion and cleaning.
* Easily swap out or update baseline models within the pipeline to test new approaches and algorithms.
* Develop validation pipelines that catch data anomalies and model drift early before outputs are produced.
* Gain practical, verifiable experience with industry-standard deployment and operational workflows.

**Pain Points:**
* Poorly structured pipelines or "spaghetti code" that make debugging ingestion failures a nightmare.
* Unclear evaluation metrics that make it hard to tell if a pipeline tweak improved the model or broke it entirely.
* Steep learning curves when the infrastructure lacks clear separation of concerns between the data cleaning, modelling, and reporting stages.

**Example Agile User Story:**
> *"As a Junior Data Engineer, I want the validation pipelines to automatically flag anomalous data during ingestion so that I can troubleshoot the cleaning workflow without the model failing silently."*