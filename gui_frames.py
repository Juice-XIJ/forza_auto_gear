"""Frame-builder mixin extracted from ``gui.py``.

Holds the ``set_*_frame`` methods and their helpers as a single mixin
class. ``MainWindow`` inherits this mixin to get the layout code without
having every layout method inline in ``gui.py``.

The mixin uses ``self`` extensively (`self.car_info_frame`, `self.forza5`,
`self.car_perf_frame`, ``self.text_update``-bound StringVars, etc.) — it
is *not* a standalone class; it is only meant to be combined with
``MainWindow``. We keep the names and bodies byte-identical to the
previous in-file methods so the baseline widget-tree snapshot remains
unchanged.
"""

from __future__ import annotations

import tkinter
import tkinter.ttk
from tkinter import scrolledtext

import constants
import keyboard_helper
import theme
from gui_widgets import round_rectangle
from logger import Logger, TextHandler


class FrameBuilderMixin:
    """All Tk widget construction lives here. Used as a mixin on MainWindow."""

    # --- helpers --------------------------------------------------------

    def get_rely(self, count: int) -> float:
        """Return the relative y for the ``count``th widget in the left column."""
        return 0.03 + 0.05 * count

    def place_languages(self, pre_widget_count: int = 0) -> int:
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

    def place_ip_port(self, pre_widget_count: int = 0) -> int:
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

    def place_shortcuts(self, pre_widget_count: int = 0) -> int:
        """Place shortcuts comboboxes."""

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

    # --- frame builders -------------------------------------------------

    def set_car_setting_frame(self) -> None:
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

        # off-road, rally setting
        enable_offroad_rally = tkinter.IntVar(value=0)

        def set_offroad_rally():
            self.forza5.shift_point_factor = constants.offroad_rally_shift_factor if enable_offroad_rally.get() == 1 else constants.shift_factor

        offroad_rally_check = tkinter.Checkbutton(self.car_info_frame, textvariable=self.offroad_rally_txt, onvalue=1, offvalue=0, variable=enable_offroad_rally, bg=constants.background_color, command=set_offroad_rally, fg=constants.text_color)
        offroad_rally_check.place(relx=0.05, rely=self.get_rely(total_widget), anchor="w")
        total_widget = total_widget + 1
        self.car_info_frame.grid(row=0, column=0, sticky='news')

    def set_car_perf_frame(self) -> None:
        """set car perf frame
        """
        # Place car perf frame
        self.car_perf_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)
        self.car_perf_frame.grid(row=0, column=1, sticky='news')
        self.car_perf_frame.update()

        # place car id
        tkinter.Label(
            self.car_perf_frame,
            textvariable=self.car_id,
            bg=constants.background_color,
            fg=constants.text_color,
            font=theme.h2()
        ).place(
            relx=constants.car_info_leftbound_relx,
            rely=constants.car_info_topbound_rely,
            anchor=tkinter.W
        )

        tkinter.Label(
            self.car_perf_frame,
            textvariable=self.car_id_var,
            bg=constants.background_color,
            fg=constants.text_color,
            font=theme.h1()
        ).place(
            relx=constants.car_info_leftbound_relx,
            rely=constants.car_info_topbound_rely + constants.car_info_line_gap,
            anchor=tkinter.W
        )

        # place car perf
        perf_y = constants.car_info_topbound_rely + 0.28
        tkinter.Label(
            self.car_perf_frame,
            textvariable=self.car_perf,
            bg=constants.background_color,
            fg=constants.text_color,
            font=theme.h2()
        ).place(
            relx=constants.car_info_leftbound_relx,
            rely=perf_y,
            anchor=tkinter.W
        )

        # place car perf sticker canvas
        perf_width = 0.12
        perf_height = 0.06
        self.perf_canvas = tkinter.Canvas(self.car_perf_frame, background=constants.car_class_color[self.forza5.car_class], bd=0, highlightthickness=False)
        self.perf_canvas.place(relx=constants.car_info_leftbound_relx + 0.01, rely=perf_y + constants.car_info_line_gap, relwidth=perf_width, relheight=perf_height, anchor=tkinter.W)
        self.car_class_text = self.perf_canvas.create_text(
            self.car_perf_frame.winfo_width() * perf_width * 0.225,
            self.car_perf_frame.winfo_height() * perf_height / 2,
            text=constants.car_class_list[self.forza5.car_class],
            fill=constants.perf_sticker_background,
            font=theme.h2(),
            anchor=tkinter.CENTER
        )

        perf_index_width = 0.064
        perf_index_height = 0.05
        self.perf_index_canvas = tkinter.Canvas(self.car_perf_frame, background=constants.perf_sticker_background, bd=0, highlightthickness=False)
        self.perf_index_canvas.place(relx=constants.car_info_leftbound_relx + perf_width * 0.55 - 0.002, rely=perf_y + constants.car_info_line_gap - 0.00055, relwidth=perf_index_width, relheight=perf_index_height, anchor=tkinter.W)
        self.perf_index_text = self.perf_index_canvas.create_text(
            self.car_perf_frame.winfo_width() * perf_index_width / 2,
            self.car_perf_frame.winfo_height() * perf_index_height / 2,
            text=self.forza5.car_perf,
            fill=constants.background_color,
            font=theme.h2(),
            anchor=tkinter.CENTER
        )

        # place car drivetrain
        tkinter.Label(
            self.car_perf_frame,
            textvariable=self.car_drivetrain,
            bg=constants.background_color,
            fg=constants.text_color,
            font=theme.h2()
        ).place(
            relx=constants.car_info_leftbound_relx,
            rely=constants.car_info_bottombound_rely - constants.car_info_line_gap,
            anchor=tkinter.SW
        )

        tkinter.Label(
            self.car_perf_frame,
            textvariable=self.car_drivetrain_var,
            bg=constants.background_color,
            fg=constants.text_color,
            font=theme.h1()
        ).place(
            relx=constants.car_info_leftbound_relx,
            rely=constants.car_info_bottombound_rely,
            anchor=tkinter.SW
        )

        # place tire information canvas
        self.tire_canvas = tkinter.Canvas(self.car_perf_frame, background=constants.background_color, bd=0, highlightthickness=False)
        self.tire_canvas.place(relx=constants.tire_canvas_relx, rely=constants.tire_canvas_rely, relwidth=constants.tire_canvas_relwidth, relheight=constants.tire_canvas_relheight, anchor=tkinter.CENTER)
        self.tire_canvas_text = self.tire_canvas.create_text(
            self.car_perf_frame.winfo_width() * constants.tire_canvas_relwidth / 2,
            self.car_perf_frame.winfo_height() * constants.y_padding_top * 0.5,
            text=self.tire_information_txt.get(),
            fill=constants.text_color,
            font=theme.h2(),
            anchor=tkinter.CENTER
        )

        for pos, info in constants.tires.items():
            self.tires[pos] = round_rectangle(
                self.tire_canvas,
                self.car_perf_frame.winfo_width() * info[0],
                self.car_perf_frame.winfo_height() * info[1],
                self.car_perf_frame.winfo_width() * info[2],
                self.car_perf_frame.winfo_height() * info[3],
                radius=info[4],
                fill=constants.background_color,
                width=2,
                outline=constants.text_color
            )

        # place acceleration information text
        tkinter.Label(
            self.car_perf_frame,
            textvariable=self.accel_txt,
            bg=constants.background_color,
            fg=constants.text_color,
            font=theme.h2()
        ).place(
            relx=constants.car_info_rightbound_relx,
            rely=constants.car_info_topbound_rely,
            anchor=tkinter.E
        )

        tkinter.Label(
            self.car_perf_frame,
            textvariable=self.acceleration_var,
            bg=constants.background_color,
            fg=constants.text_color,
            font=theme.display()
        ).place(
            relx=constants.car_info_rightbound_relx,
            rely=0.35,
            anchor=tkinter.E
        )

        # place brake information test
        tkinter.Label(self.car_perf_frame, textvariable=self.brake_txt, bg=constants.background_color, fg=constants.text_color, font=theme.h2()).place(relx=constants.car_info_rightbound_relx, rely=0.545, anchor=tkinter.E)
        tkinter.Label(self.car_perf_frame, textvariable=self.brake_var, bg=constants.background_color, fg=constants.text_color, font=theme.display()).place(relx=constants.car_info_rightbound_relx, rely=0.7, anchor=tkinter.E)

    def set_shift_point_frame(self) -> None:
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

    def set_button_frame(self) -> None:
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

    def set_log_frame(self) -> None:
        """set log frame
        """
        # place log frame
        self.log_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)

        log = scrolledtext.ScrolledText(self.log_frame, bg=constants.background_color, borderwidth=2, font=theme.log_font(), fg=constants.text_color)
        log.pack(fill="both", expand=True)
        log_handler = TextHandler(log)
        self.logger = (Logger(log_handler))('ForzaHorizon5')

        button = tkinter.Button(self.log_frame, textvariable=self.clear_log_text, bg=constants.background_color, fg=constants.text_color, borderwidth=3, highlightcolor=constants.text_color, highlightthickness=True)
        button.bind('<Button-1>', lambda x: log.delete(1.0, 'end'))
        button.place(relx=0.93, rely=0.053, relwidth=0.05, relheight=0.07, anchor='center', bordermode='inside')
        self.log_frame.grid(row=1, column=1, sticky='news')

    def set_program_info_frame(self) -> None:
        """set code info frame
        """
        # place code info frame
        self.program_info_frame = tkinter.Frame(self.root, border=0, bg=constants.background_color, relief="groove", highlightthickness=True, highlightcolor=constants.text_color)

        self.program_info = tkinter.Text(self.program_info_frame, borderwidth=0, bg=constants.background_color, fg=constants.text_color, wrap=tkinter.WORD)
        self.program_info.insert("current", self.program_info_txt.get())
        self.program_info.place(relx=0.03, rely=0.03, relwidth=0.95, relheight=0.95, anchor='nw', bordermode='inside')
        self.program_info.configure(state="disabled")

        self.program_info_frame.grid(row=1, column=2, sticky='news')
