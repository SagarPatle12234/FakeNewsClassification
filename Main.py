import os
import mlflow
from dotenv import load_dotenv

# 1. Load the hidden environment variables into Python
load_dotenv()

# 2. Set your DAGsHub credentials using the .env variable
os.environ["MLFLOW_TRACKING_USERNAME"] = "SagarPatle12234"
os.environ["MLFLOW_TRACKING_PASSWORD"] = os.getenv("DAGSHUB_PAT")

# 3. Connect to the server
mlflow.set_tracking_uri("https://dagshub.com/SagarPatle12234/FakeNewsClassification.mlflow")
mlflow.set_experiment("Baseline_Text_Classification")

print("Successfully connected securely using .env!")