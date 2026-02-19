🚀 How to Run the Application in VS Code
Follow these step-by-step instructions to start the live dashboard on your local machine:

Step 1: Open the Project in VS Code
Open VS Code.

Go to the top menu and click File > Open Folder...

Select the Intraday_Dashboard folder where your files are saved.

Step 2: Open the Integrated Terminal
You need the terminal to type in the commands that run the application.

In VS Code, go to the top menu and click Terminal > New Terminal.

Alternatively, you can use the keyboard shortcut: Ctrl + ` (Control + Backtick).

Step 3: Install the Required Libraries
Before running the app for the first time, you must install the necessary Python tools.

In the terminal window at the bottom of your screen, ensure your path shows you are inside the Intraday_Dashboard folder.

Type the following command and press Enter:

Bash
pip install -r requirements.txt
Wait for the installation to finish (you will see a success message when it is done). You only ever have to do this step once.

Step 4: Run the Dashboard
Now it is time to launch the application.

In the same terminal, type the following command and press Enter:

Bash
streamlit run app.py
Step 5: View Your Dashboard
Once the command runs, a new tab will automatically open in your default web browser (like Chrome or Edge).

If it does not open automatically, look at the terminal output. You will see a "Local URL" (usually http://localhost:8501). Hold the Ctrl key and click that link to open it.

🛑 How to Stop the Application
When you are done trading for the day, you should stop the application so it doesn't keep requesting data in the background.

Go back to your VS Code terminal.

Click inside the terminal window and press Ctrl + C on your keyboard to shut down the Streamlit server.

You can safely close VS Code and your browser tab.
