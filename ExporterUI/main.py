import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QLineEdit, QTextEdit, QFileDialog, QMessageBox,
                             QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from max_interface import MaxScriptInterface
from exporter import Exporter
import config


class ExporterUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.max_interface = MaxScriptInterface()
        self.exporter = Exporter()
        self.init_ui()
        self.connect_to_max()
    
    def init_ui(self):
        self.setWindowTitle("3ds Max to Unreal - Exporter")
        self.setGeometry(100, 100, 800, 600)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(15)
        title = QLabel("3ds Max Asset Exporter")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.status_label = QLabel("Status: Not connected")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(self.status_label)
        obj_group = QGroupBox("1. Select Object")
        obj_layout = QHBoxLayout()
        self.obj_combo = QComboBox()
        self.obj_combo.setMinimumWidth(400)
        obj_layout.addWidget(QLabel("Object:"))
        obj_layout.addWidget(self.obj_combo)
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_objects)
        obj_layout.addWidget(self.refresh_btn)
        obj_group.setLayout(obj_layout)
        layout.addWidget(obj_group)
        export_group = QGroupBox("2. Export Location")
        export_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select export path...")
        export_layout.addWidget(self.path_input)
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_export_path)
        export_layout.addWidget(self.browse_btn)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        self.export_btn = QPushButton("EXPORT ASSET")
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-size: 14pt;
                font-weight: bold;
                padding: 15px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.export_btn.clicked.connect(self.export_asset)
        self.export_btn.setEnabled(False)
        layout.addWidget(self.export_btn)
        results_group = QGroupBox("Export Results")
        results_layout = QVBoxLayout()
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setMaximumHeight(150)
        results_layout.addWidget(self.results_text)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)
        console_group = QGroupBox("Console Log")
        console_layout = QVBoxLayout()
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setMaximumHeight(150)
        console_layout.addWidget(self.console_text)
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)
    
    def log(self, message, color="black"):
        self.console_text.append(f'<span style="color: {color};">{message}</span>')
    
    def connect_to_max(self):
        self.log("Connecting to 3ds Max...", "blue")
        try:
            if self.max_interface.test_connection():
                self.status_label.setText(f"Status: Connected (Port {config.MAX_LISTENER_PORT})")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
                self.log("Connected successfully", "green")
                self.load_objects()
            else:
                raise Exception("Connection test failed")
        except Exception as e:
            self.status_label.setText("Status: Not connected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.log(f"Connection failed: {str(e)}", "red")
            self.log("Make sure 3ds Max is open with listener running", "orange")
    
    def load_objects(self):
        try:
            objects = self.max_interface.get_scene_objects()
            self.obj_combo.clear()
            self.obj_combo.addItems(objects)
            self.log(f"Loaded {len(objects)} objects from scene", "blue")
        except Exception as e:
            self.log(f"Failed to load objects: {str(e)}", "red")
    
    def refresh_objects(self):
        self.log("Refreshing object list...", "blue")
        self.connect_to_max()
    
    def browse_export_path(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Export Location",
            "",
            "FBX Files (*.fbx)"
        )
        if path:
            self.path_input.setText(path)
            self.export_btn.setEnabled(True)
            self.log(f"Export path set: {path}", "blue")
    
    def export_asset(self):
        object_name = self.obj_combo.currentText()
        export_path = self.path_input.text()
        if not object_name:
            QMessageBox.warning(self, "Error", "Please select an object")
            return
        if not export_path:
            QMessageBox.warning(self, "Error", "Please select export path")
            return
        self.log("=" * 50, "black")
        self.log(f"Starting export: {object_name}", "blue")
        self.results_text.clear()
        try:
            self.log("Getting object statistics...", "blue")
            stats = self.max_interface.get_object_stats(object_name)
            self.log(f"  Polygons: {stats['polygons']:,}", "black")
            self.log(f"  Vertices: {stats['vertices']:,}", "black")
            self.log("Exporting FBX...", "blue")
            self.max_interface.export_fbx(object_name, export_path)
            self.log(f"FBX exported: {export_path}", "green")
            self.log("Creating metadata...", "blue")
            metadata, json_path = self.exporter.create_metadata(
                object_name, stats, export_path
            )
            self.log(f"Metadata saved: {json_path}", "green")
            results = f"""
                EXPORT COMPLETE
                ================

                Asset: {object_name}
                FBX: {export_path}
                JSON: {json_path}

                Geometry:
                   - Polygons: {stats['polygons']:,}
                   - Vertices: {stats['vertices']:,}
                """
            self.results_text.setText(results)
            self.log("=" * 50, "black")
            self.log("EXPORT SUCCESSFUL", "green")
            QMessageBox.information(
                self,
                "Export Complete",
                f"Asset exported successfully!\n\nFBX: {os.path.basename(export_path)}"
            )
        except Exception as e:
            self.log(f"Export failed: {str(e)}", "red")
            self.results_text.setText(f"ERROR:\n{str(e)}")
            QMessageBox.critical(self, "Export Failed", str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ExporterUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
