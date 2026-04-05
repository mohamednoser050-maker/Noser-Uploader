from kivy.lang import Builder
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import OneLineListItem
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
import json
import os

KV = '''
MDScreen:
    md_bg_color: self.theme_cls.bg_dark

    MDBoxLayout:
        orientation: "vertical"
        padding: "16dp"
        spacing: "16dp"

        MDTopAppBar:
            title: "Noser Image Uploader"
            elevation: 4

        ScrollView:
            MDBoxLayout:
                orientation: "vertical"
                adaptive_height: True
                padding: "16dp"
                spacing: "20dp"

                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "10dp"
                    adaptive_height: True
                    elevation: 2
                    radius: [15, ]

                    MDLabel:
                        text: "إعدادات التليجرام"
                        font_style: "H6"
                        halign: "right"
                    
                    MDTextField:
                        id: bot_token
                        hint_text: "Telegram Bot Token"
                        mode: "rectangle"

                    MDTextField:
                        id: chat_id
                        hint_text: "Telegram Channel ID"
                        mode: "rectangle"

                    MDRaisedButton:
                        text: "حفظ الإعدادات"
                        pos_hint: {"center_x": .5}
                        on_release: app.save_settings()

                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    spacing: "15dp"
                    adaptive_height: True
                    elevation: 2
                    radius: [15, ]

                    MDLabel:
                        text: "حالة العمل"
                        font_style: "H6"
                        halign: "right"

                    MDProgressBar:
                        id: progress_bar
                        value: app.progress_value
                        max: 100

                    MDLabel:
                        text: app.status_text
                        halign: "center"

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: "10dp"
                        
                        MDRaisedButton:
                            text: "ابدأ النسخ والإرسال"
                            md_bg_color: "green"
                            on_release: app.start_service()

                        MDRaisedButton:
                            text: "إيقاف"
                            md_bg_color: "red"
                            on_release: app.stop_service()

                    MDRaisedButton:
                        text: "طلب استثناء البطارية"
                        pos_hint: {"center_x": .5}
                        on_release: app.request_battery_optimization()

                MDCard:
                    orientation: "vertical"
                    padding: "16dp"
                    height: "250dp"
                    size_hint_y: None
                    elevation: 2
                    radius: [15, ]

                    MDLabel:
                        text: "سجل العمليات"
                        font_style: "Subtitle1"
                        halign: "right"

                    ScrollView:
                        MDList:
                            id: log_list
'''

class NoserApp(MDApp):
    status_text = StringProperty("بانتظار البدء...")
    progress_value = NumericProperty(0)

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Dark"
        self.config_file = os.path.join(self.user_data_dir, 'config.json')
        return Builder.load_string(KV)

    def on_start(self):
        self.load_settings()
        self.request_permissions()
        Clock.schedule_interval(self.check_service_status, 1)

    def request_permissions(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            perms = [
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.POST_NOTIFICATIONS,
                Permission.FOREGROUND_SERVICE
            ]
            request_permissions(perms)

    def request_battery_optimization(self):
        if platform == 'android':
            from jnius import autoclass
            from android import api_version
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            currentActivity = PythonActivity.mActivity
            Context = autoclass('android.content.Context')
            Intent = autoclass('android.content.Intent')
            Settings = autoclass('android.provider.Settings')
            Uri = autoclass('android.net.Uri')
            
            pm = currentActivity.getSystemService(Context.POWER_SERVICE)
            if not pm.isIgnoringBatteryOptimizations(currentActivity.getPackageName()):
                intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS)
                intent.setData(Uri.parse("package:" + currentActivity.getPackageName()))
                currentActivity.startActivity(intent)

    def load_settings(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                self.root.ids.bot_token.text = data.get('token', '')
                self.root.ids.chat_id.text = data.get('chat_id', '')

    def save_settings(self):
        data = {
            'token': self.root.ids.bot_token.text,
            'chat_id': self.root.ids.chat_id.text
        }
        with open(self.config_file, 'w') as f:
            json.dump(data, f)
        self.add_log("تم حفظ الإعدادات بنجاح")

    def add_log(self, message):
        self.root.ids.log_list.add_widget(
            OneLineListItem(text=message)
        )

    def start_service(self):
        if platform == 'android':
            from android import service
            self.save_settings()
            service.start_service("NoserService", "service.py", "Noser Background Service")
            self.add_log("بدء خدمة الخلفية...")
        else:
            self.add_log("التشغيل متاح فقط على أندرويد")

    def stop_service(self):
        if platform == 'android':
            from android import service
            service.stop_service()
            self.add_log("إيقاف خدمة الخلفية")

    def check_service_status(self, dt):
        # Update progress and status from shared file/memory
        status_file = os.path.join(self.user_data_dir, 'status.json')
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r') as f:
                    data = json.load(f)
                    self.status_text = data.get('status', self.status_text)
                    self.progress_value = data.get('progress', self.progress_value)
            except:
                pass

if __name__ == "__main__":
    NoserApp().run()
