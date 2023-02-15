# Speedtest-tracker

This Python code provides a Graphical User Interface (GUI) for running internet speed tests using the `speedtest-cli` library, and display the results in a chart and a table.

The code uses `tkinter` to create a simple GUI with `azure-ttk-theme` style. The program features a table to display the speed test results, and a chart that visually represents the download, upload, and ping speeds over time.

![image](https://user-images.githubusercontent.com/87757968/219075903-7519c252-d222-4784-8f69-8d4753604bf3.png)

## Prerequisites

-   Python 3.6 or higher
-   Required libraries: `speedtest-cli`, `tkinter`, `pandas`, `matplotlib`, `Pillow`

## Installation

1.  Install Python 3.x.
2. To download the project, follow these steps:

	1.  Go to the project's GitHub page at https://github.com/NpFHs/speedtest-tracker.
	2.  Click on the green "Code" button and select "Download ZIP" to download the project as a zip file.
	3.  Extract the files from the zip file to a directory of your choice.

	Alternatively, you can also clone the repository using git. Here are the instructions for doing so:

	1.  Open a terminal window.
	2.  Change to the directory where you want to clone the repository.
	3.  Run the following command:
	`git clone https://github.com/NpFHs/speedtest-tracker.git` 

	This will create a new directory called `speedtest-tracker` and download the files from the repository into it.
3.  Install the required libraries using the following command:
    `pip install speedtest-cli tkinter pandas matplotlib Pillow`
    

## Usage

To run the speed test program, simply run the script with Python. The program will appear on the screen, showing the table of results and the chart.

### Running a speed test
1.  Set the break time between tests in the `Settings` section. Enter a number between 1-60 and select whether it is in seconds, minutes, or hours. Click `Set` to save the settings. If you don't set a time, the default interval is 10 minutes.
2.  Click the `Start` button to start the speed test. The GUI will automatically run a new test every 60 seconds.
3.  Wait for the test to complete. The results will be displayed in the table and the chart.
4.  You can stop the speed test at any time by clicking the `Stop` button.

### Viewing the results

The speed test results are displayed in a table. The table shows the download speed, upload speed, and ping time for each test.

The results are also displayed in a chart that shows the download, upload, and ping speeds over time. The chart is automatically updated every time a new test is completed.
