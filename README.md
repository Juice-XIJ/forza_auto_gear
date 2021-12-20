# forza_auto_gear
forza_auto_gear is a tool for Forza5. It will help us understand the best gear shift point using Manual or w/ Clutch in Forza5. Built with python.

## Prerequisites
Install >= Python 3.8

## Installation
```
pip3 install -r requirements.txt
git submodule update --recursive
```

## Usage
0. Setup the data out:
![data_output_settings](./img/output_settings.png)
1. Run main.py
2. F10 starts the data collection:
    - Find a drag strip location.
    - Starting from Gear 1, accelerate until fuel cut-off (rpm is vibrating), then up shifting gear. Repeat until reaching the maximum gear.
    - Press REWIND to pause, then press F10 to stop data collect.
3. F8 to analyze the data. It will generate the car perfomance figures like below:
![forza_performance_analysis](./img/forza_performance_analysis.png)
Then the result will be saved at `./config/{car ordinal}.json`
4. F7 to start auto gear shifting! Press F7 again to stop.

## Moreover
1. By default the shifting mode Manual with Clutch. You could change it in `constants.py`.
2. Lots of variables could be modified in `constants.py`
3. If you already have the config file, then run F7 directly. It will load the config automatically while driving. Or you could share configs to your friends. Don't forget to share your car tune as well :)
4. You could modify the log level in `logger.py` for console and file handlers.

## Acknowledgments
- [forza_motorsport](https://github.com/nettrom/forza_motorsport) for data reading protocal
- [forza-MT-auto](https://github.com/Yuandiaodiaodiao/forza-MT-auto) for the inspirations
- [Optimal Shift Point](https://glennmessersmith.com/shiftpt.html) for shift point calculation
