import json
import csv
import io
import re
import math

class WorkforceOptimizer:
    def __init__(self):
        self.valid_fields = ["team_id", "current_staff", "queries_per_day", 
                           "average_query_time", "shift_hours", 
                           "available_capacity", "remote_infrastructure_efficiency"]
        self.numeric_fields = ["current_staff", "queries_per_day", 
                             "average_query_time", "shift_hours", 
                             "available_capacity", "remote_infrastructure_efficiency"]
        self.positive_fields = ["current_staff", "queries_per_day", 
                              "average_query_time", "shift_hours"]
        self.percentage_fields = ["available_capacity", "remote_infrastructure_efficiency"]
    
    def detect_format(self, data_str):
        """Detect if the data is in CSV or JSON format"""
        data_str = data_str.strip()
        if data_str.startswith('{') and data_str.endswith('}'):
            return 'json'
        elif ',' in data_str and '\n' in data_str:
            return 'csv'
        else:
            return None
    
    def parse_data(self, data_str):
        """Parse the input data into a list of team records"""
        data_format = self.detect_format(data_str)
        teams = []
        
        if data_format == 'json':
            try:
                data = json.loads(data_str)
                if 'teams' in data:
                    teams = data['teams']
                else:
                    teams = [data]  # Single team object
            except json.JSONDecodeError:
                return None, "ERROR: Invalid JSON format."
        
        elif data_format == 'csv':
            try:
                csv_reader = csv.DictReader(io.StringIO(data_str))
                teams = list(csv_reader)
            except Exception as e:
                return None, f"ERROR: Invalid CSV format. {str(e)}"
        
        else:
            return None, "ERROR: Invalid data format. Please provide data in CSV or JSON format."
            
        return teams, None

    def validate_data(self, teams):
        """Validate the input data"""
        validation_report = []
        validation_errors = []
        
        validation_report.append("# Data Validation Report")
        validation_report.append("## Data Structure Check:")
        validation_report.append(f" - Number of teams: {len(teams)}")
        
        if teams:
            validation_report.append(f" - Number of fields per record: {len(teams[0])}")
        else:
            validation_report.append(" - Number of fields per record: 0")
            validation_errors.append("ERROR: No teams found in the input data.")
            return validation_report, validation_errors
        
        validation_report.append("\n## Required Fields Check:")
        for field in self.valid_fields:
            if all(field in team for team in teams):
                validation_report.append(f" - {field}: present")
            else:
                validation_report.append(f" - {field}: missing")
                for i, team in enumerate(teams):
                    if field not in team:
                        validation_errors.append(f"ERROR: Missing required field '{field}' in row {i+1}.")
        
        validation_report.append("\n## Data Type and Value Validation:")
        
        for i, team in enumerate(teams):
            for field in self.numeric_fields:
                if field in team:
                    try:
                        value = float(team[field])
                        
                        # Ensure positive integer for specific fields
                        if field in ["current_staff", "queries_per_day"]:
                            if not value.is_integer() or value <= 0:
                                validation_errors.append(f"ERROR: Invalid value for '{field}' in row {i+1}. Expected positive integer.")
                        
                        # Ensure positive number for other numeric fields
                        elif field in ["average_query_time", "shift_hours"]:
                            if value <= 0:
                                validation_errors.append(f"ERROR: Invalid value for '{field}' in row {i+1}. Expected positive number.")
                        
                        # Ensure percentage values (0-100)
                        elif field in self.percentage_fields:
                            if value < 0 or value > 100:
                                validation_errors.append(f"ERROR: Invalid value for '{field}' in row {i+1}. Expected value between 0 and 100.")
                                
                    except ValueError:
                        validation_errors.append(f"ERROR: Invalid data type for '{field}' in row {i+1}. Expected a numeric value.")
        
        # Add validation status for each field type
        for field in self.positive_fields[:2]:  # current_staff and queries_per_day
            if not any(f"Invalid value for '{field}'" in err for err in validation_errors):
                validation_report.append(f" - {field} (positive integer): validated")
            else:
                validation_report.append(f" - {field} (positive integer): not valid")
                
        for field in self.positive_fields[2:]:  # average_query_time and shift_hours
            if not any(f"Invalid value for '{field}'" in err for err in validation_errors):
                validation_report.append(f" - {field} (positive number): validated")
            else:
                validation_report.append(f" - {field} (positive number): not valid")
                
        for field in self.percentage_fields:
            if not any(f"Invalid value for '{field}'" in err for err in validation_errors):
                validation_report.append(f" - {field} (0 to 100): validated")
            else:
                validation_report.append(f" - {field} (0 to 100): not valid")
        
        validation_report.append("\n## Validation Summary:")
        if not validation_errors:
            validation_report.append("Data validation is successful!")
        else:
            validation_report.append("Validation failed with the following errors:")
            for error in validation_errors:
                validation_report.append(f"- {error}")
            validation_report.append("\nPlease correct and resubmit this data again.")
            
        return validation_report, validation_errors
    
    def calculate_metrics(self, team):
        """Calculate all metrics for a team"""
        # Convert data to numerical values
        team_data = {k: float(v) if k in self.numeric_fields else v for k, v in team.items()}
        
        # 1. Workload per Agent
        queries_per_day = team_data["queries_per_day"]
        avg_query_time = team_data["average_query_time"]
        current_staff = team_data["current_staff"]
        
        workload_step1 = queries_per_day * avg_query_time
        workload_per_agent = workload_step1 / current_staff
        
        # 2. Agent Capacity
        shift_hours = team_data["shift_hours"]
        available_capacity = team_data["available_capacity"]
        
        capacity_step1 = shift_hours * 60
        agent_capacity = capacity_step1 * (available_capacity / 100)
        
        # 3. Utilization Rate
        utilization_rate = (workload_per_agent / agent_capacity) * 100
        
        # 4. Composite Scheduling Score
        remote_efficiency = team_data["remote_infrastructure_efficiency"]
        
        capacity_surplus_percentage = ((agent_capacity - workload_per_agent) / agent_capacity) * 100
        weighted_surplus = capacity_surplus_percentage * 0.5
        weighted_efficiency = remote_efficiency * 0.3
        weighted_utilization = (100 - utilization_rate) * 0.2
        
        composite_score = weighted_surplus + weighted_efficiency + weighted_utilization
        
        # 5. Staffing Efficiency
        required_staff = (queries_per_day * avg_query_time) / agent_capacity
        staffing_efficiency_ratio = current_staff / required_staff
        
        # Determine recommendation
        is_optimal = (composite_score >= 60 and 
                      0.9 <= staffing_efficiency_ratio <= 1.1 and 
                      utilization_rate <= 90)
        
        status = "Optimal" if is_optimal else "Needs Adjustment"
        
        if is_optimal:
            recommendation = ("Based on a Composite Score of {:.2f}, a Staffing Efficiency Ratio of {:.2f}, "
                             "and a Utilization Rate of {:.2f}%, the team's scheduling is optimal. "
                             "The recommendation is to maintain the current workforce distribution.").format(
                                 composite_score, staffing_efficiency_ratio, utilization_rate)
        else:
            recommendation = ("Based on a Composite Score of {:.2f}, a Staffing Efficiency Ratio of {:.2f}, "
                             "and a Utilization Rate of {:.2f}%, the team's scheduling requires adjustments. "
                             "Consider reassigning workforce, adjusting shift timings, or enhancing remote infrastructure.").format(
                                 composite_score, staffing_efficiency_ratio, utilization_rate)
        
        # Return all metrics and steps
        return {
            # Input data
            "team_id": team_data["team_id"],
            "current_staff": current_staff,
            "queries_per_day": queries_per_day,
            "average_query_time": avg_query_time,
            "shift_hours": shift_hours,
            "available_capacity": available_capacity,
            "remote_infrastructure_efficiency": remote_efficiency,
            
            # Workload calculation
            "workload_step1": workload_step1,
            "workload_per_agent": workload_per_agent,
            
            # Capacity calculation
            "capacity_step1": capacity_step1,
            "agent_capacity": agent_capacity,
            
            # Utilization calculation
            "utilization_rate": utilization_rate,
            
            # Composite score calculation
            "capacity_surplus_percentage": capacity_surplus_percentage,
            "weighted_surplus": weighted_surplus,
            "weighted_efficiency": weighted_efficiency,
            "weighted_utilization": weighted_utilization,
            "composite_score": composite_score,
            
            # Staffing efficiency calculation
            "required_staff": required_staff,
            "staffing_efficiency_ratio": staffing_efficiency_ratio,
            
            # Recommendation
            "status": status,
            "recommendation": recommendation
        }
    
    def generate_report(self, teams):
        """Generate the full report for all teams"""
        team_results = [self.calculate_metrics(team) for team in teams]
        
        report = []
        report.append("# Workforce Distribution Summary:")
        report.append(f"Total Teams Evaluated: {len(teams)}")
        report.append("")
        
        for result in team_results:
            report.append(f"# Detailed Analysis per Team:")
            report.append(f"Team {result['team_id']}")
            report.append("Input Data:")
            report.append(f" - Current Staff: {result['current_staff']:.0f}")
            report.append(f" - Queries Per Day: {result['queries_per_day']:.0f}")
            report.append(f" - Average Query Time (minutes): {result['average_query_time']:.2f}")
            report.append(f" - Shift Hours: {result['shift_hours']:.2f}")
            report.append(f" - Available Capacity (%): {result['available_capacity']:.2f}")
            report.append(f" - Remote Infrastructure Efficiency (%): {result['remote_infrastructure_efficiency']:.2f}")
            report.append("")
            
            report.append("# Detailed Calculations:")
            
            # 1. Workload per Agent
            report.append("## 1. Workload per Agent Calculation:")
            report.append(" - Formula: $$ \\text{Workload per Agent} = \\frac{\\text{queries_per_day} \\times \\text{average_query_time}}{\\text{current_staff}} $$")
            report.append(" - Calculation Steps:")
            report.append(f"   Step 1: Multiply queries_per_day by average_query_time: {result['queries_per_day']:.2f} × {result['average_query_time']:.2f} = {result['workload_step1']:.2f}")
            report.append(f"   Step 2: Divide the result by current_staff: {result['workload_step1']:.2f} ÷ {result['current_staff']:.2f} = {result['workload_per_agent']:.2f}")
            report.append(f" - Final Workload per Agent: {result['workload_per_agent']:.2f}")
            report.append("")
            
            # 2. Agent Capacity
            report.append("## 2. Agent Capacity Calculation:")
            report.append(" - Formula: $$ \\text{Agent Capacity} = \\text{shift_hours} \\times 60 \\times \\frac{\\text{available_capacity}}{100} $$")
            report.append(" - Calculation Steps:")
            report.append(f"   Step 1: Multiply shift_hours by 60: {result['shift_hours']:.2f} × 60 = {result['capacity_step1']:.2f}")
            report.append(f"   Step 2: Multiply the result by (available_capacity/100): {result['capacity_step1']:.2f} × ({result['available_capacity']:.2f}/100) = {result['agent_capacity']:.2f}")
            report.append(f" - Final Agent Capacity: {result['agent_capacity']:.2f}")
            report.append("")
            
            # 3. Utilization Rate
            report.append("## 3. Utilization Rate Calculation:")
            report.append(" - Formula: $$ \\text{Utilization Rate} = \\frac{\\text{Workload per Agent}}{\\text{Agent Capacity}} \\times 100 $$")
            report.append(" - Calculation Steps:")
            report.append(f"   Step 1: Divide Workload per Agent by Agent Capacity: {result['workload_per_agent']:.2f} ÷ {result['agent_capacity']:.2f} = {result['workload_per_agent']/result['agent_capacity']:.4f}")
            report.append(f"   Step 2: Multiply the result by 100: {result['workload_per_agent']/result['agent_capacity']:.4f} × 100 = {result['utilization_rate']:.2f}")
            report.append(f" - Final Utilization Rate: {result['utilization_rate']:.2f}%")
            report.append("")
            
            # 4. Composite Scheduling Score
            report.append("## 4. Composite Scheduling Score Calculation:")
            report.append(" - Step 1: Calculate Capacity Surplus Percentage:")
            report.append(" $$ \\text{Capacity Surplus Percentage} = \\frac{(\\text{Agent Capacity} - \\text{Workload per Agent})}{\\text{Agent Capacity}} \\times 100 $$")
            report.append(f"   Calculation: ({result['agent_capacity']:.2f} - {result['workload_per_agent']:.2f}) ÷ {result['agent_capacity']:.2f} × 100 = {result['capacity_surplus_percentage']:.2f}%")
            
            report.append(f" - Step 2: Multiply the Capacity Surplus Percentage by 0.5: {result['capacity_surplus_percentage']:.2f} × 0.5 = {result['weighted_surplus']:.2f}")
            report.append(f" - Step 3: Multiply remote_infrastructure_efficiency by 0.3: {result['remote_infrastructure_efficiency']:.2f} × 0.3 = {result['weighted_efficiency']:.2f}")
            report.append(f" - Step 4: Subtract the Utilization Rate from 100, then multiply by 0.2: (100 - {result['utilization_rate']:.2f}) × 0.2 = {result['weighted_utilization']:.2f}")
            
            report.append(" - Step 5: Sum the weighted values:")
            report.append(" $$ \\text{Composite Score} = (\\text{Capacity Surplus Percentage} \\times 0.5) + (\\text{remote_infrastructure_efficiency} \\times 0.3) + ((100 - \\text{Utilization Rate}) \\times 0.2) $$")
            report.append(f"   Calculation: {result['weighted_surplus']:.2f} + {result['weighted_efficiency']:.2f} + {result['weighted_utilization']:.2f} = {result['composite_score']:.2f}")
            report.append(f" - Final Composite Score: {result['composite_score']:.2f}")
            report.append("")
            
            # 5. Staffing Efficiency
            report.append("## 5. Staffing Efficiency Calculation:")
            report.append(" - Formula for Required Staff:")
            report.append(" $$ \\text{Required Staff} = \\frac{\\text{queries_per_day} \\times \\text{average_query_time}}{\\text{Agent Capacity}} $$")
            report.append(f"   Calculation: ({result['queries_per_day']:.2f} × {result['average_query_time']:.2f}) ÷ {result['agent_capacity']:.2f} = {result['required_staff']:.2f}")
            
            report.append(" - Formula for Staffing Efficiency Ratio:")
            report.append(" $$ \\text{Staffing Efficiency Ratio} = \\frac{\\text{current_staff}}{\\text{Required Staff}} $$")
            report.append(f"   Calculation: {result['current_staff']:.2f} ÷ {result['required_staff']:.2f} = {result['staffing_efficiency_ratio']:.2f}")
            report.append(f" - Final Staffing Efficiency Ratio: {result['staffing_efficiency_ratio']:.2f}")
            report.append("")
            
            # Final Recommendation
            report.append("# Final Recommendation per Team:")
            report.append(f" - Composite Score: {result['composite_score']:.2f}")
            report.append(f" - Utilization Rate: {result['utilization_rate']:.2f}%")
            report.append(f" - Staffing Efficiency Ratio: {result['staffing_efficiency_ratio']:.2f}")
            report.append(f" - Status: {result['status']}")
            report.append(f" - Recommended Action: {result['recommendation']}")
            report.append("")
            
        # Add the feedback request
        report.append("# FEEDBACK AND RATING PROTOCOL")
        report.append("Would you like detailed calculations for any specific team? Please rate this analysis on a scale of 1-5.")
        
        return "\n".join(report)
    
    def process_input(self, input_data):
        """Process the input data and generate a report"""
        teams, error = self.parse_data(input_data)
        
        if error:
            return error
        
        validation_report, validation_errors = self.validate_data(teams)
        validation_report_str = "\n".join(validation_report)
        
        if validation_errors:
            return validation_report_str
            
        final_report = self.generate_report(teams)
        return f"{validation_report_str}\n\n{final_report}"
    
    def provide_template(self, format_type="both"):
        """Provide data input templates"""
        templates = []
        
        if format_type in ["csv", "both"]:
            templates.append("CSV Template:")
            templates.append("```csv")
            templates.append("team_id,current_staff,queries_per_day,average_query_time,shift_hours,available_capacity,remote_infrastructure_efficiency")
            templates.append("[String],[positive integer],[positive integer],[positive number in minutes],[positive number],[0-100],[0-100]")
            templates.append("```")
        
        if format_type in ["json", "both"]:
            templates.append("JSON Template:")
            templates.append("```json")
            templates.append("{")
            templates.append(' "teams": [')
            templates.append(' {')
            templates.append(' "team_id": "[String]",')
            templates.append(' "current_staff": [positive integer],')
            templates.append(' "queries_per_day": [positive integer],')
            templates.append(' "average_query_time": [positive number in minutes],')
            templates.append(' "shift_hours": [positive number],')
            templates.append(' "available_capacity": [0-100],')
            templates.append(' "remote_infrastructure_efficiency": [0-100]')
            templates.append(' }')
            templates.append(' ]')
            templates.append('}')
            templates.append("```")
        
        return "\n".join(templates)
    
    def handle_feedback(self, rating):
        """Handle user feedback based on rating"""
        rating = int(rating)
        
        if rating == 1:
            return "We are very sorry that the analysis did not meet your expectations. Could you please provide specific feedback on what went wrong?"
        elif rating == 2:
            return "Thank you for your feedback. We appreciate your input and would love to know more details on how we can improve."
        elif rating == 3:
            return "Thank you for your feedback. We are committed to continuous improvement. Could you share what aspects need enhancement?"
        elif rating == 4:
            return "Thank you for your positive feedback! We're glad the analysis was helpful."
        elif rating == 5:
            return "Thank you for your excellent feedback! We are thrilled to have met your expectations and appreciate your input."
        else:
            return "Please rate this analysis on a scale of 1-5."

def main():
    optimizer = WorkforceOptimizer()
    
    # Sample data in JSON format
    sample_data = {
  "teams": [
    {
      "team_id": "TeamOmega",
      "current_staff": 10,
      "queries_per_day": 150,
      "average_query_time": 3.0,
      "shift_hours": 8,
      "available_capacity": 70,
      "remote_infrastructure_efficiency": 80
    },
    {
      "team_id": "TeamSigma",
      "current_staff": 12,
      "queries_per_day": 170,
      "average_query_time": 3.5,
      "shift_hours": 7,
      "available_capacity": 75,
      "remote_infrastructure_efficiency": 85
    },
    {
      "team_id": "TeamTheta",
      "current_staff": 8,
      "queries_per_day": 140,
      "average_query_time": 2.8,
      "shift_hours": 6,
      "available_capacity": 65,
      "remote_infrastructure_efficiency": 90
    },
    {
      "team_id": "TeamLambda",
      "current_staff": 11,
      "queries_per_day": 160,
      "average_query_time": 3.2,
      "shift_hours": 7.5,
      "available_capacity": 80,
      "remote_infrastructure_efficiency": 88
    },
    {
      "team_id": "TeamZeta",
      "current_staff": 9,
      "queries_per_day": 130,
      "average_query_time": 3.6,
      "shift_hours": 8,
      "available_capacity": 68,
      "remote_infrastructure_efficiency": 82
    }
  ]
}
    
    # Convert sample data to JSON string
    input_data = json.dumps(sample_data)
    
    # Process the data and print results
    try:
        result = optimizer.process_input(input_data)
        print(result)
    except Exception as e:
        print(f"ERROR: An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
