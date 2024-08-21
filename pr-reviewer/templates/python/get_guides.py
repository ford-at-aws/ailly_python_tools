import os
import shutil
import subprocess

from git import Repo

# Configuration
repo_url = "https://github.com/boto/boto3.git"
branch = "develop"
directory_to_copy = "docs/source/guide"
local_repo_dir = "boto3-repo"
local_copy_dir = "guide"

# Clone the specific branch of the repository
if os.path.exists(local_repo_dir):
    shutil.rmtree(local_repo_dir)

print("Cloning the repository...")
Repo.clone_from(repo_url, local_repo_dir, branch=branch)

# Copy the specific directory to a new location
src_dir = os.path.join(local_repo_dir, directory_to_copy)
if os.path.exists(local_copy_dir):
    shutil.rmtree(local_copy_dir)

shutil.copytree(src_dir, local_copy_dir)

# Convert .rst files to .md using pandoc
for root, _, files in os.walk(local_copy_dir):
    for file in files:
        if file.endswith(".rst"):
            rst_file = os.path.join(root, file)
            md_file = os.path.join(root, file.replace(".rst", ".md"))
            print(f"Converting {rst_file} to {md_file}...")
            subprocess.run(
                ["pandoc", "-f", "rst", "-t", "markdown", "-o", md_file, rst_file]
            )

print("Conversion complete!")

# Clean up the cloned repository
shutil.rmtree(local_repo_dir)
