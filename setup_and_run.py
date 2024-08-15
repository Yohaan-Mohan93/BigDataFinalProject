import os
import platform
import subprocess
import sys

def create_virtual_environment():
    """Creates a virtual environment in the current directory."""
    if platform.system() == 'Windows':
        subprocess.check_call([sys.executable, '-m', 'venv', '.'])
    else:
        subprocess.check_call([sys.executable, '-m', 'venv', '.'])

def install_requirements(requirements_file='requirements.txt'):
    """Installs the necessary requirements."""
    if platform.system() == 'Windows':
        pip_executable = os.path.join('Scripts', 'pip')
    else:
        pip_executable = os.path.join('bin', 'pip')

    subprocess.check_call([pip_executable, 'install', '-r', requirements_file])

def run_script(script_name):
    """Runs a Python script within the virtual environment."""
    if platform.system() == 'Windows':
        python_executable = os.path.join('Scripts', 'python')
    else:
        python_executable = os.path.join('bin', 'python')

    subprocess.check_call([python_executable, script_name])

def main():
    requirements_file = 'requirements.txt'
    migrate_script = 'migrate.py'
    train_script = 'train_model.py'

    print("Creating virtual environment in the current directory...")
    create_virtual_environment()
    
    print(f"Installing requirements from '{requirements_file}'...")
    install_requirements(requirements_file)

    print(f"Running migration script '{migrate_script}'...")
    run_script(migrate_script)

    print(f"Running training script '{train_script}'...")
    run_script(train_script)

    print("Setup and scripts execution completed successfully.")

if __name__ == '__main__':
    main()
