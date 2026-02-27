#!/usr/bin/env python3
import os
import subprocess
import sys

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 1. Run build.py
    print("Running build process...")
    build_script = os.path.join(base_dir, 'scripts', 'build.py')
    try:
        subprocess.run([sys.executable, build_script], check=True, cwd=base_dir)
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        sys.exit(1)
        
    # 2. Run Terraform init and apply
    print("Running Terraform deployment...")
    terraform_dir = os.path.join(base_dir, 'terraform')
    try:
        subprocess.run(['terraform', 'init'], check=True, cwd=terraform_dir)
        subprocess.run(['terraform', 'apply', '-auto-approve'], check=True, cwd=terraform_dir)
    except subprocess.CalledProcessError as e:
        print(f"Terraform deployment failed: {e}")
        sys.exit(1)
        
    print("Deployment completed successfully!")

if __name__ == "__main__":
    main()
