[简体中文](./README.zhcn.md)

# forza_auto_gear
forza_auto_gear is a tool for Forza Horizon 5. It will help us understand the best gear shift point using Manual or w/ Clutch in Forza Horizon 5. Built with python.

## Quick View
GUI Demo

[Demo](https://www.bilibili.com/video/BV11R4y1A7jA/)

A800, GTR93, Aerodromo Drag Strip
- Automatic (00:27.665):
![automatic](./img/automatic.png)
- Manual (00:27.166):
![manual](./img/manual.png)
- Manual with Clutch (00:26.441):
![manual w/ clutch](./img/manual_and_clutch.png)
- Program, Manual with Clutch (00:26.265):
![program manual w/ clutch](./img/program_m_and_c.png)

## Prerequisites
Install >= Python 3.8

## Game Setup
Setup the data out:
![data_output_settings](./img/output_settings.png)

## Installation
1. You could download and run the source code directly
    ```
    pip3 install -r requirements.txt
    git submodule init
    git submodule update --recursive
    ```
2. You could download the `Forza_Auto_Gear_GUI` from the [release](https://github.com/Juice-XIJ/forza_auto_gear/releases) to run the `Forza_Auto_Gear_GUI.exe` directly.

## Usage
1. If you download the `Forza_Auto_Gear_GUI.exe` directly, the GUI is running. If you download the source code, please run: `python ./gui.py` to use GUI. If preferred command line, please run `python ./main.py`.
2. F10 starts the data collection:
    - Find a drag strip location.
    - Starting from Gear 1, accelerate until fuel cut-off (rpm is vibrating), then up shifting gear. Repeat until reaching the maximum gear.
    - Press REWIND to pause, then press F10 to stop data collect.
3. F8 to analyze the data. It will generate the car performance figures like below:
![console_analysis](./img/forza_performance_analysis_console.png)
![forza_performance_analysis](./img/forza_performance_analysis.png)
Then the result will be saved at `./config/{car ordinal}.json`
4. F7 to start auto gear shifting! Press F7 again to stop.
    - GUI:
    ![f7 gui test](./img/f7_gui_test.png)

    - Command Line:
    ![f7 test](./img/f7_test.png)
5. If you are running exp and skill point farming in long blueprint, you could enable the farming mode in GUI left panel by checking `farm`. It will help you press brake to avoid AFK detection and reset car position if you got stuck.

## Moreover
1. By default the shifting mode is Manual with Clutch. You could change it in `constants.py`. If you are using the GUI, you could switch Clutch at the top right corner. If you want to change shortcuts, there are a few shortcut modifications available in left panel of GUI.
2. Lots of variables could be modified in `constants.py`
3. If you already have the config file, then run F7 directly. It will load the config automatically while driving. Or you could share configs to your friends. Don't forget to share your car tune as well :)
4. You could modify the log level in `logger.py` for console and file handlers.
5. Feel free to modify any logic to fit your style.

## Acknowledgments
- [forza_motorsport](https://github.com/nettrom/forza_motorsport) for data reading protocol
- [forza-MT-auto](https://github.com/Yuandiaodiaodiao/forza-MT-auto) for the inspirations
- [Optimal Shift Point](https://glennmessersmith.com/shiftpt.html) for shift point calculation
