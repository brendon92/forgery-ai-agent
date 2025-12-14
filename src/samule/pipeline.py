import json
from src.samule.collector import collector
from src.samule.analyzer import analyzer
from src.samule.generator import generator

def run_pipeline():
    print("Starting SAMULE Self-Improvement Pipeline...")
    
    # 1. Collect Traces
    traces = collector.fetch_traces(limit=10)
    if not traces:
        print("No traces found. Run the agent first to generate data.")
        # For demo purposes, let's mock a failure trace if none exist
        traces = [{"id": "mock-trace", "mock_failure": True}]
    
    # 2. Analyze Failures
    # In our mock analyzer, we need to force it to see a failure for the demo
    failures = analyzer.identify_failures(traces)
    
    # Force a mock failure if logic returns empty (since we have no real data)
    if not failures and traces:
        print("No failures detected by analyzer. Using mock failure for demonstration.")
        failures = [traces[0]]
    
    print(f"Processing {len(failures)} failures...")
    
    # 3. Generate Synthetic Data
    dataset = []
    for failure in failures:
        print(f"Generating correction for trace {failure.get('id', 'unknown')}...")
        try:
            example = generator.create_sft_example(failure)
            dataset.append(example)
        except Exception as e:
            print(f"Failed to generate correction: {e}")
            
    # 4. Export Dataset
    if dataset:
        output_file = "data/sft_dataset.json"
        with open(output_file, "w") as f:
            json.dump(dataset, f, indent=2)
        print(f"Successfully exported {len(dataset)} SFT examples to {output_file}")
    else:
        print("No dataset generated.")

if __name__ == "__main__":
    run_pipeline()
