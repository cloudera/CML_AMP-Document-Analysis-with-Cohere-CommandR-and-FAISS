import subprocess

print(subprocess.run(["sh 0_session-install-requirements/install_requirements.sh"], shell=True))