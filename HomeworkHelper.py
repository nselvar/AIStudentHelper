import os
import subprocess


class HomeworkHelper:
    def __init__(self):
        # Run Streamlit app
        script_path = os.path.join(os.getcwd(), "homeworkhelper", "streamlit_app.py")  # ✅ Correct path
        subprocess.run(["streamlit", "run", script_path], check=True)  # ✅ Pass full file path
