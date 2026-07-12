from __future__ import annotations

import json
import sys
import time
from pathlib import Path

try:
    from PySide6.QtCore import QPoint, QSettings, Qt, QTimer
    from PySide6.QtGui import QColor, QFont, QFontDatabase, QLinearGradient, QPainter, QPainterPath, QPen
    from PySide6.QtWidgets import (
        QApplication, QCheckBox, QComboBox, QDialog, QFrame, QGridLayout, QHBoxLayout,
        QGraphicsDropShadowEffect, QLabel, QMainWindow, QMessageBox, QProgressBar, QPushButton, QSizePolicy, QTextEdit,
        QVBoxLayout, QWidget,
    )
except ModuleNotFoundError as exc:
    raise SystemExit("PySide6 is required. Run: python -m pip install PySide6") from exc

from backend import RESULT_PATH, discover_network, gateway_result, gateway_state, launch


BG = "#040814"
CARD = "#091426"
BORDER = "#1b3a60"
TEXT = "#f6f9ff"
MUTED = "#91a8cb"
CYAN = "#19d7ff"
BLUE = "#477cff"
GREEN = "#2ce6a2"
RED = "#ff6680"
ROOT = Path(__file__).resolve().parent
EN_FONT = "Segoe UI Variable Text"
FA_FONT = "Vazirmatn"

TRANSLATIONS = {
    "en": {
        "language": "فارسی", "subtitle": "Universal VPN sharing for all LAN devices",
        "routing_title": "ROUTING SOURCE", "routing_hint": "Route-based VPNs and local SOCKS5 proxy modes are supported.",
        "vpn_label": "ACTIVE VPN / TUNNEL", "lan_label": "DEVICE NETWORK / LAN", "detect": "AUTO DETECT",
        "nat": "Enable WinNAT compatibility mode", "kill": "Stop sharing automatically if VPN disconnects",
        "device_title": "DEVICE NETWORK SETTINGS", "device_hint": "Use these values in the manual network settings of any device connected to this LAN.",
        "device_ip": "Device IP", "mask": "Subnet mask", "gateway": "Gateway (PC)", "dns": "DNS",
        "start": "START GATEWAY", "stop": "STOP & RESTORE", "copy": "COPY DEVICE SETTINGS",
        "activity": "ACTIVITY", "activity_hint": "Administrator access is requested only when Windows routing changes.",
        "offline": "OFFLINE", "active": "GATEWAY ACTIVE", "select_both": "Select both VPN and LAN adapters.",
        "different": "VPN and LAN adapters must be different.", "tv_settings": "Device Network Settings",
        "loading": "Detecting network sources…", "close": "CLOSE", "copied": "Device settings copied to clipboard.",
        "television": "TELEVISION", "mobile": "MOBILE", "device_model": "DEVICE PROFILE",
    },
    "fa": {
        "language": "English", "subtitle": "اشتراک‌گذاری اینترنت VPN برای تمام دستگاه‌های شبکه",
        "routing_title": "منبع اتصال", "routing_hint": "VPNهای مسیری و پراکسی‌های SOCKS5 محلی پشتیبانی می‌شوند.",
        "vpn_label": "VPN یا تونل فعال", "lan_label": "شبکه دستگاه / شبکه محلی", "detect": "تشخیص خودکار",
        "nat": "فعال‌سازی حالت سازگاری WinNAT", "kill": "قطع خودکار اشتراک‌گذاری هنگام قطع VPN",
        "device_title": "تنظیمات شبکه دستگاه‌ها", "device_hint": "این مقادیر را در تنظیمات دستی شبکه هر دستگاه متصل به این شبکه وارد کنید.",
        "device_ip": "آی‌پی دستگاه", "mask": "ماسک شبکه", "gateway": "درگاه کامپیوتر", "dns": "دی‌ان‌اس",
        "start": "فعال‌سازی درگاه", "stop": "توقف و بازیابی", "copy": "کپی تنظیمات دستگاه",
        "activity": "گزارش فعالیت", "activity_hint": "دسترسی Administrator فقط هنگام تغییر تنظیمات شبکه درخواست می‌شود.",
        "offline": "غیرفعال", "active": "درگاه فعال", "select_both": "VPN و شبکه محلی را انتخاب کنید.",
        "different": "آداپتر VPN و LAN باید متفاوت باشند.", "tv_settings": "تنظیمات شبکه دستگاه",
        "loading": "در حال شناسایی منابع شبکه…", "close": "بستن", "copied": "تنظیمات دستگاه کپی شد.",
        "television": "تلویزیون", "mobile": "موبایل", "device_model": "مدل دستگاه",
    },
}


DEVICE_PROFILES = {
    "tv": [
        {
            "id": "samsung_tv", "en": "Samsung TV", "fa": "تلویزیون سامسونگ",
            "fields": (("IP Address", "ip"), ("Subnet Mask", "mask"), ("Gateway", "gateway"), ("DNS Server", "dns")),
            "guide": "Settings › General › Network › Network Status › IP Settings",
        },
        {
            "id": "lg_tv", "en": "LG TV", "fa": "تلویزیون ال‌جی",
            "fields": (("IP Address", "ip"), ("Subnet Mask", "mask"), ("Gateway", "gateway"), ("DNS Server", "dns")),
            "guide": "Settings › Network › Wi-Fi Connection › Advanced Wi-Fi Settings › Edit",
        },
        {
            "id": "sony_tv", "en": "Sony TV", "fa": "تلویزیون سونی",
            "fields": (("IP address", "ip"), ("Subnet mask", "mask"), ("Gateway", "gateway"), ("Primary DNS", "dns")),
            "guide": "Settings › Network & Internet › IP settings › Static",
        },
    ],
    "mobile": [
        {
            "id": "xiaomi", "en": "Xiaomi", "fa": "شیائومی",
            "fields": (("IP address", "ip"), ("Gateway", "gateway"), ("Network prefix length", "prefix"), ("DNS 1", "dns")),
            "guide": "Settings › Wi-Fi › Selected network › IP settings › Static",
        },
        {
            "id": "samsung_mobile", "en": "Samsung", "fa": "سامسونگ",
            "fields": (("IP address", "ip"), ("Gateway", "gateway"), ("Network prefix length", "prefix"), ("DNS 1", "dns")),
            "guide": "Settings › Connections › Wi-Fi › Gear icon › View more › IP settings › Static",
        },
        {
            "id": "huawei", "en": "Huawei", "fa": "هواوی",
            "fields": (("IP address", "ip"), ("Gateway", "gateway"), ("Network prefix length", "prefix"), ("DNS 1", "dns")),
            "guide": "Settings › Wi-Fi › Selected network › Modify network › Advanced options › Static",
        },
        {
            "id": "iphone", "en": "iPhone", "fa": "آیفون",
            "fields": (("IP Address", "ip"), ("Subnet Mask", "mask"), ("Router", "gateway"), ("DNS", "dns")),
            "guide": "Settings › Wi-Fi › ⓘ › Configure IP › Manual / Configure DNS › Manual",
        },
    ],
}


class LogoMark(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setFixedSize(46, 46)

    def paintEvent(self, event) -> None:
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.moveTo(23, 3); path.lineTo(40, 12); path.lineTo(40, 31)
        path.lineTo(23, 42); path.lineTo(6, 31); path.lineTo(6, 12); path.closeSubpath()
        gradient = QLinearGradient(5, 5, 42, 42)
        gradient.setColorAt(0, QColor("#44f0ff")); gradient.setColorAt(1, QColor("#496cff"))
        p.setPen(QPen(gradient, 3)); p.setBrush(QColor("#07162a")); p.drawPath(path)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(QColor("#2de5b2")); p.drawEllipse(19, 18, 8, 8)


class GlowPanel(QFrame):
    def __init__(self, accent: str = BLUE) -> None:
        super().__init__()
        self.accent = accent
        self.setObjectName("GlowPanel")
        shadow = QGraphicsDropShadowEffect(self)
        color = QColor(accent); color.setAlpha(38)
        shadow.setColor(color); shadow.setBlurRadius(30); shadow.setOffset(0, 7)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        a = QColor(self.accent); a.setAlpha(20)
        b = QColor("#081224"); b.setAlpha(8)
        gradient.setColorAt(0, a); gradient.setColorAt(1, b)
        p.setBrush(gradient)
        p.setPen(QPen(QColor(BORDER), 1))
        p.drawRoundedRect(self.rect().adjusted(1, 1, -2, -2), 16, 16)


class ValueBox(QFrame):
    def __init__(self, title: str, value: str = "-") -> None:
        super().__init__()
        self.setObjectName("ValueBox")
        self.setMinimumHeight(72)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 11, 16, 11)
        layout.setSpacing(4)
        self.label = QLabel(title.upper()); self.label.setObjectName("TinyLabel")
        self.value = QLabel(value); self.value.setObjectName("ValueText")
        self.value.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.value.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.label); layout.addWidget(self.value)

    def set_value(self, value: object) -> None:
        self.value.setText(str(value))

    def set_title(self, title: str) -> None:
        self.label.setText(title.upper())


class WindowControlButton(QPushButton):
    """Crisp, DPI-independent title-bar controls."""
    def __init__(self, kind: str) -> None:
        super().__init__()
        self.kind = kind
        self.setObjectName("CloseButton" if kind == "close" else "WindowButton")
        self.setFixedSize(38, 34)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#e8f2ff"), 1.7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        cx, cy = self.width() / 2, self.height() / 2
        if self.kind == "close":
            painter.drawLine(int(cx - 4), int(cy - 4), int(cx + 4), int(cy + 4))
            painter.drawLine(int(cx + 4), int(cy - 4), int(cx - 4), int(cy + 4))
        else:
            painter.drawLine(int(cx - 5), int(cy + 2), int(cx + 5), int(cy + 2))


class DeviceSettingsDialog(QDialog):
    def __init__(self, parent: QWidget, title: str, values: list[tuple[str, str]], close_text: str, rtl: bool) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.setFixedWidth(440)

        shell = QFrame(self); shell.setObjectName("DialogShell")
        outer = QVBoxLayout(self); outer.setContentsMargins(10, 10, 10, 10); outer.addWidget(shell)
        layout = QVBoxLayout(shell); layout.setContentsMargins(22, 18, 22, 20); layout.setSpacing(14)

        header = QHBoxLayout(); header.setSpacing(10)
        heading = QLabel(title); heading.setObjectName("DialogTitle")
        close_icon = WindowControlButton("close"); close_icon.clicked.connect(self.accept)
        header.addWidget(heading, 1); header.addWidget(close_icon)
        layout.addLayout(header)

        values_panel = QFrame(); values_panel.setObjectName("DialogValues")
        values_layout = QGridLayout(values_panel); values_layout.setContentsMargins(16, 12, 16, 12)
        values_layout.setHorizontalSpacing(18); values_layout.setVerticalSpacing(10)
        for row, (label, value) in enumerate(values):
            name = QLabel(label); name.setObjectName("DialogLabel")
            data = QLabel(value); data.setObjectName("DialogValue")
            data.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
            name.setAlignment(Qt.AlignmentFlag.AlignRight if rtl else Qt.AlignmentFlag.AlignLeft)
            data.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label_column, value_column = (1, 0) if rtl else (0, 1)
            values_layout.addWidget(name, row, label_column)
            values_layout.addWidget(data, row, value_column)
        values_layout.setColumnStretch(0 if rtl else 1, 1)
        layout.addWidget(values_panel)

        done = QPushButton(close_text); done.setObjectName("PrimaryButton"); done.clicked.connect(self.accept)
        layout.addWidget(done)
        self.setStyleSheet(parent.styleSheet())


class UacGateway(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.settings = QSettings("UAC", "UAC Gateway")
        self.language = str(self.settings.value("language", "en"))
        if self.language not in TRANSLATIONS:
            self.language = "en"
        self.adapters: list[dict] = []
        self.proxies: list[dict] = []
        self.pending_action: str | None = None
        self.pending_since = 0.0
        self.drag_pos: QPoint | None = None
        self.device_category = str(self.settings.value("device_category", "tv"))
        if self.device_category not in DEVICE_PROFILES:
            self.device_category = "tv"
        self.device_profile_id = str(self.settings.value("device_profile", DEVICE_PROFILES[self.device_category][0]["id"]))
        self.network_values = {"ip": "-", "mask": "-", "prefix": "-", "gateway": "-", "dns": "-"}

        self.setWindowTitle("UAC Gateway")
        self.setMinimumSize(920, 720)
        self.resize(1120, 850)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.build_ui()
        self.apply_language()
        self.apply_style()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        QTimer.singleShot(150, self.refresh_adapters)

    def build_ui(self) -> None:
        shell = QFrame(); shell.setObjectName("Shell")
        self.setCentralWidget(shell)
        root = QVBoxLayout(shell); root.setContentsMargins(1, 1, 1, 1); root.setSpacing(0)

        self.titlebar = QFrame(); self.titlebar.setObjectName("TitleBar")
        title_layout = QHBoxLayout(self.titlebar); title_layout.setContentsMargins(25, 15, 18, 14)
        logo = LogoMark()
        titles = QVBoxLayout(); titles.setSpacing(0)
        self.app_title = QLabel("UAC GATEWAY"); self.app_title.setObjectName("AppTitle")
        self.app_subtitle = QLabel(); self.app_subtitle.setObjectName("Subtitle")
        titles.addWidget(self.app_title); titles.addWidget(self.app_subtitle)
        self.status = QLabel("●  OFFLINE"); self.status.setObjectName("StatusOff")
        self.lang_btn = QPushButton(); self.lang_btn.setObjectName("LanguageButton"); self.lang_btn.clicked.connect(self.toggle_language)
        minimize = WindowControlButton("minimize"); minimize.clicked.connect(self.showMinimized)
        close = WindowControlButton("close"); close.clicked.connect(self.close)
        title_layout.addWidget(logo); title_layout.addSpacing(10); title_layout.addLayout(titles)
        title_layout.addStretch(1); title_layout.addWidget(self.lang_btn); title_layout.addSpacing(8)
        self.loading_bar = QProgressBar(); self.loading_bar.setObjectName("LoadingBar")
        self.loading_bar.setRange(0, 0); self.loading_bar.setTextVisible(False); self.loading_bar.setFixedSize(74, 4)
        title_layout.addWidget(self.loading_bar); title_layout.addSpacing(8)
        title_layout.addWidget(self.status); title_layout.addSpacing(10)
        title_layout.addWidget(minimize); title_layout.addWidget(close)
        root.addWidget(self.titlebar)

        self.body = QWidget(); body_layout = QVBoxLayout(self.body)
        body_layout.setContentsMargins(26, 18, 26, 26); body_layout.setSpacing(16)
        root.addWidget(self.body, 1)

        selector = GlowPanel(CYAN)
        grid = QGridLayout(selector); grid.setContentsMargins(22, 18, 22, 20); grid.setHorizontalSpacing(16); grid.setVerticalSpacing(10)
        self.routing_title = QLabel(); self.routing_title.setObjectName("SectionTitle")
        self.routing_hint = QLabel(); self.routing_hint.setObjectName("Hint")
        grid.addWidget(self.routing_title, 0, 0, 1, 3); grid.addWidget(self.routing_hint, 1, 0, 1, 3)
        self.vpn_field_label = self.field_label(""); self.lan_field_label = self.field_label("")
        grid.addWidget(self.vpn_field_label, 3, 0)
        grid.addWidget(self.lan_field_label, 3, 1)
        self.refresh_btn = QPushButton("AUTO DETECT"); self.refresh_btn.setObjectName("SecondaryButton"); self.refresh_btn.clicked.connect(self.refresh_adapters)
        self.vpn_combo = QComboBox(); self.vpn_combo.currentIndexChanged.connect(self.update_preview)
        self.lan_combo = QComboBox(); self.lan_combo.currentIndexChanged.connect(self.update_preview)
        grid.addWidget(self.vpn_combo, 4, 0); grid.addWidget(self.lan_combo, 4, 1); grid.addWidget(self.refresh_btn, 4, 2)
        self.nat_check = QCheckBox("Enable WinNAT compatibility mode"); self.nat_check.setChecked(True)
        self.kill_check = QCheckBox("Stop sharing automatically if VPN disconnects"); self.kill_check.setChecked(True)
        self.options_widget = QWidget(); options = QHBoxLayout(self.options_widget)
        options.setContentsMargins(0, 5, 0, 0); options.setSpacing(28)
        options.addWidget(self.nat_check); options.addWidget(self.kill_check); options.addStretch(1)
        grid.addWidget(self.options_widget, 5, 0, 1, 3)
        grid.setColumnStretch(0, 1); grid.setColumnStretch(1, 1); grid.setColumnMinimumWidth(2, 145)
        body_layout.addWidget(selector)

        network = GlowPanel(BLUE)
        network_layout = QVBoxLayout(network); network_layout.setContentsMargins(22, 17, 22, 20); network_layout.setSpacing(12)
        device_header, self.device_title, self.device_hint = self.section("", "")
        network_layout.addWidget(device_header)
        self.device_selector = QFrame(); self.device_selector.setObjectName("DeviceSelector")
        selector_layout = QHBoxLayout(self.device_selector); selector_layout.setContentsMargins(8, 7, 8, 7); selector_layout.setSpacing(8)
        self.tv_tab = QPushButton(); self.tv_tab.setObjectName("DeviceTab"); self.tv_tab.setCheckable(True)
        self.mobile_tab = QPushButton(); self.mobile_tab.setObjectName("DeviceTab"); self.mobile_tab.setCheckable(True)
        self.tv_tab.clicked.connect(lambda: self.set_device_category("tv"))
        self.mobile_tab.clicked.connect(lambda: self.set_device_category("mobile"))
        self.device_model_label = self.field_label("")
        self.device_combo = QComboBox(); self.device_combo.setObjectName("DeviceCombo")
        self.device_combo.currentIndexChanged.connect(self.device_profile_changed)
        selector_layout.addWidget(self.tv_tab); selector_layout.addWidget(self.mobile_tab)
        selector_layout.addSpacing(8); selector_layout.addWidget(self.device_model_label)
        selector_layout.addWidget(self.device_combo, 1)
        network_layout.addWidget(self.device_selector)
        self.device_guide = QLabel(); self.device_guide.setObjectName("DeviceGuide")
        self.device_guide.setWordWrap(True); self.device_guide.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        network_layout.addWidget(self.device_guide)
        values = QGridLayout(); values.setSpacing(10)
        self.tv_ip = ValueBox("Device IP")
        self.mask = ValueBox("Subnet mask")
        self.gateway = ValueBox("Gateway (PC)")
        self.dns = ValueBox("DNS")
        for i, box in enumerate((self.tv_ip, self.mask, self.gateway, self.dns)):
            values.addWidget(box, 0, i)
        network_layout.addLayout(values)
        body_layout.addWidget(network)

        actions = QHBoxLayout(); actions.setSpacing(14)
        self.start_btn = QPushButton("START GATEWAY"); self.start_btn.setObjectName("PrimaryButton"); self.start_btn.clicked.connect(self.start_gateway)
        self.stop_btn = QPushButton("STOP & RESTORE"); self.stop_btn.setObjectName("DangerButton"); self.stop_btn.clicked.connect(self.stop_gateway)
        self.copy_btn = QPushButton("COPY DEVICE SETTINGS"); self.copy_btn.setObjectName("SecondaryButton"); self.copy_btn.clicked.connect(self.copy_settings)
        actions.addWidget(self.start_btn, 2); actions.addWidget(self.stop_btn, 1); actions.addWidget(self.copy_btn, 1)
        body_layout.addLayout(actions)

        log_panel = GlowPanel(GREEN)
        log_layout = QVBoxLayout(log_panel); log_layout.setContentsMargins(20, 14, 20, 18); log_layout.setSpacing(8)
        activity_header, self.activity_title, self.activity_hint = self.section("", "")
        log_layout.addWidget(activity_header)
        self.log_box = QTextEdit(); self.log_box.setReadOnly(True); self.log_box.setMaximumHeight(130); self.log_box.setObjectName("Log")
        log_layout.addWidget(self.log_box)
        body_layout.addWidget(log_panel, 1)

    @staticmethod
    def field_label(text: str) -> QLabel:
        label = QLabel(text); label.setObjectName("TinyLabel"); return label

    @staticmethod
    def section(title: str, subtitle: str) -> tuple[QWidget, QLabel, QLabel]:
        widget = QWidget(); layout = QVBoxLayout(widget); layout.setContentsMargins(0, 0, 0, 0); layout.setSpacing(2)
        a = QLabel(title); a.setObjectName("SectionTitle")
        b = QLabel(subtitle); b.setObjectName("Hint")
        layout.addWidget(a); layout.addWidget(b); return widget, a, b

    def t(self, key: str) -> str:
        return TRANSLATIONS[self.language].get(key, key)

    def toggle_language(self) -> None:
        self.language = "fa" if self.language == "en" else "en"
        self.settings.setValue("language", self.language)
        self.apply_language()
        self.apply_style()

    def set_device_category(self, category: str) -> None:
        if category == self.device_category:
            self.tv_tab.setChecked(category == "tv")
            self.mobile_tab.setChecked(category == "mobile")
            return
        self.device_category = category
        self.device_profile_id = DEVICE_PROFILES[category][0]["id"]
        self.settings.setValue("device_category", category)
        self.settings.setValue("device_profile", self.device_profile_id)
        self.populate_device_profiles()

    def populate_device_profiles(self) -> None:
        profiles = DEVICE_PROFILES[self.device_category]
        valid_ids = {profile["id"] for profile in profiles}
        if self.device_profile_id not in valid_ids:
            self.device_profile_id = profiles[0]["id"]
        self.tv_tab.setChecked(self.device_category == "tv")
        self.mobile_tab.setChecked(self.device_category == "mobile")
        self.device_combo.blockSignals(True)
        self.device_combo.clear()
        for profile in profiles:
            self.device_combo.addItem(profile["fa" if self.language == "fa" else "en"], profile["id"])
        index = self.device_combo.findData(self.device_profile_id)
        self.device_combo.setCurrentIndex(max(index, 0))
        self.device_combo.blockSignals(False)
        self.render_device_profile()

    def device_profile_changed(self, index: int) -> None:
        profile_id = self.device_combo.itemData(index) if index >= 0 else None
        if not profile_id:
            return
        self.device_profile_id = str(profile_id)
        self.settings.setValue("device_profile", self.device_profile_id)
        self.render_device_profile()

    def current_device_profile(self) -> dict:
        profiles = DEVICE_PROFILES[self.device_category]
        return next((profile for profile in profiles if profile["id"] == self.device_profile_id), profiles[0])

    @staticmethod
    def mask_to_prefix(mask: str) -> str:
        try:
            return str(sum(bin(int(part)).count("1") for part in mask.split(".")))
        except (TypeError, ValueError):
            return "-"

    def render_device_profile(self) -> None:
        profile = self.current_device_profile()
        self.network_values["prefix"] = self.mask_to_prefix(self.network_values.get("mask", "-"))
        boxes = (self.tv_ip, self.mask, self.gateway, self.dns)
        for box, (label, key) in zip(boxes, profile["fields"]):
            box.set_title(label)
            box.set_value(self.network_values.get(key, "-"))
        device_name = profile["fa" if self.language == "fa" else "en"]
        self.device_guide.setText(f"Settings path — {profile['guide']}")
        self.device_guide.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.device_guide.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

    def apply_language(self) -> None:
        fa = self.language == "fa"
        self.setWindowTitle("درگاه UAC" if fa else "UAC Gateway")
        self.app_subtitle.setText(self.t("subtitle"))
        self.lang_btn.setText(self.t("language"))
        self.routing_title.setText(self.t("routing_title"))
        self.routing_hint.setText(self.t("routing_hint"))
        self.vpn_field_label.setText(self.t("vpn_label"))
        self.lan_field_label.setText(self.t("lan_label"))
        self.refresh_btn.setText(self.t("detect"))
        self.nat_check.setText(self.t("nat"))
        self.kill_check.setText(self.t("kill"))
        self.device_title.setText(self.t("device_title"))
        self.device_hint.setText(self.t("device_hint"))
        self.tv_ip.set_title(self.t("device_ip"))
        self.mask.set_title(self.t("mask"))
        self.gateway.set_title(self.t("gateway"))
        self.dns.set_title(self.t("dns"))
        self.start_btn.setText(self.t("start"))
        self.stop_btn.setText(self.t("stop"))
        self.copy_btn.setText(self.t("copy"))
        self.activity_title.setText(self.t("activity"))
        self.activity_hint.setText(self.t("activity_hint"))
        self.tv_tab.setText(self.t("television"))
        self.mobile_tab.setText(self.t("mobile"))
        self.device_model_label.setText(self.t("device_model"))
        self.populate_device_profiles()
        # Keep the physical grid stable in both languages; only text direction changes.
        self.body.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.titlebar.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.vpn_combo.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.lan_combo.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.log_box.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.app_title.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        text_alignment = Qt.AlignmentFlag.AlignRight if fa else Qt.AlignmentFlag.AlignLeft
        for label in (self.routing_title, self.routing_hint, self.vpn_field_label, self.lan_field_label,
                      self.device_title, self.device_hint, self.activity_title, self.activity_hint):
            label.setAlignment(text_alignment | Qt.AlignmentFlag.AlignVCenter)
            label.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        self.app_subtitle.setAlignment(text_alignment)
        self.app_subtitle.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        for check in (self.nat_check, self.kill_check):
            check.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
        self.options_widget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        for box in (self.tv_ip, self.mask, self.gateway, self.dns):
            box.label.setAlignment(text_alignment)
            box.label.setLayoutDirection(Qt.LayoutDirection.RightToLeft if fa else Qt.LayoutDirection.LeftToRight)
            box.value.setAlignment(Qt.AlignmentFlag.AlignRight if fa else Qt.AlignmentFlag.AlignLeft)
        self.device_model_label.setAlignment(text_alignment | Qt.AlignmentFlag.AlignVCenter)
        active = bool(gateway_state())
        self.status.setText(("●  " + self.t("active")) if active else ("●  " + self.t("offline")))

    def apply_style(self) -> None:
        font_family = FA_FONT if self.language == "fa" else EN_FONT
        QApplication.instance().setFont(QFont(font_family, 10))
        self.setStyleSheet(f"""
            * {{ font-family: '{font_family}'; color: {TEXT}; outline: none; }}
            #Shell {{ background: {BG}; border: 1px solid #23466e; border-radius: 22px; }}
            #TitleBar {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #07162b,stop:.58 #091329,stop:1 #081124); border-top-left-radius: 22px; border-top-right-radius: 22px; border-bottom: 1px solid #1a385c; }}
            #AppTitle {{ font-family: '{EN_FONT}'; font-size: 19px; font-weight: 800; letter-spacing: 2.4px; color: #ffffff; }}
            #Subtitle {{ color: #91b4dd; font-size: 11px; padding-top: 2px; }}
            #Hint {{ color: {MUTED}; font-size: 11px; }}
            #StatusOff, #StatusOn {{ padding: 9px 16px; border-radius: 16px; font-weight: 700; min-width: 112px; }}
            #StatusOff {{ color: #9aabc5; background: #0b172c; border: 1px solid #294666; }}
            #StatusOn {{ color: {GREEN}; background: #082821; border: 1px solid #1b9872; }}
            #LanguageButton {{ min-height: 32px; padding: 3px 15px; border-radius: 16px; color: #d6f7ff; background: #10223b; border: 1px solid #2f6187; }}
            #LanguageButton:hover {{ color: #ffffff; border-color: {CYAN}; background: #143052; }}
            #WindowButton, #CloseButton {{ padding: 0; border: 1px solid transparent; border-radius: 10px; background: transparent; }}
            #WindowButton:hover {{ background: #152a47; border-color: #294b70; }}
            #CloseButton:hover {{ background: #b83e57; border-color: #e06378; }}
            #GlowPanel {{ background: transparent; border: 0; }}
            #SectionTitle {{ font-weight: 800; font-size: 14px; letter-spacing: .7px; color: #f9fbff; }}
            #TinyLabel {{ color: #7ea5d4; font-size: 10px; font-weight: 700; letter-spacing: .8px; }}
            QComboBox {{ background: #071326; border: 1px solid #28517e; border-radius: 12px; padding: 11px 14px; min-height: 24px; selection-background-color: #2058a1; }}
            QComboBox:hover, QComboBox:focus {{ border-color: {CYAN}; background: #091a31; }}
            QComboBox::drop-down {{ border: 0; width: 30px; }}
            QComboBox QAbstractItemView {{ background: #09162a; selection-background-color: #2058a1; border: 1px solid #2c527c; padding: 6px; }}
            QCheckBox {{ color: #c1d0e8; spacing: 9px; padding: 4px 2px; min-height: 20px; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border-radius: 5px; border: 1px solid #3b628f; background: #071326; }}
            QCheckBox::indicator:hover {{ border-color: {CYAN}; }}
            QCheckBox::indicator:checked {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 {BLUE},stop:1 {CYAN}); border-color: #7beaff; }}
            #ValueBox {{ background: #071326; border: 1px solid #22466f; border-radius: 14px; }}
            #ValueBox:hover {{ border-color: #3579a8; background: #09182d; }}
            #ValueText {{ font-family: '{EN_FONT}'; font-size: 16px; font-weight: 750; color: #e9fbff; }}
            QPushButton {{ border-radius: 12px; padding: 12px 17px; font-weight: 700; min-height: 22px; }}
            #DeviceSelector {{ background: #061020; border: 1px solid #1d3d61; border-radius: 13px; }}
            #DeviceTab {{ min-width: 92px; padding: 8px 14px; min-height: 20px; color: #91a9c8; background: transparent; border: 1px solid transparent; border-radius: 9px; }}
            #DeviceTab:hover {{ color: #eafaff; background: #10233d; }}
            #DeviceTab:checked {{ color: #ffffff; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #315ff0,stop:1 #159ec6); border-color: #5cd9ef; }}
            #DeviceCombo {{ min-height: 20px; padding: 8px 12px; border-radius: 9px; background: #0a1930; }}
            #DeviceGuide {{ color: #8fa9ca; background: #071223; border-left: 3px solid #2fcdeb; border-radius: 7px; padding: 8px 12px; font-size: 10px; }}
            #PrimaryButton {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #4268ff,stop:.55 #168ff4,stop:1 #16c8df); border: 1px solid #65dfff; color: white; }}
            #PrimaryButton:hover {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #5479ff,stop:1 #25d8e9); }}
            #PrimaryButton:pressed {{ background: #245ed4; }}
            #DangerButton {{ background: #27111e; border: 1px solid #a63b55; color: #ff91a3; }}
            #DangerButton:hover {{ background: #46192b; border-color: #ff6680; }}
            #SecondaryButton {{ background: #0c1b31; border: 1px solid #315a84; color: #b9e6ff; }}
            #SecondaryButton:hover {{ border-color: {CYAN}; background: #102743; color: white; }}
            QPushButton:disabled {{ color: #64758f; background: #0b1321; border-color: #1d2d43; }}
            #Log {{ background: #040b16; border: 1px solid #1d4566; border-radius: 12px; padding: 10px; color: #73ebc2; font-family: Consolas; font-size: 10px; selection-background-color: #155c65; }}
            #LoadingBar {{ padding: 0; border: 0; background: #11243c; border-radius: 2px; }}
            #LoadingBar::chunk {{ border-radius: 2px; background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 {BLUE},stop:1 {CYAN}); }}
            #DialogShell {{ background: #081426; border: 1px solid #2b5682; border-radius: 18px; }}
            #DialogTitle {{ color: #ffffff; font-size: 16px; font-weight: 800; }}
            #DialogValues {{ background: #050d1a; border: 1px solid #1d4165; border-radius: 12px; }}
            #DialogLabel {{ color: #8ba9cd; font-size: 11px; font-weight: 650; }}
            #DialogValue {{ color: #effaff; font-family: '{EN_FONT}'; font-size: 14px; font-weight: 750; }}
            QScrollBar:vertical {{ background: transparent; width: 8px; margin: 3px; }}
            QScrollBar::handle:vertical {{ background: #31516f; border-radius: 4px; min-height: 24px; }}
            QToolTip {{ color: white; background: #0d1d34; border: 1px solid #37648f; padding: 6px; }}
        """)

    def log(self, message: str) -> None:
        self.log_box.append(f"[{time.strftime('%H:%M:%S')}] {message}")

    def set_loading(self, loading: bool, lock_sources: bool = False) -> None:
        self.loading_bar.setVisible(loading)
        if lock_sources:
            self.refresh_btn.setEnabled(not loading)
            self.vpn_combo.setEnabled(not loading)
            self.lan_combo.setEnabled(not loading)
            self.refresh_btn.setText(self.t("loading") if loading else self.t("detect"))
        QApplication.processEvents()

    def adapter_by_index(self, index: int) -> dict | None:
        return next((x for x in self.adapters if int(x["index"]) == index), None)

    def selected(self, combo: QComboBox) -> dict | None:
        value = combo.currentData()
        return self.adapter_by_index(int(value)) if value is not None else None

    def selected_vpn(self) -> dict | None:
        value = self.vpn_combo.currentData()
        return value if isinstance(value, dict) else None

    def refresh_adapters(self) -> None:
        self.set_loading(True, lock_sources=True)
        try:
            old_vpn, old_lan = self.vpn_combo.currentData(), self.lan_combo.currentData()
            network = discover_network()
            self.adapters = network["adapters"]
            self.proxies = network["proxies"]
            self.vpn_combo.blockSignals(True); self.lan_combo.blockSignals(True)
            self.vpn_combo.clear(); self.lan_combo.clear()
            vpn_items = [x for x in self.adapters if (x["vpn_route"] or x["vpn_hint"]) and not (
                "virtualbox" in x["description"].lower() or "host-only" in x["description"].lower()
            )]
            vpn_items.sort(key=lambda x: (not x["vpn_route"], not x["vpn_hint"], x["alias"]))
            lan_items = sorted(self.adapters, key=lambda x: (not (x["hardware"] and x["gateway"]), x["alias"]))
            for item in vpn_items:
                tag = "VPN ROUTE" if item["vpn_route"] else ("VPN" if item["vpn_hint"] else "ADAPTER")
                self.vpn_combo.addItem(f"{item['alias']}  ·  {item['ipv4']}  [{tag}]", {"mode": "adapter", **item})
            for proxy in self.proxies:
                self.vpn_combo.addItem(
                    f"{proxy['label']}  ·  {proxy['owner_name']}  [PROXY → TUN]",
                    proxy,
                )
            if not vpn_items and not self.proxies:
                self.vpn_combo.addItem("No active VPN or SOCKS5 proxy detected", None)
            for item in lan_items:
                if item["hardware"] or item["gateway"]:
                    self.lan_combo.addItem(f"{item['alias']}  ·  {item['ipv4']}", item["index"])
            self.restore_combo(self.vpn_combo, old_vpn)
            self.restore_combo(self.lan_combo, old_lan)
            self.vpn_combo.blockSignals(False); self.lan_combo.blockSignals(False)
            self.log(f"Detected {len(vpn_items)} VPN tunnel(s) and {len(self.proxies)} SOCKS5 proxy source(s).")
            self.update_preview()
        except Exception as exc:
            self.log(f"Discovery failed: {exc}")
            QMessageBox.critical(self, "UAC Gateway", str(exc))
        finally:
            self.set_loading(False, lock_sources=True)

    @staticmethod
    def restore_combo(combo: QComboBox, previous) -> None:
        if previous is not None:
            index = combo.findData(previous)
            if index >= 0: combo.setCurrentIndex(index); return
        if combo.count(): combo.setCurrentIndex(0)

    def update_preview(self) -> None:
        lan = self.selected(self.lan_combo)
        if not lan: return
        parts = lan["ipv4"].split(".")
        tv = ".".join(parts[:3] + ["200"]) if len(parts) == 4 else "-"
        mask = self.prefix_mask(int(lan["prefix"]))
        self.network_values.update({"ip": tv, "mask": mask, "prefix": str(lan["prefix"]), "gateway": lan["ipv4"], "dns": "9.9.9.9"})
        self.render_device_profile()

    @staticmethod
    def prefix_mask(prefix: int) -> str:
        value = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix else 0
        return ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))

    def start_gateway(self) -> None:
        vpn, lan = self.selected_vpn(), self.selected(self.lan_combo)
        if not vpn or not lan:
            QMessageBox.warning(self, "UAC Gateway", self.t("select_both")); return
        if vpn.get("mode") == "adapter" and vpn["index"] == lan["index"]:
            QMessageBox.warning(self, "UAC Gateway", self.t("different")); return
        config = {
            "mode": vpn.get("mode", "adapter"), "vpn_index": vpn.get("index", 0), "lan_index": lan["index"],
            "use_nat": self.nat_check.isChecked(), "kill_switch": self.kill_check.isChecked(),
        }
        if vpn.get("mode") == "proxy":
            config.update({"proxy_host": vpn["host"], "proxy_port": vpn["port"], "proxy_owner_pid": vpn.get("owner_pid", 0)})
        try:
            launch("start", config); self.pending_action = "start"; self.pending_since = time.time()
            self.set_loading(True)
            source_name = vpn.get("alias") or vpn.get("label")
            self.log(f"Starting gateway: {lan['alias']} → {source_name}. Confirm the UAC prompt.")
        except Exception as exc: QMessageBox.critical(self, "UAC Gateway", str(exc))

    def stop_gateway(self) -> None:
        try:
            launch("stop"); self.pending_action = "stop"; self.pending_since = time.time()
            self.set_loading(True)
            self.log("Stopping gateway and restoring Windows settings. Confirm the UAC prompt.")
        except Exception as exc: QMessageBox.critical(self, "UAC Gateway", str(exc))

    def tick(self) -> None:
        state = gateway_state()
        active = bool(state)
        self.status.setText(("●  " + self.t("active")) if active else ("●  " + self.t("offline")))
        self.status.setObjectName("StatusOn" if active else "StatusOff")
        self.status.style().unpolish(self.status); self.status.style().polish(self.status)
        self.start_btn.setEnabled(not active and self.pending_action is None)
        self.stop_btn.setEnabled(active and self.pending_action is None)
        if state:
            mask = str(state.get("subnet_mask", "-"))
            self.network_values.update({
                "ip": str(state.get("tv_ip", "-")), "mask": mask, "prefix": self.mask_to_prefix(mask),
                "gateway": str(state.get("lan_ip", "-")), "dns": str(state.get("dns1", "-")),
            })
            self.render_device_profile()
        if not self.pending_action: return
        result = gateway_result()
        if result and RESULT_PATH.stat().st_mtime >= self.pending_since - 1:
            action = self.pending_action; self.pending_action = None
            self.set_loading(False)
            if result.get("ok"):
                self.log(result.get("message", "Done."))
                if action == "start":
                    QTimer.singleShot(300, self.show_tv_settings)
            else:
                error = str(result.get("message") or "Gateway operation failed.")
                self.log(error); QMessageBox.critical(self, "UAC Gateway", error)
        elif time.time() - self.pending_since > 45:
            self.pending_action = None; self.set_loading(False); self.log("Operation timed out or UAC was cancelled.")

    def settings_text(self) -> str:
        profile = self.current_device_profile()
        device_name = profile["fa" if self.language == "fa" else "en"]
        lines = [device_name]
        lines.extend(f"{label}: {self.network_values.get(key, '-')}" for label, key in profile["fields"])
        state = gateway_state() or {}
        if state.get("dns2"):
            lines.append(f"Backup DNS: {state['dns2']}")
        return "\n".join(lines)

    def show_tv_settings(self) -> None:
        state = gateway_state() or {}
        fa = self.language == "fa"
        profile = self.current_device_profile()
        values = [(label, str(self.network_values.get(key, "-"))) for label, key in profile["fields"]]
        backup = state.get("dns2")
        if backup:
            values.append(("دی‌ان‌اس پشتیبان" if fa else "Backup DNS", str(backup)))
        device_name = profile["fa" if fa else "en"]
        DeviceSettingsDialog(self, f"{self.t('tv_settings')} — {device_name}", values, self.t("close"), fa).exec()

    def copy_settings(self) -> None:
        QApplication.clipboard().setText(self.settings_text())
        self.log(self.t("copied"))

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 80:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event) -> None:
        if self.drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event) -> None:
        self.drag_pos = None


def load_app_fonts() -> None:
    font_dir = ROOT / "assets" / "fonts"
    for name in ("Vazirmatn-Regular.ttf", "Vazirmatn-SemiBold.ttf"):
        path = font_dir / name
        if path.exists():
            QFontDatabase.addApplicationFont(str(path))


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName("UAC Gateway")
    load_app_fonts()
    window = UacGateway(); window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
