import subprocess

def get_current_requirements(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines

def get_pip_freeze_output():
    result = subprocess.run(['pip', 'freeze'], stdout=subprocess.PIPE, text=True)
    return result.stdout.splitlines()

def parse_requirements(lines):
    github_packages = {}
    other_packages = {}
    for line in lines:
        if 'git+' in line:
            package_name = line.split('egg=')[-1].strip()
            github_packages[package_name] = line.strip()
        else:
            package_name = line.split('==')[0].strip()
            other_packages[package_name] = line.strip()
    return github_packages, other_packages

def merge_requirements(github_packages, pip_freeze_lines):
    merged_requirements = []
    for line in pip_freeze_lines:
        package_name = line.split('==')[0].strip()
        if package_name in github_packages:
            merged_requirements.append(github_packages[package_name])
        else:
            merged_requirements.append(line)
    return merged_requirements

def write_requirements(file_path, requirements):
    with open(file_path, 'w') as file:
        for line in requirements:
            file.write(f"{line}\n")

def update_requirements(file_path):
    current_lines = get_current_requirements(file_path)
    pip_freeze_lines = get_pip_freeze_output()
    
    github_packages, other_packages = parse_requirements(current_lines)
    
    merged_requirements = merge_requirements(github_packages, pip_freeze_lines)
    
    write_requirements(file_path, merged_requirements)

if __name__ == "__main__":
    requirements_file = 'requirements.txt'
    update_requirements(requirements_file)
