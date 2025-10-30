The program consists of two files(Final.py and project_data.csv).

The code defines a Project Health Analysis System aimed at performing basic diagnostics on project work logs stored within a database. Its core functionality is to process multi-dimensional work entries to assess:
1)Project Efficiency (Time Metrics).
2)Module Workload Distribution (Resource Allocation).
3)Potential Risks based on textual sentiment analysis.
4)Key Functional Analysis Modules
   A. Time Efficiency Analysis
Total Duration: Calculates the sum of all logged work hours.
Project Span: Determines the earliest (min) and latest (max) dates in the logs.
Average Daily Workload: Calculates the total work duration divided by the number of unique work days, providing a measure of productivity/utilization.
   B. Module Workload Analysi
Workload Breakdown: Calculates the absolute hours spent on each project module (e.g., 'Backend API', 'Frontend UI').
Proportional Effort: Determines the percentage of total project time allocated to each module.
Visualization: The report uses an ASCII bar chart (composed of # symbols) to visually represent the percentage breakdown.
  C. Risk and Sentiment Analysis
Risk Keywords: Uses a pre-defined list (NEGATIVE_WORDS) to scan log summaries.
Risk Index: Calculates the percentage of total records that contain at least one negative keyword, providing a quantitative Potential Risk Index.
Qualitative Assessment: Assigns a risk level (Low, Medium, or High) based on the calculated percentage threshold.
Top Risk Factors: Identifies the top three most frequently cited negative keywords to highlight common pain points.
