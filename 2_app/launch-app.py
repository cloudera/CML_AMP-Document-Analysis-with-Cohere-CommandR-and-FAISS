import subprocess

print(subprocess.run(["streamlit run ./2_app/chatbot.py --server.port $CDSW_APP_PORT --server.address 127.0.0.1"], shell=True))

