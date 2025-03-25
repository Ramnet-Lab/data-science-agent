#!/usr/bin/env python3
"""
Command-line script to run data analysis using the Data Science Agent.
"""

import os
import argparse
import sys
from src.agent import DataScienceAgent

def main():
    """Main function to parse arguments and run the analysis."""
    parser = argparse.ArgumentParser(description="Run data analysis using the Data Science Agent")
    
    parser.add_argument("--file", "-f", required=True, help="Path to the data file (CSV or Excel)")
    parser.add_argument("--objective", "-o", default=None, help="Analysis objective")
    parser.add_argument("--api-key", "-k", default=None, help="OpenAI API key (or set OPENAI_API_KEY environment variable)")
    parser.add_argument("--model", "-m", default="gpt-4o", help="OpenAI model to use")
    parser.add_argument("--output", default="analysis_results.txt", help="Output file for analysis results")
    
    args = parser.parse_args()
    
    # Check if file exists
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)
    
    # Get API key from args or environment
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("Error: OpenAI API key is required. Provide it with --api-key or set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    try:
        # Initialize agent
        print(f"Initializing agent with model {args.model}...")
        agent = DataScienceAgent(api_key=api_key, model=args.model)
        
        # Create analysis prompt
        prompt = agent.create_analysis_prompt(
            file_path=args.file,
            objective=args.objective
        )
        
        # Run analysis
        print(f"Running analysis on {args.file}...")
        results = agent.run(prompt)
        
        # Save results to file
        with open(args.output, "w") as f:
            f.write(results)
        
        print(f"Analysis completed! Results saved to {args.output}")
        
        # Check for generated plots
        if os.path.exists("eda_plots"):
            plot_files = [f for f in os.listdir("eda_plots") if f.endswith((".png", ".jpg", ".jpeg"))]
            if plot_files:
                print(f"Generated {len(plot_files)} plots in the 'eda_plots' directory:")
                for plot_file in plot_files:
                    print(f"  - {os.path.join('eda_plots', plot_file)}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()