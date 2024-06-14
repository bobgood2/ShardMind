import os
import numpy as np
from azureml.core import Workspace, Experiment, ScriptRunConfig, Environment
from azureml.core.compute import AmlCompute, ComputeTarget

class AzureMLVectorizer:
    def __init__(self, workspace_config_path, compute_name, experiment_name, vm_size="STANDARD_NC6", min_nodes=0, max_nodes=4):
        self.workspace_config_path = workspace_config_path
        self.compute_name = compute_name
        self.experiment_name = experiment_name
        self.vm_size = vm_size
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.workspace = Workspace.from_config(path=workspace_config_path)
        self.compute_target = self._get_or_create_compute_target()

    def _get_or_create_compute_target(self):
        if self.compute_name in self.workspace.compute_targets:
            compute_target = self.workspace.compute_targets[self.compute_name]
            if compute_target and type(compute_target) is AmlCompute:
                print(f"Found existing compute target: {self.compute_name}")
                return compute_target
        else:
            compute_config = AmlCompute.provisioning_configuration(vm_size=self.vm_size, min_nodes=self.min_nodes, max_nodes=self.max_nodes)
            compute_target = ComputeTarget.create(self.workspace, self.compute_name, compute_config)
            compute_target.wait_for_completion(show_output=True)
            print(f"Created new compute target: {self.compute_name}")
            return compute_target

    def create_vector(self, query_text, environment_file_path="environment.yml", script_name="inference_script.py"):
        # Create the inference script
        with open(script_name, "w") as script_file:
            script_file.write(f"""
from sentence_transformers import SentenceTransformer
import numpy as np

def main():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_text = "{query_text}"
    encoded_vector = model.encode([query_text], convert_to_tensor=True).cpu().numpy()
    np.save("encoded_vector.npy", encoded_vector)

if __name__ == "__main__":
    main()
""")

        # Set up the environment with the required dependencies
        env = Environment.from_conda_specification(name="sentence-embedding-env", file_path=environment_file_path)

        # Create a script configuration
        src = ScriptRunConfig(source_directory=".", script=script_name, compute_target=self.compute_target, environment=env)

        # Submit the experiment
        experiment = Experiment(self.workspace, self.experiment_name)
        run = experiment.submit(src)
        run.wait_for_completion(show_output=True)

        # Download the encoded vector
        run.download_file(name="outputs/encoded_vector.npy", output_file_path="encoded_vector.npy")

        # Load and return the vector
        encoded_vector = np.load("encoded_vector.npy")
        return encoded_vector

if __name__ == "__main__":
    # Sample usage
    workspace_config_path = "config.json"
    compute_name = "gpu-cluster"
    experiment_name = "sentence-embedding"
    query_text = "Sample text for encoding"
    environment_file_path = "environment.yml"

    vectorizer = AzureMLVectorizer(workspace_config_path, compute_name, experiment_name)
    vector = vectorizer.create_vector(query_text, environment_file_path)
    print("Encoded vector:", vector)
