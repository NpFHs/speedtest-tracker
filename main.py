import time
import psutil
import speedtest
import tkinter as tk
from threading import *
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image, ImageTk
import warnings

# to avoid UserWarning (Starting a Matplotlib GUI outside the main thread will likely fail).
warnings.simplefilter("ignore", UserWarning)
# default time between speedtests (in seconds - 1 minute * number of minutes)
SLEEP_TIME = 60 * 10

servers = []

threads = None
results_dicts_list = []
is_speedtest_run = False


# If you want to use a single threaded test
# threads = 1

class TkGui(tk.Tk):
    def __init__(self):
        super().__init__()

        # create the variables
        self.download_var = tk.StringVar(value="Download: ")
        self.upload_var = tk.StringVar(value="Upload: ")
        self.ping_var = tk.StringVar(value="Ping: ")
        self.sleep_time_var = tk.IntVar(value=10)
        self.time_type_var = tk.IntVar(value=2)
        self.sys_download_var = tk.StringVar(value="Download: ")
        self.sys_upload_var = tk.StringVar(value="Upload: ")

        self.results_frame = ttk.LabelFrame(self, text="Current results", padding=(20, 10))
        self.results_frame.grid(row=0, column=0, rowspan=3, sticky="news", padx=10, pady=10)

        # insert items in the results frame
        self.current_download_label = ttk.Label(self.results_frame, textvariable=self.download_var)
        self.current_download_label.grid(row=0, padx=10, pady=5)
        self.current_upload_label = ttk.Label(self.results_frame, textvariable=self.upload_var)
        self.current_upload_label.grid(row=1, padx=10, pady=5)
        self.current_ping_label = ttk.Label(self.results_frame, textvariable=self.ping_var)
        self.current_ping_label.grid(row=2, padx=10, pady=5)

        self.separator = ttk.Separator(self.results_frame)
        self.separator.grid(row=3, pady=10, sticky="ew")

        self.system_download_label = ttk.Label(self.results_frame, textvariable=self.sys_download_var)
        self.system_download_label.grid(row=4, padx=10, pady=5)

        self.system_upload_label = ttk.Label(self.results_frame, textvariable=self.sys_upload_var)
        self.system_upload_label.grid(row=5, padx=10, pady=5)

        # settings frame
        self.settings_frame = ttk.LabelFrame(self, text="settings", padding=(20, 10))
        self.settings_frame.grid(row=0, column=1, columnspan=2, sticky="news", padx=10, pady=(10, 0))

        self.settings_label = ttk.Label(self.settings_frame, text="Run speedtest once in:")
        self.settings_label.grid(row=0, column=0)

        self.time_spinbox = ttk.Spinbox(self.settings_frame, from_=1, to=60, increment=1,
                                        textvariable=self.sleep_time_var, width=5)
        self.time_spinbox.grid(row=0, column=1, padx=10, pady=10, sticky="news")

        self.seconds_radio = ttk.Radiobutton(self.settings_frame, text="seconds", variable=self.time_type_var, value=1)
        self.seconds_radio.grid(row=0, column=2, padx=10, pady=10, sticky="news")
        self.minutes_radio = ttk.Radiobutton(self.settings_frame, text="minutes", variable=self.time_type_var, value=2)
        self.minutes_radio.grid(row=0, column=3, padx=10, pady=10, sticky="news")
        self.hours_radio = ttk.Radiobutton(self.settings_frame, text="hours", variable=self.time_type_var, value=3)
        self.hours_radio.grid(row=0, column=4, padx=10, pady=10, sticky="news")

        self.set_button = ttk.Button(self.settings_frame, text="Set",
                                     command=lambda: set_sleep_time(self.sleep_time_var, self.time_type_var))
        self.set_button.grid(row=0, column=5, padx=10, pady=10)

        self.columns = ("download", "upload", "ping")
        self.speeds_list = ttk.Treeview(self, columns=self.columns)
        self.speeds_list["show"] = "headings"  # to avoid empty column in the beginning
        self.speeds_list.heading("download", text="download")
        self.speeds_list.column("download", width=60)
        self.speeds_list.heading("upload", text="upload")
        self.speeds_list.column("upload", width=60)
        self.speeds_list.heading("ping", text="ping")
        self.speeds_list.column("ping", width=40)
        self.speeds_list.grid(row=3, column=0, rowspan=2, padx=10, pady=10)

        # create the started chart var
        self.start_chart = ImageTk.PhotoImage(Image.open("./images/speedtest_clear_chart.png"))

        self.chart_label = ttk.Label(self, image=self.start_chart)
        # keep reference to the chart, so it doesn't get prematurely garbage collected at the end of the function
        self.chart_label.image = self.start_chart
        self.chart_label.grid(row=1, column=1, rowspan=3, columnspan=2, padx=10, pady=10)

        self.start_test_button = ttk.Button(self, text="Start",
                                            command=lambda: start_speedtests_loop(self.speeds_list, self.chart_label,
                                                                                  self))
        self.start_test_button.grid(row=4, column=1, padx=10, pady=(0, 10), sticky="news")
        self.stop_test_button = ttk.Button(self, text="Stop", command=stop_speedtests_loop)
        self.stop_test_button.grid(row=4, column=2, padx=10, pady=(0, 10), sticky="news")

    def set_download_var(self, new_value):
        self.download_var.set(new_value)

    def set_upload_var(self, new_value):
        self.upload_var.set(new_value)

    def set_ping_var(self, new_value):
        self.ping_var.set(new_value)

    def set_sys_download_var(self, new_value):
        self.sys_download_var.set(new_value)

    def set_sys_upload_var(self, new_value):
        self.sys_upload_var.set(new_value)


def get_system_net_usage():
    inf = "wlo1"  # change the inf variable according to the interface
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]  # NOQA
    net_in_1 = net_stat.bytes_recv
    net_out_1 = net_stat.bytes_sent
    time.sleep(1)
    net_stat = psutil.net_io_counters(pernic=True, nowrap=True)[inf]  # NOQA
    net_in_2 = net_stat.bytes_recv
    net_out_2 = net_stat.bytes_sent

    net_in = round((net_in_2 - net_in_1) / 1000000 * 8, 2)
    net_out = round((net_out_2 - net_out_1) / 1000000 * 8, 2)
    return net_in, net_out


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
        plt.savefig("./images/speedtest_chart.png")
        plt.close()
        # update the chart
        chart = ImageTk.PhotoImage(Image.open("./images/speedtest_chart.png"))
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


def new_speedtest(speeds_list, chart_label, win):
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

    results_dicts_list.append(results_dict)

    download_usage, upload_usage = get_system_net_usage()
    win.set_sys_download_var(f"download: {download_usage} Mb/s")
    win.set_sys_upload_var(f"upload: {upload_usage} Mb/s")
    update_vars(win)
    update_table(speeds_list)
    show_chart(chart_label)


def test_to_vars_in_new_thread(speeds_list, chart_label, win):
    new_speedtest(speeds_list, chart_label, win)


def update_vars(win):
    result = results_dicts_list[-1]

    # print the result on the screen
    mb_download = round(result["download"] / 1000000, 2)
    mb_upload = round(result["upload"] / 1000000, 2)
    ping_res = result['ping']

    win.set_download_var(f"download: {mb_download} Mb/s")
    win.set_upload_var(f"upload: {mb_upload} Mb/s")
    win.set_ping_var(f"ping: {ping_res} ms")


def speedtests_loop(speeds_list, chart_label, win):
    print("speedtest started")
    while is_speedtest_run:
        new_speedtest(speeds_list, chart_label, win)
        time.sleep(SLEEP_TIME)
    print("speedtest really stopped")


def start_speedtests_loop(speeds_list, chart_label, win):
    global is_speedtest_run

    is_speedtest_run = True
    speedtests = Thread(target=lambda: speedtests_loop(speeds_list, chart_label, win))
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
    # clear the CSV file if exist
    clear_csv_file()

    # create the window
    win = TkGui()
    win.title("Speedtest Tracking")
    win.resizable(width=False, height=False)

    # add azure theme
    win.tk.call("source", "azure.tcl")
    win.tk.call("set_theme", "dark")

    win.mainloop()


if __name__ == "__main__":
    main()
