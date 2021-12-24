import sys
import tkinter
import tkinter.ttk
from tkinter import scrolledtext
import warnings

from pynput.keyboard import Listener

import keyboard_helper

sys.path.append(r'./forza_motorsport')

import helper
from forza import *
from logger import Logger, TextHandler

# suppress matplotlib warning while running in thread
warnings.filterwarnings("ignore", category=UserWarning)

class MainWindow:
    def __init__(self):
        """init
        """
        self.root = tkinter.Tk()
        # Configure the rows that are in use to have weight #
        self.root.grid_rowconfigure(0, minsize=500, weight=500)
        self.root.grid_rowconfigure(1, minsize=300, weight=300)

        # Configure the cols that are in use to have weight #
        self.root.grid_columnconfigure(0, minsize=150, weight=150)
        self.root.grid_columnconfigure(1, minsize=650, weight=650)
        self.root.grid_columnconfigure(2, minsize=200, weight=100)

        self.root.title("Forza Horizon 5: Auto GFear Shifting")
        self.root.geometry("1300x800")
        self.root.minsize(1200, 800)
        self.root.maxsize(1800, 800)
        self.root["background"] = "LightSlateGray"

        self.speed_tree = {}
        self.rpm_tree = {}

        # set log frame
        self.set_log_frame()

        # forza info
        self.threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
        self.forza5 = Forza(self.threadPool, self.logger, constants.packet_format, clutch=constants.enable_clutch)
        self.listener = Listener(on_press=self.on_press)

        self.set_car_info_frame()
        self.set_car_perf_frame()
        self.set_shift_point_frame()
        self.set_button_frame()
        self.set_program_info_frame()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.logger.info('Forza Horizon 5: Auto Gear Shifting Started!!!')
        self.listener.start()
        self.root.mainloop()

    def update_tree(self):
        """Update shift point tree
        """
        for key, value in self.forza5.shift_point.items():
            self.treeview.item(self.speed_tree[key], values=round(value['speed'], 3))
            self.treeview.item(self.rpm_tree[key], values=round(value['rpmo'], 3))

    def on_press(self, key):
        """on press callback

        Args:
            key: key
        """
        pressed = keyboard_helper.get_key_name(key)
        if pressed == constants.collect_data:
            self.collect_data_handler(None)
        elif pressed == constants.analysis:
            self.analysis_handler(None, performance_profile=False, is_guid=False)
        elif pressed == constants.auto_shift:
            self.run_handler(None)
        elif pressed == constants.stop:
            self.pause_handler(None)
        elif pressed == constants.close:
            self.exit_handler(None)

    def close(self):
        """close program
        """
        shutdown(self.forza5, self.threadPool, self.listener)
        self.root.destroy()

    def set_car_info_frame(self):
        """set car info frame
        """
        self.car_info_frame = tkinter.Frame(self.root, borderwidth=3, bg='LightSlateGray', relief="groove",
                                            highlightthickness=True)
        enable_clutch = tkinter.IntVar(value=1)

        def set_clutch():
            self.forza5.clutch = enable_clutch.get()

        clutch_check = tkinter.Checkbutton(self.car_info_frame, text='Clutch', onvalue=1, offvalue=0,
                                           variable=enable_clutch, bg="LightSlateGray", command=set_clutch)
        clutch_check.place(rely=0.03, anchor="w")
        self.car_info_frame.grid(row=0, column=0, sticky='news')

    def set_car_perf_frame(self):
        """set car perf frame
        """
        self.car_perf_frame = tkinter.Frame(self.root, borderwidth=3, bg='LightSlateGray', relief="groove",
                                            highlightthickness=True)
        tkinter.Label(self.car_perf_frame, text='new features coming soon', bg="LightSlateGray", borderwidth=2,
                      relief="groove", anchor="nw").pack(fill="both", expand=True)
        self.car_perf_frame.grid(row=0, column=1, sticky='news')

    def set_shift_point_frame(self):
        """set shift point frame
        """
        self.shift_point = tkinter.Frame(self.root, borderwidth=3, bg='LightSlateGray', relief="groove",
                                         highlightthickness=True)
        self.treeview = tkinter.ttk.Treeview(self.shift_point, columns="value")
        self.treeview.heading('#0', text='Shift Point', anchor=tkinter.CENTER)
        self.treeview.heading('value', text='Value', anchor=tkinter.CENTER)
        self.treeview.column('#0', width=80, anchor=tkinter.CENTER)
        self.treeview.column('value', width=120, anchor=tkinter.CENTER)
        self.speed_level = self.treeview.insert(parent='', index=tkinter.END, text='Speed (km/h)', open=True)
        self.rpm_level = self.treeview.insert(parent='', index=tkinter.END, text='RPM (r/m)', open=True)

        for i in range(1, 11):
            self.speed_tree[i] = self.treeview.insert(self.speed_level, tkinter.END, text=i, values=-1)
            self.rpm_tree[i] = self.treeview.insert(self.rpm_level, tkinter.END, text=i, values=-1)

        self.treeview.pack(fill="both", expand=True)
        self.shift_point.grid(row=0, column=2, sticky='news')

    def set_button_frame(self):
        """set buttom frame
        """
        self.button_frame = tkinter.Frame(self.root, borderwidth=3, bg='LightSlateGray', relief="groove",
                                          highlightthickness=True)

        button_names = [('Collect Data', self.collect_data_handler, constants.collect_data),
                        ('Analysis', self.analysis_handler, constants.analysis),
                        ('Run Auto Shift', self.run_handler, constants.auto_shift),
                        ('Pause', self.pause_handler, constants.stop),
                        ('Exit', self.exit_handler, constants.close)]

        for i, (name, func, shortcut) in enumerate(button_names):
            button = tkinter.Button(self.button_frame, text=f'{name} ({shortcut.capitalize()})')
            button.bind('<Button-1>', func)
            button.place(relx=0.5, rely=1 / len(button_names) * i + 1 / len(button_names) / 2, relwidth=0.8,
                         relheight=1 / len(button_names) * 0.9, anchor='center')

        self.button_frame.grid(row=1, column=0, sticky='news')

    def set_log_frame(self):
        """set log frame
        """
        self.log_frame = tkinter.Frame(self.root, borderwidth=3, bg='LightSlateGray', relief="groove",
                                       highlightthickness=True)
        log = tkinter.scrolledtext.ScrolledText(self.log_frame, bg="LightSlateGray", borderwidth=2,
                                                font='Monaco 9 bold')
        log.pack(fill="both", expand=True)
        log_handler = TextHandler(log)
        self.logger = (Logger(log_handler))('ForzaHorizon5')

        button = tkinter.Button(self.log_frame, text='Clear')
        button.bind('<Button-1>', lambda x: log.delete(1.0, 'end'))
        button.place(relx=0.93, rely=0.053, relwidth=0.05, relheight=0.05, anchor='center', bordermode='inside')

        self.log_frame.grid(row=1, column=1, sticky='news')

    def set_program_info_frame(self):
        """set code info frame
        """
        self.program_info_frame = tkinter.Frame(self.root, borderwidth=3, bg='LightSlateGray', relief="groove",
                                       highlightthickness=True)
        label = tkinter.Label(self.program_info_frame, text='If you found any issues, or want to contribute to the '
                                                            'program, feel free to visit github: '
                                                            'https://github.com/Juice-XIJ/forza_auto_gear',
                              bg="LightSlateGray", borderwidth=2,
                      relief="groove", anchor="nw", justify=tkinter.LEFT)
        label.bind('<Configure>', lambda e: label.config(wraplength=int(label.winfo_width() * 0.9)))
        label.pack(fill="both", expand=True)
        self.program_info_frame.grid(row=1, column=2, sticky='news')

    def collect_data_handler(self, event):
        """collect data button callback

        Args:
            event
        """
        if self.forza5.isRunning:
            self.logger.info('stopping gear test')

            def stopping():
                self.forza5.isRunning = False

            self.threadPool.submit(stopping)
        else:
            self.logger.info('starting gear test')

            def starting():
                self.forza5.isRunning = True
                self.forza5.test_gear()

            self.threadPool.submit(starting)

    def analysis_handler(self, event, performance_profile=True, is_guid=True):
        """analysis button callback

        Args:
            event
            performance_profile (bool, optional): draw performance of not. Defaults to True.
            is_guid (bool, optional): is guid or not. Defaults to True.
        """
        if len(self.forza5.records) <= 0:
            self.logger.info(f'load config {constants.example_car_ordinal}.json for analysis as an example')
            helper.load_config(self.forza5,
                               os.path.join(constants.root_path, 'example', f'{constants.example_car_ordinal}.json'))
        self.logger.info('Analysis')

        self.forza5.analyze(performance_profile=performance_profile, is_gui=is_guid)
        self.update_tree()

    def run_handler(self, event):
        """run button callback

        Args:
            event
        """
        if self.forza5.isRunning:
            self.forza5.logger.info('stopping auto gear')

            def stopping():
                self.forza5.isRunning = False

            self.threadPool.submit(stopping)
        else:
            self.forza5.logger.info('starting auto gear')

            def starting():
                self.forza5.isRunning = True
                self.forza5.run(self.update_tree)

            self.threadPool.submit(starting)

    def pause_handler(self, event):
        """pause button callback

        Args:
            event
        """
        shutdown(self.forza5, self.threadPool, self.listener)
        self.threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()
        self.forza5.logger.info('stopped')

    def exit_handler(self, event):
        """exit button callback

        Args:
            event
        """
        shutdown(self.forza5, self.threadPool, self.listener)
        self.forza5.logger.info('bye~')
        self.root.destroy()


def shutdown(forza: Forza, threadPool: ThreadPoolExecutor, listener: Listener):
    """shutdown/clean up resources

    Args:
        forza (Forza): forza
        threadPool (ThreadPoolExecutor): thread pool
        listener (Listener): keyboard listener
    """
    forza.isRunning = False
    threadPool.shutdown(wait=False)
    listener.stop()


def main():
    """main.....
    """
    MainWindow()


if __name__ == "__main__":
    main()
