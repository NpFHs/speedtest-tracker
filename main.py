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
# time between speedtests
SLEEP_TIME = 60

servers = []
# If you want to test against a specific server
# servers = [1234]

threads = None
results_dicts_list = []
is_speedtest_run = True


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


def new_speedtest(speeds_list, chart_label):
    global results_dicts_list

    s = speedtest.Speedtest()
    s.get_servers(servers)
    try:
        s.get_best_server()
        s.download(threads=threads)
        s.upload(threads=threads)
        s.results.share()

        results_dict = s.results.dict()
    except speedtest.SpeedtestBestServerFailure:
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

    update_table(speeds_list)
    show_chart(chart_label)


def test_to_vars(speeds_list, chart_label):
    t = Thread(target=lambda: new_speedtest(speeds_list, chart_label))
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


def speedtests_loop(speeds_list, chart_label):
    print("speedtest started")
    while is_speedtest_run:
        test_to_vars(speeds_list, chart_label)
        time.sleep(SLEEP_TIME)
    print("speedtest really stopped")


def stop_speedtests_loop():
    global is_speedtest_run
    print("speedtest stopped")
    is_speedtest_run = False


def main():
    clear_csv_file()

    win = tk.Tk()

    # add azure theme
    win.tk.call("source", "azure.tcl")
    win.tk.call("set_theme", "dark")

    win.title("Speedtest Tracking")
    download_var = tk.StringVar(value="Download: ")
    upload_var = tk.StringVar(value="Upload: ")
    ping_var = tk.StringVar(value="Ping: ")

    results_vars_label = tk.Label(text="Download: \nUpload: \nPing: ")
    results_vars_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10)

    columns = ("download", "upload", "ping")
    speeds_list = ttk.Treeview(win, columns=columns)
    speeds_list["show"] = "headings"  # to avoid empty column in the beginning
    speeds_list.heading("download", text="download")
    speeds_list.column("download", width=60)
    speeds_list.heading("upload", text="upload")
    speeds_list.column("upload", width=60)
    speeds_list.heading("ping", text="ping")
    speeds_list.column("ping", width=40)
    speeds_list.grid(row=2, column=0, rowspan=2, padx=10, pady=10)

    # create the started chart var
    start_chart = ImageTk.PhotoImage(Image.open("./images/speedtest_clear_chart.png"))

    # # resize the image
    # img1 = img.subsample(2, 2)

    chart_label = ttk.Label(win, image=start_chart)
    # keep reference to the chart, so it doesn't get prematurely garbage collected at the end of the function
    chart_label.image = start_chart
    chart_label.grid(row=0, column=1, rowspan=3, columnspan=2, padx=10, pady=10)

    stop_test_button = ttk.Button(win, text="Stop tests", command=stop_speedtests_loop)
    stop_test_button.grid(row=3, column=1, padx=10, pady=(0, 10), sticky="news")
    show_chart_button = ttk.Button(win, text="Show chart", command=lambda: show_chart(chart_label))
    show_chart_button.grid(row=3, column=2, padx=10, pady=(0, 10), sticky="news")

    speedtests = Thread(target=lambda: speedtests_loop(speeds_list, chart_label))
    speedtests.start()

    win.mainloop()


if __name__ == "__main__":
    main()
