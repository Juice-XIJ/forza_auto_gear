import os
import tkinter
import tkinter.ttk
import warnings
from concurrent.futures import ThreadPoolExecutor
from tkinter import scrolledtext

import matplotlib.colors as mcolors
from pynput.keyboard import Listener

import constants
import helper
import keyboard_helper
from forza import Forza
from logger import Logger, TextHandler

# suppress matplotlib warning while running in thread
warnings.filterwarnings("ignore", category=UserWarning)


class MainWindow:

    def __init__(self):
        """init
        """
        self.root = tkinter.Tk()

        # init text
        self.language = helper.get_sys_lang()

        self.init_text()
        self.text_update(self.language)

        # Configure the rows that are in use to have weight #
        self.root.grid_rowconfigure(0, minsize=500, weight=500)
        self.root.grid_rowconfigure(1, minsize=300, weight=300)

        # Configure the cols that are in use to have weight #
        self.root.grid_columnconfigure(0, minsize=150, weight=150)
        self.root.grid_columnconfigure(1, minsize=650, weight=650)
        self.root.grid_columnconfigure(2, minsize=200, weight=100)

        self.root.title("Forza Horizon 5: Auto Gear Shifting")
        self.root.geometry("1300x800")
        self.root.minsize(1200, 800)
        self.root.maxsize(1800, 1000)
        self.root["background"] = constants.background_color

        # widgets to be updated
        self.speed_tree = {}
        self.rpm_tree = {}

        self.tires = {}
        self.tire_color = mcolors.LinearSegmentedColormap.from_list("", [(0, "green"), (1, "red")])

        self.acceleration_var = tkinter.StringVar()
        self.acceleration_var.set("0%")
        self.brake_var = tkinter.StringVar()
        self.brake_var.set("0%")

        # set log frame
        self.set_log_frame()

        # forza info
        self.threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
        self.forza5 = Forza(self.threadPool, self.logger, constants.packet_format, enable_clutch=constants.enable_clutch)
        self.listener = Listener(on_press=self.on_press)

        self.set_car_setting_frame()
        self.set_car_perf_frame()
        self.set_shift_point_frame()
        self.set_button_frame()
        self.set_program_info_frame()
        self.root.protocol('WM_DELETE_WINDOW', self.close)
        self.logger.info('Forza Horizon 5: Auto Gear Shifting Started!!!')
        self.listener.start()
        self.root.mainloop()

    def init_text(self):
        self.select_language_txt = tkinter.StringVar()
        self.language_txt = tkinter.StringVar()
        self.clutch_shortcut_txt = tkinter.StringVar()
        self.upshift_shortcut_txt = tkinter.StringVar()
        self.downshift_shortcut_txt = tkinter.StringVar()
        self.clutch_txt = tkinter.StringVar()
        self.farm_txt = tkinter.StringVar()
        self.tire_information_txt = tkinter.StringVar()
        self.accel_txt = tkinter.StringVar()
        self.brake_txt = tkinter.StringVar()
        self.shift_point_txt = tkinter.StringVar()
        self.tree_value_txt = tkinter.StringVar()
        self.speed_txt = tkinter.StringVar()
        self.rpm_txt = tkinter.StringVar()
        self.collect_button_txt = tkinter.StringVar()
        self.analysis_button_txt = tkinter.StringVar()
        self.run_button_txt = tkinter.StringVar()
        self.pause_button_txt = tkinter.StringVar()
        self.exit_button_txt = tkinter.StringVar()
        self.clear_log_text = tkinter.StringVar()
        self.program_info_txt = tkinter.StringVar()

    def text_update(self, lang_index):
        self.select_language_txt.set(constants.select_language_txt[lang_index])
        self.language_txt.set(constants.language_txt[lang_index])
        self.clutch_shortcut_txt.set(constants.clutch_shortcut_txt[lang_index])
        self.upshift_shortcut_txt.set(constants.upshift_shortcut_txt[lang_index])
        self.downshift_shortcut_txt.set(constants.downshift_shortcut_txt[lang_index])
        self.clutch_txt.set(constants.clutch_txt[lang_index])
        self.farm_txt.set(constants.farm_txt[lang_index])
        self.tire_information_txt.set(constants.tire_information_txt[lang_index])
        self.accel_txt.set(constants.accel_txt[lang_index])
        self.brake_txt.set(constants.brake_txt[lang_index])
        self.shift_point_txt.set(constants.shift_point_txt[lang_index])
        self.tree_value_txt.set(constants.tree_value_txt[lang_index])
        self.speed_txt.set(f'{constants.speed_txt[lang_index]} km/h')
        self.rpm_txt.set(f'{constants.rpm_txt[lang_index]} r/m')
        self.collect_button_txt.set(f'{constants.collect_button_txt[lang_index]} ({constants.collect_data.name})')
        self.analysis_button_txt.set(f'{constants.analysis_button_txt[lang_index]} ({constants.analysis.name})')
        self.run_button_txt.set(f'{constants.run_button_txt[lang_index]} ({constants.auto_shift.name})')
        self.pause_button_txt.set(f'{constants.pause_button_txt[lang_index]} ({constants.stop.name})')
        self.exit_button_txt.set(f'{constants.exit_button_txt[lang_index]} ({constants.close.name})')
        self.clear_log_text.set(constants.clear_log_txt[lang_index])
        self.program_info_txt.set(constants.program_info_txt[lang_index])

        # widgets to be set
        if hasattr(self, 'tire_canvas'):
            self.tire_canvas.itemconfigure(self.tire_canvas_text, text=self.tire_information_txt.get())

        if hasattr(self, 'treeview'):
            self.treeview.heading('#0', text=self.shift_point_txt.get(), anchor=tkinter.CENTER)
            self.treeview.heading('value', text=self.tree_value_txt.get(), anchor=tkinter.CENTER)
            self.treeview.item(self.speed_level, text=self.speed_txt.get())
            self.treeview.item(self.rpm_level, text=self.rpm_txt.get())

        if hasattr(self, 'program_info'):
            self.program_info.configure(state=tkinter.NORMAL)
            self.program_info.delete("1.0", tkinter.END)
            self.program_info.insert('1.0', self.program_info_txt.get())
            self.program_info.configure(state=tkinter.DISABLED)

    def update_tree(self):
        """Update shift point tree
        """
        for key, value in self.forza5.shift_point.items():
            self.treeview.item(self.speed_tree[key], values=round(value['speed'], 3))
            self.treeview.item(self.rpm_tree[key], values=round(value['rpmo'], 3))

    def update_car_info(self, fdp):
        """update car info

        Args:
            fdp: fdp
        """
        if self.forza5.isRunning:
            self.acceleration_var.set(f"{str(round(fdp.accel / 255 * 100, 1))}%")
            self.brake_var.set(f"{str(round(fdp.brake / 255 * 100, 1))}%")

            # FL tire
            slip = abs(fdp.tire_combined_slip_FL) if abs(fdp.tire_combined_slip_FL) < 1 else 1
            color = self.tire_color(slip / 0.8 * 0.5 if slip < 0.8 else (1 - slip) / 0.2 * 0.5 + 0.8)
            self.tire_canvas.itemconfig(self.tires["FL"], fill=helper.rgb(color[0], color[1], color[2]))

            # FR tire
            slip = abs(fdp.tire_combined_slip_FR) if abs(fdp.tire_combined_slip_FR) < 1 else 1
            color = self.tire_color(slip / 0.8 * 0.5 if slip < 0.8 else (1 - slip) / 0.2 * 0.5 + 0.8)
            self.tire_canvas.itemconfig(self.tires["FR"], fill=helper.rgb(color[0], color[1], color[2]))

            # RL tire
            slip = abs(fdp.tire_combined_slip_RL) if abs(fdp.tire_combined_slip_RL) < 1 else 1
            color = self.tire_color(slip / 0.8 * 0.5 if slip < 0.8 else (1 - slip) / 0.2 * 0.5 + 0.8)
            self.tire_canvas.itemconfig(self.tires["RL"], fill=helper.rgb(color[0], color[1], color[2]))

            # RR tire
            slip = abs(fdp.tire_combined_slip_RR) if abs(fdp.tire_combined_slip_RR) < 1 else 1
            color = self.tire_color(slip / 0.8 * 0.5 if slip < 0.8 else (1 - slip) / 0.2 * 0.5 + 0.8)
            self.tire_canvas.itemconfig(self.tires["RR"], fill=helper.rgb(color[0], color[1], color[2]))

    def reset_car_info(self):
        """reset car info and tree view
        """
        # reset tree
        for key, _ in self.speed_tree.items():
            self.treeview.item(self.speed_tree[key], values="-")
            self.treeview.item(self.rpm_tree[key], values="-")

        # reset accel and brake
        self.acceleration_var.set("0%")
        self.brake_var.set("0%")

        # FL tire
        self.tire_canvas.itemconfig(self.tires["FL"], fill=constants.background_color)

        # FR tire
        self.tire_canvas.itemconfig(self.tires["FR"], fill=constants.background_color)

        # RL tire
        self.tire_canvas.itemconfig(self.tires["RL"], fill=constants.background_color)

        # RR tire
        self.tire_canvas.itemconfig(self.tires["RR"], fill=constants.background_color)

    def on_press(self, key):
        """on press callback

        Args:
            key: key
        """
        try:
            if key == constants.collect_data:
                self.collect_data_handler(None)
            elif key == constants.analysis:
                self.analysis_handler(None, performance_profile=False, is_guid=False)
            elif key == constants.auto_shift:
                self.run_handler(None)
            elif key == constants.stop:
                self.pause_handler(None)
            elif key == constants.close:
                self.exit_handler(None)
        except BaseException as e:
            self.forza5.logger.exception(e)

    def close(self):
        """close program
        """
        shutdown(self.forza5, self.threadPool, self.listener)
        self.root.destroy()

    def place_languages(self, pre_widget_count=0):
        # ==== language setting ====
        # language label
        language_label = tkinter.Label(self.car_info_frame, textvariable=self.select_language_txt, bg=constants.background_color, fg=constants.text_color)
        language_label.place(relx=0.06, rely=self.get_rely(pre_widget_count), anchor="w")
        pre_widget_count = pre_widget_count + 1

        # language options
        language_combobox = tkinter.ttk.Combobox(self.car_info_frame, values=constants.language_txt, state='readonly')
        language_combobox.current(self.language)

        def set_language(event):
            self.language = constants.language_txt.index(event.widget.get())
            self.text_update(self.language)

        language_combobox.bind("<<ComboboxSelected>>", set_language)
        language_combobox.place(relx=0.08, rely=self.get_rely(pre_widget_count), anchor="w")
        return pre_widget_count + 1

    def place_ip_port(self, pre_widget_count=0):
        self.ip_widget = tkinter.Text(self.car_info_frame, borderwidth=0, bg=constants.background_color, fg=constants.text_color, wrap=tkinter.WORD)
        self.ip_widget.insert("1.0", f'IP: {self.forza5.ip}')
        self.ip_widget.place(relx=0.08, rely=self.get_rely(pre_widget_count), relwidth=0.85, relheight=0.03, anchor="w")
        self.ip_widget.configure(state="disabled")
        pre_widget_count = pre_widget_count + 1

        self.port_widget = tkinter.Text(self.car_info_frame, borderwidth=0, bg=constants.background_color, fg=constants.text_color, wrap=tkinter.WORD)
        self.port_widget.insert("1.0", f'Port: {self.forza5.port}')
        self.port_widget.place(relx=0.08, rely=self.get_rely(pre_widget_count), relwidth=0.85, relheight=0.03, anchor="w")
        self.port_widget.configure(state="disabled")
        pre_widget_count = pre_widget_count + 1

        return pre_widget_count

    def place_shortcuts(self, pre_widget_count=0):
        """place shortcuts comboboxes
        """

        def get_available_shortcuts(cur_shortcut):
            all_boundKeys = self.forza5.boundKeys()
            all_boundKeys.extend(constants.boundKeys)
            return [x for x in keyboard_helper.key_list if x not in all_boundKeys or x == cur_shortcut]

        shortcut_list = []
        # ==== short-cut options ====
        # == define clutch shortcuts ==
        # clutch shortcut label
        clutch_shortcut_label = tkinter.Label(self.car_info_frame, textvariable=self.clutch_shortcut_txt, bg=constants.background_color, fg=constants.text_color)
        shortcut_list.append(tuple((clutch_shortcut_label, "")))

        # clutch options
        clutch_shortcuts = get_available_shortcuts(self.forza5.clutch)
        clutch_shortcut = tkinter.ttk.Combobox(self.car_info_frame, values=clutch_shortcuts, state='readonly')
        clutch_shortcut.current(clutch_shortcuts.index(self.forza5.clutch))
        shortcut_list.append(tuple((clutch_shortcut, "clutch")))

        # == upshift shortcut ==
        # upshift short label
        upshift_shortcut_label = tkinter.Label(self.car_info_frame, textvariable=self.upshift_shortcut_txt, bg=constants.background_color, fg=constants.text_color)
        shortcut_list.append(tuple((upshift_shortcut_label, "")))

        # upshift options
        upshift_shortcuts = get_available_shortcuts(self.forza5.upshift)
        upshift_shortcut = tkinter.ttk.Combobox(self.car_info_frame, values=upshift_shortcuts, state='readonly')
        upshift_shortcut.current(upshift_shortcuts.index(self.forza5.upshift))
        shortcut_list.append(tuple((upshift_shortcut, "upshift")))

        # == downshift shortcut ==
        # downshift short label
        downshift_shortcut_label = tkinter.Label(self.car_info_frame, textvariable=self.downshift_shortcut_txt, bg=constants.background_color, fg=constants.text_color)
        shortcut_list.append(tuple((downshift_shortcut_label, "")))

        # downshift options
        downshift_shortcuts = get_available_shortcuts(self.forza5.downshift)
        downshift_shortcut = tkinter.ttk.Combobox(self.car_info_frame, values=downshift_shortcuts, state='readonly')
        downshift_shortcut.current(downshift_shortcuts.index(self.forza5.downshift))
        shortcut_list.append(tuple((downshift_shortcut, "downshift")))

        all_combobox = [box[0] for box in shortcut_list if type(box[0]) is tkinter.ttk.Combobox]
        for i in range(len(shortcut_list)):
            if type(shortcut_list[i][0]) is tkinter.Label:
                shortcut_list[i][0].place(relx=0.06, rely=self.get_rely(i + pre_widget_count), anchor="w")
            elif type(shortcut_list[i][0]) is tkinter.ttk.Combobox:

                def set_clutch_shortcut(event):
                    box = [x for x in shortcut_list if x[0] == event.widget][0]
                    if box[1] == "clutch":
                        self.forza5.clutch = event.widget.get()
                        self.logger.info(f"clutch shortcut is: {self.forza5.clutch}")
                    elif box[1] == "upshift":
                        self.forza5.upshift = event.widget.get()
                        self.logger.info(f"upshift shortcut is: {self.forza5.upshift}")
                    elif box[1] == "downshift":
                        self.forza5.downshift = event.widget.get()
                        self.logger.info(f"downshift shortcut is: {self.forza5.downshift}")

                    for box in all_combobox:
                        box['values'] = get_available_shortcuts(box.get())

                shortcut_list[i][0].bind("<<ComboboxSelected>>", set_clutch_shortcut)
                shortcut_list[i][0].place(relx=0.08, rely=self.get_rely(i + pre_widget_count), anchor="w")

        return len(shortcut_list) + pre_widget_count

    def get_rely(self, count):
        """get relative y

        Args:
            count (int): previous widgets count

        Returns:
            float: relative y
        """
        return 0.03 + 0.05 * count

    def set_car_setting_frame(self):
        """set car setting frame
        """
        # place car setting frame
        self.car_info_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)
        total_widget = 0

        # ==== IP/Port setting ====
        total_widget = self.place_ip_port(total_widget)

        # ==== language setting ====
        total_widget = self.place_languages(total_widget)

        # ==== place shortcuts ====
        total_widget = self.place_shortcuts(total_widget)

        # ==== features settings ====
        # clutch setting
        enable_clutch = tkinter.IntVar(value=self.forza5.enable_clutch)

        def set_clutch():
            self.forza5.enable_clutch = enable_clutch.get()

        clutch_check = tkinter.Checkbutton(self.car_info_frame, textvariable=self.clutch_txt, onvalue=1, offvalue=0, variable=enable_clutch, bg=constants.background_color, command=set_clutch, fg=constants.text_color)
        clutch_check.place(relx=0.05, rely=self.get_rely(total_widget), anchor="w")
        total_widget = total_widget + 1

        # farming setting
        enable_farm = tkinter.IntVar(value=self.forza5.farming)

        def set_farm():
            self.forza5.farming = enable_farm.get()

        farm_check = tkinter.Checkbutton(self.car_info_frame, textvariable=self.farm_txt, onvalue=1, offvalue=0, variable=enable_farm, bg=constants.background_color, command=set_farm, fg=constants.text_color)
        farm_check.place(relx=0.05, rely=self.get_rely(total_widget), anchor="w")
        total_widget = total_widget + 1
        self.car_info_frame.grid(row=0, column=0, sticky='news')

    def set_car_perf_frame(self):
        """set car perf frame
        """
        # Place car perf frame
        self.car_perf_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)
        self.car_perf_frame.grid(row=0, column=1, sticky='news')
        self.car_perf_frame.update()

        # place tire information canvas
        self.tire_canvas = tkinter.Canvas(self.car_perf_frame, background=constants.background_color, bd=0, highlightthickness=False)
        self.tire_canvas.place(relx=constants.tire_canvas_relx, rely=constants.tire_canvas_rely, relwidth=constants.tire_canvas_relwidth, relheight=constants.tire_canvas_relheight, anchor=tkinter.CENTER)
        self.tire_canvas_text = self.tire_canvas.create_text(self.car_perf_frame.winfo_width() * constants.tire_canvas_relwidth / 2,
                                                             self.car_perf_frame.winfo_height() * constants.y_padding_top * 0.5,
                                                             text=self.tire_information_txt.get(),
                                                             fill=constants.text_color,
                                                             font=('Helvetica 15 bold'),
                                                             anchor=tkinter.CENTER)
        for pos, info in constants.tires.items():
            self.tires[pos] = self.round_rectangle(self.tire_canvas,
                                                   self.car_perf_frame.winfo_width() * info[0],
                                                   self.car_perf_frame.winfo_height() * info[1],
                                                   self.car_perf_frame.winfo_width() * info[2],
                                                   self.car_perf_frame.winfo_height() * info[3],
                                                   radius=info[4],
                                                   fill=constants.background_color,
                                                   width=2,
                                                   outline=constants.text_color)

        # place acceleration information text
        tkinter.Label(self.car_perf_frame, textvariable=self.accel_txt, bg=constants.background_color, fg=constants.text_color, font=('Helvetica 15 bold')).place(relx=0.15, rely=0.185, anchor=tkinter.CENTER)
        tkinter.Label(self.car_perf_frame, textvariable=self.acceleration_var, bg=constants.background_color, fg=constants.text_color, font=('Helvetica 35 bold italic')).place(relx=0.15, rely=0.35, anchor=tkinter.CENTER)

        # place brake information test
        tkinter.Label(self.car_perf_frame, textvariable=self.brake_txt, bg=constants.background_color, fg=constants.text_color, font=('Helvetica 15 bold')).place(relx=0.15, rely=0.525, anchor=tkinter.CENTER)
        tkinter.Label(self.car_perf_frame, textvariable=self.brake_var, bg=constants.background_color, fg=constants.text_color, font=('Helvetica 35 bold italic')).place(relx=0.15, rely=0.7, anchor=tkinter.CENTER)

    def set_shift_point_frame(self):
        """set shift point frame
        """
        # place shift point frame
        self.shift_point_frame = tkinter.Frame(self.root, border=0, relief="groove", background=constants.background_color, highlightthickness=True, highlightcolor=constants.text_color)

        style = tkinter.ttk.Style()
        style.theme_use("clam")

        # set background and foreground of the treeview
        style.configure("Treeview", background=constants.background_color, foreground=constants.text_color, fieldbackground=constants.background_color)
        style.map('Treeview', background=[('selected', '#BFBFBF')], foreground=[('selected', 'black')], fieldbackground=[('selected', 'black')])

        self.treeview = tkinter.ttk.Treeview(self.shift_point_frame, columns="value", style='Treeview')
        self.treeview.heading('#0', text=self.shift_point_txt.get(), anchor=tkinter.CENTER)
        self.treeview.heading('value', text=self.tree_value_txt.get(), anchor=tkinter.CENTER)
        self.treeview.column('#0', width=80, anchor=tkinter.CENTER)
        self.treeview.column('value', width=120, anchor=tkinter.CENTER)
        self.speed_level = self.treeview.insert(parent='', index=tkinter.END, text=self.speed_txt.get(), open=True)
        self.rpm_level = self.treeview.insert(parent='', index=tkinter.END, text=self.rpm_txt.get(), open=True)

        for i in range(1, 11):
            self.speed_tree[i] = self.treeview.insert(self.speed_level, tkinter.END, text=i, values="-")
            self.rpm_tree[i] = self.treeview.insert(self.rpm_level, tkinter.END, text=i, values="-")

        self.treeview.pack(fill="both", expand=True)
        self.shift_point_frame.grid(row=0, column=2, sticky='news')

    def set_button_frame(self):
        """set buttom frame
        """
        # place button frame
        self.button_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)

        button_names = [(self.collect_button_txt, self.collect_data_handler), (self.analysis_button_txt, self.analysis_handler), (self.run_button_txt, self.run_handler), (self.pause_button_txt, self.pause_handler),
                        (self.exit_button_txt, self.exit_handler)]

        for i, (name, func) in enumerate(button_names):
            button = tkinter.Button(self.button_frame, textvariable=name, bg=constants.background_color, fg=constants.text_color, borderwidth=3, highlightcolor=constants.text_color, highlightthickness=True)
            button.bind('<Button-1>', func)
            button.place(relx=0.5, rely=1 / len(button_names) * i + 1 / len(button_names) / 2, relwidth=0.8, relheight=1 / len(button_names) * 0.9, anchor='center')

        self.button_frame.grid(row=1, column=0, sticky='news')

    def set_log_frame(self):
        """set log frame
        """
        # place log frame
        self.log_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)

        log = scrolledtext.ScrolledText(self.log_frame, bg=constants.background_color, borderwidth=2, font='Monaco 9 bold', fg=constants.text_color)
        log.pack(fill="both", expand=True)
        log_handler = TextHandler(log)
        self.logger = (Logger(log_handler))('ForzaHorizon5')

        button = tkinter.Button(self.log_frame, textvariable=self.clear_log_text, bg=constants.background_color, fg=constants.text_color, borderwidth=3, highlightcolor=constants.text_color, highlightthickness=True)
        button.bind('<Button-1>', lambda x: log.delete(1.0, 'end'))
        button.place(relx=0.93, rely=0.053, relwidth=0.05, relheight=0.07, anchor='center', bordermode='inside')
        self.log_frame.grid(row=1, column=1, sticky='news')

    def set_program_info_frame(self):
        """set code info frame
        """
        # place code info frame
        self.program_info_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)

        self.program_info = tkinter.Text(self.program_info_frame, borderwidth=0, bg=constants.background_color, fg=constants.text_color, wrap=tkinter.WORD)
        self.program_info.insert("current", self.program_info_txt.get())
        self.program_info.place(relx=0.03, rely=0.03, relwidth=0.95, relheight=0.95, anchor='nw', bordermode='inside')
        self.program_info.configure(state="disabled")

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
                self.reset_car_info()

            self.threadPool.submit(stopping)
        else:
            self.logger.info('starting gear test')

            def starting():
                self.forza5.isRunning = True
                self.forza5.test_gear(self.update_car_info)

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
            helper.load_config(self.forza5, os.path.join(constants.root_path, 'example', f'{constants.example_car_ordinal}.json'))
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
                self.reset_car_info()

            self.threadPool.submit(stopping)
        else:
            self.forza5.logger.info('starting auto gear')

            def starting():
                self.forza5.isRunning = True
                self.forza5.run(self.update_tree, self.update_car_info)

            self.threadPool.submit(starting)

    def pause_handler(self, event):
        """pause button callback

        Args:
            event
        """
        shutdown(self.forza5, self.threadPool, self.listener)
        self.reset_car_info()
        self.threadPool = ThreadPoolExecutor(max_workers=8, thread_name_prefix="exec")
        self.forza5.threadPool = self.threadPool
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

    def round_rectangle(self, canvas: tkinter.Canvas, x1, y1, x2, y2, radius=25, **kwargs):
        """draw rectangle with round corner

        Args:
            canvas (tkinter.Canvas): canvas
            x1: top left x coordinate
            y1: top left y coordinate
            x2: bot right x coordinate
            y2: bot right y coordinate
            radius (int, optional): round radius. Defaults to 25.

        Returns:
            rectangle
        """
        points = [
            x1 + radius, y1, x1 + radius, y1, x2 - radius, y1, x2 - radius, y1, x2, y1, x2, y1 + radius, x2, y1 + radius, x2, y2 - radius, x2, y2 - radius, x2, y2, x2 - radius, y2, x2 - radius, y2, x1 + radius, y2, x1 + radius, y2, x1, y2, x1,
            y2 - radius, x1, y2 - radius, x1, y1 + radius, x1, y1 + radius, x1, y1
        ]

        return canvas.create_polygon(points, **kwargs, smooth=True)


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
