import subprocess
import argparse

# Argument parsing to allow dynamic input from Cloud Run Jobs
parser = argparse.ArgumentParser()
parser.add_argument(
    "--level", required=True, type=str, choices=["A1", "A2", "B1", "B2", "C1"],
    help="Target level for the generated text"
)
parser.add_argument("--n_samples", default=10, type=int, help="Number of samples to generate")
args = parser.parse_args()

# Run the download script
subprocess.run(["python", "download_train_datasets.py"])

# Run gen_samples.py with the specified level and number of samples
subprocess.run(["python", "gen_samples.py", "--level", args.level, "--n_samples", str(args.n_samples)])

# import subprocess

# # Run the download script
# subprocess.run(["python3", "download_train_datasets.py"])

# # List of (level, n_samples) pairs
# params = [
#     ("A1", 100),
#     ("A2", 100),
#     ("B1", 100),
#     ("B2", 100),
#     ("C1", 100),
# ]

# for level, n_samples in params:
#     subprocess.run(["python3", "gen_samples.py", "--level", level, "--n_samples", str(n_samples)])
