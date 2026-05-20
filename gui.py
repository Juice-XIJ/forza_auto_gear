"""Forza Horizon 5 Auto Gear — Tkinter GUI orchestrator.

This module owns ``MainWindow``: window construction, the data-binding
layer of ``StringVar`` / ``IntVar`` instances, hotkey wiring through
pynput, and the lifecycle of the Forza telemetry / shifting loop.

The threading model is:

* The Tk root and all widgets live on the *main* thread.
* :class:`update_queue.TkUpdateQueue` (``self.ui_queue``) marshals
  closures back to the main thread when called from the pynput listener
  thread or any :class:`ThreadPoolExecutor` worker.
* The five ``_ui_*`` shims (``_ui_update_car_info`` etc.) are the
  worker-safe entry points passed to :mod:`forza` and to closures
  submitted to ``threadPool``.

Layout code (the six ``set_*_frame`` builders and their helpers) lives
in :mod:`gui_frames` as the :class:`~gui_frames.FrameBuilderMixin` mixin.
Utility widgets and lifecycle helpers live in :mod:`gui_widgets`.
"""

from __future__ import annotations

import os
import tkinter
import warnings
from concurrent.futures import ThreadPoolExecutor

import matplotlib.colors as mcolors
from pynput.keyboard import Listener

import constants
import helper
import theme
from forza import Forza
from gui_frames import FrameBuilderMixin
from gui_widgets import shutdown
from update_queue import TkUpdateQueue

# suppress matplotlib warning while running in thread
warnings.filterwarnings("ignore", category=UserWarning)


class MainWindow(FrameBuilderMixin):

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
        # No maxsize cap so the window can scale on 4K / multi-monitor setups.
        self.root["background"] = constants.background_color

        # Configure shared ttk styles once at startup. Today only the
        # Treeview picks these up; the long-term migration moves the rest
        # of the widgets in gui_frames.py over to the named Forza.* styles.
        theme.apply_global_ttk_theme(self.root)

        # widgets to be updated
        self.speed_tree = {}
        self.rpm_tree = {}

        self.car_id_var = tkinter.StringVar()
        self.car_id_var.set("None")
        self.car_perf_var = tkinter.IntVar()
        self.car_perf_var.set(0)
        self.car_class_var = tkinter.IntVar()
        self.car_class_var.set(-1)
        self.car_drivetrain_var = tkinter.StringVar()
        self.car_drivetrain_var.set('N')

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

        # Thread-safe pump for marshaling background-thread updates onto the
        # Tk main thread. Started before mainloop so any enqueue from the
        # pynput listener or ThreadPool workers is delivered safely.
        self.ui_queue = TkUpdateQueue(self.root)
        self.ui_queue.start()

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
        self.offroad_rally_txt = tkinter.StringVar()
        self.car_id = tkinter.StringVar()
        self.car_perf = tkinter.StringVar()
        self.car_drivetrain = tkinter.StringVar()
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
        self.offroad_rally_txt.set(constants.offroad_rally_txt[lang_index])
        self.car_id.set(constants.car_id[lang_index])
        self.car_perf.set(constants.car_perf[lang_index])
        self.car_drivetrain.set(constants.car_drivetrain[lang_index])
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
        max_key = 0
        for key, value in self.forza5.shift_point.items():
            self.treeview.item(self.speed_tree[key], values=round(value['speed'], 3))
            self.treeview.item(self.rpm_tree[key], values=round(value['rpmo'], 3))
            max_key = key

        upper_bound = min(11, max(max_key + 1, self.forza5.maxGear + 1))
        for i in range(max_key + 1, upper_bound):
            self.treeview.item(self.speed_tree[i], values='-')
            self.treeview.item(self.rpm_tree[i], values='-')

    def update_car_info(self, fdp):
        """update car info

        Args:
            fdp: fdp
        """
        if self.forza5.isRunning:
            # Update car information
            self.car_id_var.set(fdp.car_ordinal)
            self.car_perf_var.set(fdp.car_performance_index)
            self.car_class_var.set(fdp.car_class)
            self.car_drivetrain_var.set(constants.car_drivetrain_list[fdp.drivetrain_type][self.language])

            # Update PERF CARD
            self.perf_canvas.config(bg=constants.car_class_color[fdp.car_class])
            self.perf_canvas.itemconfig(self.car_class_text, text=constants.car_class_list[fdp.car_class])
            self.perf_index_canvas.itemconfig(self.perf_index_text, text=fdp.car_performance_index)

            # Update acceleration and brake value
            self.acceleration_var.set(f"{str(round(fdp.accel / 255 * 100, 1))}%")
            self.brake_var.set(f"{str(round(fdp.brake / 255 * 100, 1))}%")

            # Update tire slip colors. Each corner uses the same mapping:
            # 0 <= slip < 0.8 -> green->yellow (0..0.5 in the gradient)
            # 0.8 <= slip <= 1.0 -> yellow->red (0.8..1.0 in the gradient)
            for pos in ("FL", "FR", "RL", "RR"):
                raw = abs(getattr(fdp, f"tire_combined_slip_{pos}"))
                slip = raw if raw < 1 else 1
                color = self.tire_color(
                    slip / 0.8 * 0.5 if slip < 0.8 else (1 - slip) / 0.2 * 0.5 + 0.8
                )
                self.tire_canvas.itemconfig(
                    self.tires[pos],
                    fill=helper.rgb(color[0], color[1], color[2]),
                )

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

        # reset all four tires to the neutral (background) color
        for pos in ("FL", "FR", "RL", "RR"):
            self.tire_canvas.itemconfig(self.tires[pos], fill=constants.background_color)

    def on_press(self, key):
        """on press callback

        pynput invokes this on its own listener thread. Marshal onto the
        Tk main thread (via the update queue) so handlers can safely touch
        widgets. When called from the main thread (e.g. unit tests), the
        queue runs the callback inline so behavior remains synchronous.

        Args:
            key: key
        """
        self.ui_queue.call_on_main(self._on_press_main, key)

    def _on_press_main(self, key):
        """Main-thread dispatch of an on_press event."""
        try:
            if key == constants.collect_data:
                self.collect_data_handler(None)
            elif key == constants.analysis:
                self.analysis_handler(None, performance_profile=False, is_gui=False)
            elif key == constants.auto_shift:
                self.run_handler(None)
            elif key == constants.stop:
                self.pause_handler(None)
            elif key == constants.close:
                self.exit_handler(None)
        except BaseException as e:
            self.forza5.logger.exception(e)

    # --- Worker-safe shims -------------------------------------------------
    # The Forza worker callbacks below are invoked from ThreadPoolExecutor
    # workers; routing them through ``ui_queue.call_on_main`` keeps Tk
    # widget mutations on the main thread without forcing callers to know
    # which thread they're on.

    def _ui_update_car_info(self, fdp):
        self.ui_queue.call_on_main(self.update_car_info, fdp)

    def _ui_update_tree(self):
        self.ui_queue.call_on_main(self.update_tree)

    def _ui_reset_car_info(self):
        self.ui_queue.call_on_main(self.reset_car_info)

    def close(self):
        """close program
        """
        self.ui_queue.stop()
        shutdown(self.forza5, self.threadPool, self.listener)
        self.root.destroy()

    def collect_data_handler(self, event):
        """collect data button callback

        Args:
            event
        """
        if self.forza5.isRunning:
            self.logger.info('stopping gear test')

            def stopping():
                self.forza5.isRunning = False
                self._ui_reset_car_info()

            self.threadPool.submit(stopping)
        else:
            self.logger.info('starting gear test')

            def starting():
                self.forza5.isRunning = True
                self.forza5.test_gear(self._ui_update_car_info)

            self.threadPool.submit(starting)

    def analysis_handler(self, event, performance_profile=True, is_gui=True):
        """analysis button callback

        Args:
            event
            performance_profile (bool, optional): draw performance of not. Defaults to True.
            is_gui (bool, optional): is gui or not. Defaults to True.
        """
        if len(self.forza5.records) <= 0:
            self.logger.info(f'load config {constants.example_car_ordinal}.json for analysis as an example')
            helper.load_config(self.forza5, os.path.join(constants.root_path, 'example', f'{constants.example_car_ordinal}.json'))
        self.logger.info('Analysis')

        self.forza5.analyze(performance_profile=performance_profile, is_gui=is_gui)
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
                self._ui_reset_car_info()

            self.threadPool.submit(stopping)
        else:
            self.forza5.logger.info('starting auto gear')

            def starting():
                self.forza5.isRunning = True
                self.forza5.run(self._ui_update_tree, self._ui_update_car_info)

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
        self.ui_queue.stop()
        shutdown(self.forza5, self.threadPool, self.listener)
        helper.dump_settings(self.forza5)
        self.forza5.logger.info('bye~')
        self.root.destroy()


def main():
    """Launch the GUI."""
    MainWindow()


if __name__ == "__main__":
    main()
