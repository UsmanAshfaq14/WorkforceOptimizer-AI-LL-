# WorkforceOptimizer-AI Case Study

## Overview

**WorkforceOptimizer-AI** is an intelligent system developed to optimize workforce distribution for remote customer support teams. Its main goal is to balance workloads and make sure that resources are used effectively. The system automates the process of validating team data (provided in CSV or JSON formats), performing detailed calculations, and generating clear, step-by-step recommendations—all in plain language that anyone can understand.

In simple terms, WorkforceOptimizer-AI takes data about support teams (like the number of agents, the number of customer queries, and the time it takes to handle them), checks the data for errors, performs a series of calculations (such as determining each agent's workload and overall team efficiency), and then suggests whether the current staffing is optimal or if adjustments are needed.

## Features

- **Data Validation:**  
  The system ensures that the data provided meets strict criteria:
  - **Format Check:** Only accepts data in CSV or JSON formats (within markdown code blocks).
  - **Language Check:** Only English is accepted.
  - **Required Fields:** Each record must include fields such as `team_id`, `current_staff`, `queries_per_day`, `average_query_time`, `shift_hours`, `available_capacity`, and `remote_infrastructure_efficiency`.
  - **Data Type & Range:** Numeric fields are checked to ensure they are valid and within specified ranges.

- **Calculation Steps and Formulas:**  
  For each team, the system performs these key calculations:
  - **Workload per Agent:**  
    \[
    \text{Workload per Agent} = \frac{\text{queries\_per\_day} \times \text{average\_query\_time}}{\text{current\_staff}}
    \]
  - **Agent Capacity:**  
    \[
    \text{Agent Capacity} = \text{shift\_hours} \times 60 \times \frac{\text{available\_capacity}}{100}
    \]
  - **Utilization Rate:**  
    \[
    \text{Utilization Rate} = \frac{\text{Workload per Agent}}{\text{Agent Capacity}} \times 100
    \]
  - **Composite Scheduling Score:** A weighted score calculated using capacity surplus, remote infrastructure efficiency, and the inverse of the utilization rate.
  - **Staffing Efficiency Ratio:**  
    \[
    \text{Required Staff} = \frac{\text{queries\_per\_day} \times \text{average\_query\_time}}{\text{Agent Capacity}},\quad \text{Staffing Efficiency Ratio} = \frac{\text{current\_staff}}{\text{Required Staff}}
    \]
    
  These calculations help determine whether the current staffing levels are optimal or if adjustments (such as reducing or reallocating staff) are needed.

- **Final Recommendations:**  
  The system compares the calculated metrics against defined thresholds. For example, if:
  - The **Composite Score** is 60 or above,
  - The **Staffing Efficiency Ratio** is between 0.9 and 1.1, and
  - The **Utilization Rate** is 90% or below,
  
  then the system recommends: "Maintain current distribution." Otherwise, it suggests making adjustments.

- **Feedback and Iterative Improvement:**  
  After each analysis, the system asks the user for feedback (e.g., a rating on a scale of 1-5) and invites suggestions for improvement.

## System Prompt

The system prompt directs WorkforceOptimizer-AI’s behavior. It specifies:
- How to handle and validate input data,
- The exact formulas and calculation steps to use,
- The structure of the output report (including detailed calculations and recommendations),
- The protocol for user feedback.

A simplified version of the system prompt looks like this:


**[system]**
You are WorkforceOptimizer-AI. Validate all input data for language, format, and required fields. Use explicit IF/THEN/ELSE logic for calculations:
1. Validate data structure and required fields.
2. For each team, calculate:
   - Workload per Agent: (queries_per_day × average_query_time) / current_staff
   - Agent Capacity: shift_hours × 60 × (available_capacity / 100)
   - Utilization Rate: (Workload per Agent / Agent Capacity) × 100
   - Composite Scheduling Score using weighted values.
   - Required Staff and Staffing Efficiency Ratio.
3. If Composite Score ≥ 60, Staffing Efficiency Ratio is between 0.9 and 1.1, and Utilization Rate ≤ 90%, recommend "Maintain current distribution"; otherwise, recommend adjustments.
Output the results in a clear, step-by-step markdown report.


## Variations and Test Flows

### Flow 1: Greeting and Data Format Error
- **User Action:**  
  The user greets with "Hello" and provides data in an incorrect format (using semicolons and vertical bars instead of CSV or JSON).
- **Assistant Response:**  
  The system responds with an error:  
  *"ERROR: Invalid data format. Please provide data in CSV or JSON format."*
  
### Flow 2: Requesting the Template
- **User Action:**  
  The user then asks for a template.
- **Assistant Response:**  
  The system provides the CSV and JSON templates, clearly outlining the required fields and format.
  
### Flow 3: Correct Data Submission
- **User Action:**  
  The user submits correct CSV data:
  ```csv
  team_id,current_staff,queries_per_day,average_query_time,shift_hours,available_capacity,remote_infrastructure_efficiency
  TeamOmega,10,150,3.0,8,70,80
  TeamSigma,12,170,3.5,7,75,85
  TeamTheta,8,140,2.8,6,65,90
  TeamLambda,11,160,3.2,7.5,80,88
  TeamZeta,9,130,3.6,8,68,82
  ```
- **Assistant Response:**  
  The system validates the data and returns a successful validation report, confirming that all required fields are present, data types are correct, and values fall within expected ranges.

### Flow 4: Analysis and Final Report
- **User Action:**  
  The user agrees to proceed with the analysis.
- **Assistant Response:**  
  The system processes the validated data and produces a final report. This report includes detailed, step-by-step calculations for each team (e.g., TeamOmega, TeamSigma, etc.) and provides recommendations based on the computed metrics. For instance, even though the Composite Scores are high, the Staffing Efficiency Ratios indicate overstaffing, leading the system to recommend adjustments.

*Example Extract for TeamOmega:*
- **Workload per Agent:** 45.00 minutes  
- **Agent Capacity:** 336.00 minutes  
- **Utilization Rate:** 13.39%  
- **Composite Scheduling Score:** 84.63  
- **Staffing Efficiency Ratio:** 7.46  
- **Final Recommendation:** "Needs Adjustment" (i.e., consider reassigning workforce or adjusting shift timings).

## Conclusion

WorkforceOptimizer-AI is a powerful, user-friendly tool that helps organizations optimize the staffing of remote customer support teams. By strictly validating input data and performing detailed, step-by-step calculations, the system ensures that decision-makers receive clear insights into workforce distribution. The case study presented here demonstrates how the system handles various input scenarios—from format errors to data corrections—and provides actionable recommendations based on real data.

This project exemplifies how automation and clear, logical processes can simplify complex decision-making tasks, ultimately leading to improved operational efficiency and better resource management.

