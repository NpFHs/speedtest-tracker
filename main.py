import time
import speedtest
import tkinter as tk
from threading import *
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import warnings

warnings.simplefilter("ignore", UserWarning)
# time between speedtests (in seconds)
SLEEP_TIME = 60

servers = []
# If you want to test against a specific server
# servers = [1234]

threads = None
results_dicts_list = []
is_speedtest_run = False


# If you want to use a single threaded test
# threads = 1


def clear_csv_file():
    # clear the csv file (if exist)
    with open("results.csv", "w") as csv_file:
        csv_file.write("")


def show_chart(image_label: tk.Label):
    plt.rcParams["figure.figsize"] = [7.50, 3.50]
    plt.rcParams["figure.autolayout"] = True

    headers = ['Download [Mbps]', 'Upload [Mbps]', 'Ping [ms]']
    df = pd.read_csv('results.csv', names=headers)
    try:
        df.plot()

        # save the chart
        plt.savefig("speedtest_chart.png")

        # update the chart
        chart = ImageTk.PhotoImage(Image.open("speedtest_chart.png"))
        image_label.configure(image=chart)
        # keep reference to the chart, so it doesn't get prematurely garbage collected at the end of the function
        image_label.image = chart
    except TypeError:
        # when the CSV file empty
        clear_chart = ImageTk.PhotoImage(Image.open("./images/speedtest_clear_chart.png"))
        image_label.configure(image=clear_chart)
        # keep reference to the chart, so it doesn't get prematurely garbage collected at the end of the function
        image_label.image = clear_chart
        # print("no data to show!")
    # # show the chart in new window
    # plt.show()


def export_to_csv(tuple_results):
    with open("results.csv", "a") as csv_file:
        results_to_csv = str(tuple_results).strip("()")
        csv_file.write(f"{results_to_csv}\n")


# update the table and the csv file
def update_table(speeds_list):
    # clear the current table
    try:
        speeds_list.delete(*speeds_list.get_children())
    except tk.TclError:
        pass

    clear_csv_file()

    for result in results_dicts_list:
        mb_download = round(result["download"] / 1000000, 2)
        mb_upload = round(result["upload"] / 1000000, 2)
        ping_res = result['ping']

        tuple_results = (mb_download, mb_upload, ping_res)
        try:
            speeds_list.insert("", tk.END, values=tuple_results)
        except tk.TclError:
            pass

        # create and write the results to csv file
        export_to_csv(tuple_results)


def new_speedtest(speeds_list, chart_label, download, upload, ping):
    global results_dicts_list

    try:
        s = speedtest.Speedtest()
        s.get_servers(servers)
        s.get_best_server()
        s.download(threads=threads)
        s.upload(threads=threads)
        s.results.share()

        results_dict = s.results.dict()
    except (speedtest.SpeedtestBestServerFailure, speedtest.ConfigRetrievalError):
        # results when unable to connect
        results_dict = {'download': 0, 'upload': 0, 'ping': 0,
                        'server': {'url': 'Unknown', 'lat': 'Unknown', 'lon': 'Unknown', 'name': 'Unknown',
                                   'country': 'Unknown', 'cc': 'Unknown', 'sponsor': 'Unknown', 'id': 'Unknown',
                                   'host': 'Unknown', 'd': 0, 'latency': 0}, 'timestamp': 'Unknown', 'bytes_sent': 0,
                        'bytes_received': 0, 'share': 'Unknown',
                        'client': {'ip': 'Unknown', 'lat': 'Unknown', 'lon': 'Unknown', 'isp': 'Unknown',
                                   'isprating': '0', 'rating': '0', 'ispdlavg': '0', 'ispulavg': '0', 'loggedin': '0',
                                   'country': 'Unknown'}}
    print(results_dict)
    results_dicts_list.append(results_dict)

    update_vars(download, upload, ping)
    update_table(speeds_list)
    show_chart(chart_label)


def test_to_vars(speeds_list, chart_label, download, upload, ping):
    t = Thread(target=lambda: new_speedtest(speeds_list, chart_label, download, upload, ping))
    t.start()


def update_vars(download, upload, ping):
    result = results_dicts_list[-1]

    # print the result on the screen
    mb_download = round(result["download"] / 1000000, 2)
    mb_upload = round(result["upload"] / 1000000, 2)
    ping_res = result['ping']

    download.set(f"download: {mb_download} Mb/s")
    upload.set(f"upload: {mb_upload} Mb/s")
    ping.set(f"ping: {ping_res} ms")


def speedtests_loop(speeds_list, chart_label, download, upload, ping):
    print("speedtest started")
    while is_speedtest_run:
        test_to_vars(speeds_list, chart_label, download, upload, ping)
        time.sleep(SLEEP_TIME)
    print("speedtest really stopped")


def start_speedtests_loop(speeds_list, chart_label, download, upload, ping):
    global is_speedtest_run

    is_speedtest_run = True
    speedtests = Thread(target=lambda: speedtests_loop(speeds_list, chart_label, download, upload, ping))
    speedtests.start()


def stop_speedtests_loop():
    global is_speedtest_run
    print("speedtest stopped")
    is_speedtest_run = False


def set_sleep_time(sleep_time_var, sleep_time_type):
    global SLEEP_TIME

    time_type = sleep_time_type.get()
    sleep_time = sleep_time_var.get()
    if time_type == 1:
        SLEEP_TIME = sleep_time
    elif time_type == 2:
        SLEEP_TIME = sleep_time * 60
    elif time_type == 3:
        SLEEP_TIME = sleep_time * 60 * 60
    print(f"sleep_time: {SLEEP_TIME}")


def main():
    clear_csv_file()

    win = tk.Tk()

    # add azure theme
    win.tk.call("source", "azure.tcl")
    win.tk.call("set_theme", "dark")

    win.title("Speedtest Tracking")
    win.resizable(width=False, height=False)
    download_var = tk.StringVar(value="Download: ")
    upload_var = tk.StringVar(value="Upload: ")
    ping_var = tk.StringVar(value="Ping: ")
    sleep_time_var = tk.IntVar(value=1)
    time_type_var = tk.IntVar(value=1)

    current_results_frame = ttk.LabelFrame(win, text="Current results", padding=(20, 10))
    current_results_frame.grid(row=0, column=0, rowspan=3, sticky="news", padx=10, pady=10)

    current_download_label = ttk.Label(current_results_frame, textvariable=download_var)
    current_download_label.grid(row=0, column=0, padx=10, pady=10)
    current_upload_label = ttk.Label(current_results_frame, textvariable=upload_var)
    current_upload_label.grid(row=1, column=0, padx=10, pady=10)
    current_ping_label = ttk.Label(current_results_frame, textvariable=ping_var)
    current_ping_label.grid(row=2, column=0, padx=10, pady=10)

    settings_frame = ttk.LabelFrame(win, text="settings", padding=(20, 10))
    settings_frame.grid(row=0, column=1, columnspan=2, sticky="news", padx=10, pady=(10, 0))

    settings_label = ttk.Label(settings_frame, text="Run speedtest once in:")
    settings_label.grid(row=0, column=0)

    time_spinbox = ttk.Spinbox(settings_frame, from_=1, to=60, increment=1, textvariable=sleep_time_var, width=5)
    time_spinbox.grid(row=0, column=1, padx=10, pady=10, sticky="news")

    seconds_radio = ttk.Radiobutton(settings_frame, text="seconds", variable=time_type_var, value=1)
    seconds_radio.grid(row=0, column=2, padx=10, pady=10, sticky="news")
    minutes_radio = ttk.Radiobutton(settings_frame, text="minutes", variable=time_type_var, value=2)
    minutes_radio.grid(row=0, column=3, padx=10, pady=10, sticky="news")
    hours_radio = ttk.Radiobutton(settings_frame, text="hours", variable=time_type_var, value=3)
    hours_radio.grid(row=0, column=4, padx=10, pady=10, sticky="news")

    set_button = ttk.Button(settings_frame, text="Set", command=lambda: set_sleep_time(sleep_time_var, time_type_var))
    set_button.grid(row=0, column=5, padx=10, pady=10)

    columns = ("download", "upload", "ping")
    speeds_list = ttk.Treeview(win, columns=columns)
    speeds_list["show"] = "headings"  # to avoid empty column in the beginning
    speeds_list.heading("download", text="download")
    speeds_list.column("download", width=60)
    speeds_list.heading("upload", text="upload")
    speeds_list.column("upload", width=60)
    speeds_list.heading("ping", text="ping")
    speeds_list.column("ping", width=40)
    speeds_list.grid(row=3, column=0, rowspan=2, padx=10, pady=10)

    # create the started chart var
    start_chart = ImageTk.PhotoImage(Image.open("./images/speedtest_clear_chart.png"))

    # # resize the image
    # img1 = img.subsample(2, 2)

    chart_label = ttk.Label(win, image=start_chart)
    # keep reference to the chart, so it doesn't get prematurely garbage collected at the end of the function
    chart_label.image = start_chart
    chart_label.grid(row=1, column=1, rowspan=3, columnspan=2, padx=10, pady=10)

    start_test_button = ttk.Button(win, text="Start",
                                   command=lambda: start_speedtests_loop(speeds_list, chart_label, download_var,
                                                                         upload_var, ping_var))
    start_test_button.grid(row=4, column=1, padx=10, pady=(0, 10), sticky="news")
    stop_test_button = ttk.Button(win, text="Stop", command=stop_speedtests_loop)
    stop_test_button.grid(row=4, column=2, padx=10, pady=(0, 10), sticky="news")

    win.mainloop()


if __name__ == "__main__":
    main()
