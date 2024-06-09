from PySide6.QtWidgets import QApplication


class AppContext:
    @staticmethod
    def get(property_name):
        if hasattr(QApplication.instance(), property_name):
            return getattr(QApplication.instance(), property_name)

    @staticmethod
    def set(property_name, obj):
        setattr(QApplication.instance(), property_name, obj)