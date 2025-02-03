# -*- coding: utf-8 -*-
import os
import json
import time
import math
import asyncio
import requests
import traceback
import threading
import websockets
import webbrowser
from pygame import mixer
from PyQt6.QtCore import Qt
from plyer import notification
from datetime import datetime, timedelta
from PyQt6.QtGui import QPixmap, QIcon, QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget, QGroupBox, QLineEdit, QCheckBox, QMessageBox

version = "1.1.0"
websocket = None
audio_bool = True
config_updated = False
version_url = "https://tenkyuchimata.github.io/SCEEW/version.json"
settings_window, location_value, latitude_value, longitude_value, audio_value, auto_window_value, notification_value = None, None, None, None, None, None, None
with open("errors.log", "w", encoding = "utf-8") as f:
    f.write("")

def get_bjt():
    return datetime.utcnow() + timedelta(hours = 8)

def error_report():
    error_time = get_bjt().strftime("%Y-%m-%d %H:%M:%S\n")
    error_log = traceback.format_exc()
    print(error_time + error_log + "\n")
    with open("errors.log", "a", encoding = "utf-8") as f:
        f.write(error_time + error_log + "\n")

def updater(window):
    try:
        version_json = requests.get(version_url, timeout = 5).json()
        latest_version = version_json["version"]
        if int(latest_version.replace(".", "")) > int(version.replace(".", "")):
            reply = QMessageBox.question(window, f"四川地震预警(SCEEW) v{version}", f"检测到新版本v{latest_version}, 是否前往更新?")
            if reply == QMessageBox.StandardButton.Yes:
                webbrowser.open("https://github.com/TenkyuChimata/SCEEW/releases")
                closeEvent(None)
    except:
        error_report()
    return None

def set_font(label, font_size):
    try:
        font = QFont()
        font.setPointSize(font_size)
        font_id = QFontDatabase.addApplicationFont("./assets/fonts/SDK_SC_Web.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        font.setFamily(font_family)
        label.setFont(font)
    except:
        error_report()

def get_config():
    try:
        if os.path.exists("config.json"):
            with open("config.json", "r", encoding="utf-8") as f:
                config_data = json.load(f)
            config_data["audio"], config_data["auto_window"], config_data["notification"], config_data["location"], config_data["latitude"], config_data["longitude"]
            return config_data
        else:
            raise KeyError("Incomplete")
    except KeyError:
        config_data = {
            "audio": True,
            "auto_window": True,
            "notification": True,
            "location": "成都市青羊区",
            "latitude": 30.68,
            "longitude": 104.05
        }
        with open("config.json", "w", encoding = "utf-8") as f:
            json.dump(config_data, f, ensure_ascii = False)
        return config_data
    except:
        error_report()
        return None

def saveSettings(event):
    global location_value, latitude_value, longitude_value, audio_value, auto_window_value, notification_value, config_updated
    try:
        if location_value:
            config_data = {
                "audio": audio_value,
                "auto_window": auto_window_value,
                "notification": notification_value,
                "location": location_value,
                "latitude": latitude_value,
                "longitude": longitude_value
            }
            with open("config.json", "w", encoding = "utf-8") as f:
                json.dump(config_data, f, ensure_ascii = False)
            config_updated = True
            if websocket:
                asyncio.run(websocket.send("query_sceew"))
            location_value, latitude_value, longitude_value, audio_value, auto_window_value, notification_value = None, None, None, None, None, None
    except:
        error_report()

def settings_update(location_input, latitude_input, longitude_input, audio_checkbox, auto_window_checkbox, notification_checkbox):
    global location_value, latitude_value, longitude_value, audio_value, auto_window_value, notification_value
    try:
        notification_value = notification_checkbox.isChecked()
        audio_value = audio_checkbox.isChecked()
        auto_window_value = auto_window_checkbox.isChecked()
        if location_input.text() != "":
            location_value = location_input.text()
        else:
            location_value = "成都市青羊区"
        if latitude_input.text() != "":
            latitude_value = float(latitude_input.text())
        else:
            latitude_value = 30.68
        if longitude_input.text() != "":
            longitude_value = float(longitude_input.text())
        else:
            longitude_value = 104.05
    except:
        error_report()

def create_general_tab():
    try:
        tab = QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox("设定")
        group_box.setStyleSheet("QGroupBox:title {color: white;}")
        group_layout = QVBoxLayout()
        config = get_config()
        notification_checkbox = QCheckBox("启用通知")
        notification_checkbox.setChecked(config["notification"])
        notification_checkbox.setStyleSheet("color: white;")
        notification_checkbox.stateChanged.connect(lambda: settings_update(location_input, latitude_input, longitude_input, audio_checkbox, auto_window_checkbox, notification_checkbox))
        group_layout.addWidget(notification_checkbox)
        audio_checkbox = QCheckBox("启用音效")
        audio_checkbox.setChecked(config["audio"])
        audio_checkbox.setStyleSheet("color: white;")
        audio_checkbox.stateChanged.connect(lambda: settings_update(location_input, latitude_input, longitude_input, audio_checkbox, auto_window_checkbox, notification_checkbox))
        group_layout.addWidget(audio_checkbox)
        auto_window_checkbox = QCheckBox("收到预警时自动弹出窗口")
        auto_window_checkbox.setChecked(config["auto_window"])
        auto_window_checkbox.setStyleSheet("color: white;")
        auto_window_checkbox.stateChanged.connect(lambda: settings_update(location_input, latitude_input, longitude_input, audio_checkbox, auto_window_checkbox, notification_checkbox))
        group_layout.addWidget(auto_window_checkbox)
        location_label = QLabel("所在地名")
        set_font(location_label, 12)
        location_label.setStyleSheet("color: white;")
        location_input = QLineEdit()
        location_input.setText(config["location"])
        location_input.setStyleSheet("background-color: #9d9d9d; color: white;")
        location_input.setFixedWidth(150)
        location_input.textChanged.connect(lambda: settings_update(location_input, latitude_input, longitude_input, audio_checkbox, auto_window_checkbox, notification_checkbox))
        latitude_label = QLabel("所在地纬度")
        set_font(latitude_label, 12)
        latitude_label.setStyleSheet("color: white;")
        latitude_input = QLineEdit()
        latitude_input.setText(str(config["latitude"]))
        latitude_input.setStyleSheet("background-color: #9d9d9d; color: white;")
        latitude_input.setFixedWidth(150)
        latitude_input.textChanged.connect(lambda: settings_update(location_input, latitude_input, longitude_input, audio_checkbox, auto_window_checkbox, notification_checkbox))
        longitude_label = QLabel("所在地经度")
        set_font(longitude_label, 12)
        longitude_label.setStyleSheet("color: white;")
        longitude_input = QLineEdit()
        longitude_input.setText(str(config["longitude"]))
        longitude_input.setStyleSheet("background-color: #9d9d9d; color: white;")
        longitude_input.setFixedWidth(150)
        longitude_input.textChanged.connect(lambda: settings_update(location_input, latitude_input, longitude_input, audio_checkbox, auto_window_checkbox, notification_checkbox))
        input_layout = QVBoxLayout()
        input_layout.addWidget(location_label)
        input_layout.addWidget(location_input)
        input_layout.addWidget(latitude_label)
        input_layout.addWidget(latitude_input)
        input_layout.addWidget(longitude_label)
        input_layout.addWidget(longitude_input)
        input_layout.addStretch(1)
        input_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        group_layout.addLayout(input_layout)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        tab.setLayout(layout)
        return tab
    except:
        error_report()
        return None

def create_about_tab():
    try:
        tab = QWidget()
        layout = QVBoxLayout()
        group_box = QGroupBox("关于")
        group_box.setStyleSheet("QGroupBox:title {color: white;}")
        group_layout = QVBoxLayout()
        label = QLabel(f"感谢使用SCEEW v{version}\n开发者: TenkyuChimata\n预警数据来源: 四川省地震局\nAPI: https://api.wolfx.jp\n本软件基于GPL-3.0协议开源\n版权所有 (C) Wolfx Studio.\nGithub: https://github.com/TenkyuChimata/SCEEW")
        label.setStyleSheet("color: white;")
        set_font(label, 12)
        label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        group_layout.addWidget(label)
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        tab.setLayout(layout)
        return tab
    except:
        error_report()
        return None

def open_settings_window():
    global settings_window
    try:
        if settings_window is None:
            settings_window = QWidget()
            settings_window.setWindowTitle("设定")
            settings_window.setWindowIcon(QIcon("./assets/images/icon.ico"))
            settings_window.setStyleSheet("background-color: #808080;")
            settings_window.setFixedSize(600, 400)
            layout = QVBoxLayout()
            tab_widget = QTabWidget()
            tab_widget.addTab(create_general_tab(), "一般")
            tab_widget.addTab(create_about_tab(), "关于")
            tab_widget.setStyleSheet("""
            @font-face {
                font-family: SDK_SC_Web;
                src: url("./assets/fonts/SDK_SC_Web.ttf") format("truetype");
            }
            QTabWidget::pane {
                border: 0;
            }
            QTabWidget::tab-bar {
                alignment: center;
            }
            QTabBar::tab {
                background: #808080;
                color: white;
                padding: 8px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-family: SDK_SC_Web;
                font-size: 14px;
                border-bottom: 3px solid white;
            }
            QTabBar::tab:selected {
                background: #9d9d9d;
                color: white;
            }""")
            layout.addWidget(tab_widget)
            settings_window.setLayout(layout)
        settings_window.closeEvent = saveSettings
        settings_window.show()
    except:
        error_report()

def closeEvent(event):
    os._exit(0)

def alert(types, lv):
    try:
        if audio_bool:
            mixer.init()
            if types:
                mixer.music.load(f".//assets//sounds//EEW{lv}.wav")
                mixer.music.play()
                while mixer.music.get_busy():
                    time.sleep(0.1)
            else:
                mixer.music.load(".//assets//sounds//countdown.wav")
                for i in range(15):
                    mixer.music.play()
                    while mixer.music.get_busy():
                        time.sleep(0.01)
            mixer.quit()
    except:
        error_report()
        mixer.quit()

def distance(lat1, lon1, lat2, lon2):
    try:
        radius = 6378.137
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d = radius * c
        return d
    except:
        error_report()
        return 0

def countdown(user_location, distance, ctime):
    try:
        cycle = True
        Stime = distance / 4
        quaketime = datetime.strptime(ctime, "%Y-%m-%d %H:%M:%S")
        Sarrivetime = quaketime + timedelta(seconds = Stime)
        while cycle:
            s_countdown = (Sarrivetime - get_bjt()).seconds
            if s_countdown <= 0 or s_countdown >= 1200:
                s_countdown = 0
                cycle = False
            if s_countdown:
                subcdinfo_text.setText(f"地震横波还有 {s_countdown} 秒抵达{user_location}")
            else:
                subcdinfo_text.setText(f"地震横波已抵达{user_location}")
            if s_countdown == 9:
                thread5 = threading.Thread(target = alert, args = (False, 0, ))
                thread5.start()
            time.sleep(1)
    except:
        error_report()

def timer():
    while True:
        try:
            info_text.setText(f"四川地震局  {get_bjt().strftime('%H:%M:%S')}  中国地震预警网")
        except:
            error_report()
            continue
        time.sleep(1)

async def sceew(window):
    is_eew = False
    global audio_bool, config_updated, websocket
    while True:
        try:
            async with websockets.connect("wss://ws-api.wolfx.jp/sc_eew") as websocket:
                await websocket.send("query_sceew")
                while True:
                    sceew_json = json.loads(await websocket.recv())
                    if sceew_json["type"] != "heartbeat":
                        print(sceew_json)
                        config = get_config()
                        audio_bool = config["audio"]
                        user_location = config["location"]
                        eqtime = sceew_json["OriginTime"]
                        location = sceew_json["HypoCenter"]
                        magnitude = sceew_json["Magunitude"]
                        eqdistance = distance(sceew_json["Latitude"], sceew_json["Longitude"], config["latitude"], config["longitude"])
                        maxshindo = sceew_json["MaxIntensity"]
                        reportnum = sceew_json["ReportNum"]
                        cnshindo = max(1.92 + 1.63 * magnitude - 3.49 * math.log(eqdistance, 10), 0.0)
                        eqloc_text.setText(f"震中\n{location}\n{int(eqdistance)}km")
                        eqmag_text.setText(f"震级\nM{magnitude}\n烈度{maxshindo}")
                        eqtime_text.setText(f"时间\n{eqtime[0:10].replace('-', '.')}\n{eqtime[-8:]}")
                        if cnshindo >= 1.0 and cnshindo < 2.0:
                            tips_text.setText(f"注意：本地烈度{cnshindo:.1f}，有轻微震感，无需采取措施")
                            message = f"{eqtime} {location}发生M{magnitude}地震，最大预估烈度{maxshindo}度，本地预估烈度{cnshindo:.1f}度。有轻微震感，无需采取措施。"
                        elif cnshindo >= 2.0 and cnshindo < 4.0:
                            tips_text.setText(f"注意：本地烈度{cnshindo:.1f}，有较强震感，请合理避险")
                            message = f"{eqtime} {location}发生M{magnitude}地震，最大预估烈度{maxshindo}度，本地预估烈度{cnshindo:.1f}度。有较强震感，请合理避险！"
                        elif cnshindo >= 4.0:
                            tips_text.setText(f"注意：本地烈度{cnshindo:.1f}，有强烈震感，请合理避险")
                            message = f"{eqtime} {location}发生M{magnitude}地震，最大预估烈度{maxshindo}度，本地预估烈度{cnshindo:.1f}度。有强烈震感，请合理避险！"
                        else:
                            tips_text.setText(f"注意：本地烈度{cnshindo:.1f}，无震感，无需采取措施")
                            message = f"{eqtime} {location}发生M{magnitude}地震，最大预估烈度{maxshindo}度，本地预估烈度{cnshindo:.1f}度。无震感，无需采取措施。"
                        if not config_updated and (get_bjt() - datetime.strptime(eqtime, "%Y-%m-%d %H:%M:%S")).seconds < 300:
                            if config["auto_window"]:
                                window.activateWindow()
                            if cnshindo >= 1.0 and cnshindo < 4.0:
                                thread4 = threading.Thread(target = alert, args = (True, 1, ))
                                thread4.start()
                            elif cnshindo >= 4.0:
                                thread4 = threading.Thread(target = alert, args = (True, 2, ))
                                thread4.start()
                            else:
                                thread4 = threading.Thread(target = alert, args = (True, 0, ))
                                thread4.start()
                            if not is_eew:
                                is_eew = True
                                thread3 = threading.Thread(target = countdown, args = (user_location, eqdistance, eqtime, ))
                                thread3.start()
                            if config["notification"]:
                                title = f"四川地震预警（第{reportnum}报）"
                                notification.notify(title = title, message = message, app_name = f"四川地震预警(SCEEW) v{version}", app_icon = "./assets/images/icon.ico")
                        else:
                            subcdinfo_text.setText(f"地震横波已抵达{user_location}")
                        config_updated = False
                    else:
                        if is_eew and (get_bjt() - datetime.strptime(eqtime, "%Y-%m-%d %H:%M:%S")).seconds > 300:
                            is_eew = False
        except:
            error_report()
            time.sleep(1)
            continue

if __name__ == '__main__':
    try:
        app = QApplication([])
        window = QMainWindow()
        window.setWindowTitle(f"四川地震预警(SCEEW) v{version}")
        window.setFixedSize(600, 400)
        window.setWindowIcon(QIcon("./assets/images/icon.ico"))
        updater(window)
        window.setStyleSheet("background-color: #808080;")
        central_widget = QWidget()
        window.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        title_text = QLabel("四川地震预警", alignment = Qt.AlignmentFlag.AlignCenter)
        title_text.setStyleSheet("color: white; padding-top: 10px;")
        set_font(title_text, 25)
        layout.addWidget(title_text)
        warn_icon = QLabel()
        warn_icon.setPixmap(QPixmap("./assets/images/warn.png"))
        warn_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warn_icon)
        subcdinfo_text = QLabel("", alignment = Qt.AlignmentFlag.AlignCenter)
        subcdinfo_text.setStyleSheet("color: white;")
        set_font(subcdinfo_text, 20)
        layout.addWidget(subcdinfo_text)
        tips_text = QLabel("", alignment = Qt.AlignmentFlag.AlignCenter)
        tips_text.setStyleSheet("color: white;")
        set_font(tips_text, 15)
        layout.addWidget(tips_text)
        eq_info_layout = QHBoxLayout()
        layout.addLayout(eq_info_layout)
        eqloc_frame = QWidget()
        eqloc_frame.setStyleSheet("background-color: #9d9d9d;")
        eq_info_layout.addWidget(eqloc_frame)
        eqloc_layout = QVBoxLayout(eqloc_frame)
        eqloc_text = QLabel("", alignment = Qt.AlignmentFlag.AlignCenter)
        eqloc_text.setStyleSheet("color: white;")
        set_font(eqloc_text, 15)
        eqloc_layout.addWidget(eqloc_text)
        eqmag_frame = QWidget()
        eqmag_frame.setStyleSheet("background-color: #9d9d9d;")
        eq_info_layout.addWidget(eqmag_frame)
        eqmag_layout = QVBoxLayout(eqmag_frame)
        eqmag_text = QLabel("", alignment = Qt.AlignmentFlag.AlignCenter)
        eqmag_text.setStyleSheet("color: white;")
        set_font(eqmag_text, 15)
        eqmag_layout.addWidget(eqmag_text)
        eqtime_frame = QWidget()
        eqtime_frame.setStyleSheet("background-color: #9d9d9d;")
        eq_info_layout.addWidget(eqtime_frame)
        eqtime_layout = QVBoxLayout(eqtime_frame)
        eqtime_text = QLabel("", alignment = Qt.AlignmentFlag.AlignCenter)
        eqtime_text.setStyleSheet("color: white;")
        set_font(eqtime_text, 15)
        eqtime_layout.addWidget(eqtime_text)
        info_text = QLabel("", alignment = Qt.AlignmentFlag.AlignCenter)
        info_text.setStyleSheet("color: white;")
        set_font(info_text, 15)
        layout.addWidget(info_text)
        settings_button = QPushButton("⚙", window)
        settings_button.setGeometry(560, 360, 25, 25)
        settings_button.clicked.connect(open_settings_window)
        window.closeEvent = closeEvent
        window.show()
        thread1 = threading.Thread(target = timer)
        thread1.start()
        thread2 = threading.Thread(target = asyncio.run, args = (sceew(window), ))
        thread2.start()
        app.exec()
    except:
        error_report()
