import os
import subprocess

compose_file = os.path.join("compose", "docker-compose.yml")

override_files = []
for root, dirs, files in os.walk("ModelsRepository"):
    for file in files:
        if file == "docker-compose.override.yml":
            override_files.append((os.path.join(root, file)))

# Przygotowanie polecenia
command = ["docker-compose", "-f", compose_file] + [f'-f "{file}"' for file in override_files] + ["up", "-d"]
command = ' '.join(command)
print(command)
# Uruchomienie polecenia
subprocess.run(command)
