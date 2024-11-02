import os
import subprocess
import argparse

parser = argparse.ArgumentParser(description="Run docker-compose with optional override files and optional build flag.")
parser.add_argument("--build", action="store_true", help="Add --build flag to docker-compose command")

args = parser.parse_args()


compose_file = os.path.join("compose", "docker-compose.yml")

override_files = []
mainDirs = ('ModelsRepository', 'WebUI')

for base in mainDirs:
    for root, dirs, files in os.walk(base):
        for file in files:
            if file == "docker-compose.override.yml":
                override_files.append(os.path.join(root, file))

command = ["docker-compose", "-f", compose_file] + [f'-f "{file}"' for file in override_files] + ["up", "-d"]
if args.build:
    command.append("--build")
    
command_str = ' '.join(command)
print(command_str)

subprocess.run(command_str, shell=True)
