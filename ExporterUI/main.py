import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QComboBox, 
                             QLineEdit, QTextEdit, QFileDialog, QMessageBox,
                             QGroupBox, QTabWidget, QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont

from max_interface import MaxScriptInterface
from exporter import Exporter
from unreal_importer import UnrealImporter
import config

class ExportWorker(QThread):
    finished = pyqtSignal(object, str) 
    error = pyqtSignal(str)           

    def __init__(self, interface, exporter, obj_name, path, do_lods, do_nanite):
        super().__init__()
        self.interface = interface
        self.exporter = exporter
        self.obj_name = obj_name
        self.path = path
        self.do_lods = do_lods
        self.do_nanite = do_nanite

    def run(self):
        try:
            stats = self.interface.get_object_stats(self.obj_name)
            
            self.interface.export_fbx(self.obj_name, self.path, self.do_lods, self.do_nanite)
            
            json_path = self.path.replace('.fbx', '.json')
            
            self.finished.emit(stats, json_path)
        except Exception as e:
            self.error.emit(str(e))

class PipelineUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.max_interface = MaxScriptInterface()
        self.exporter = Exporter()
        self.importer = UnrealImporter()
        self.init_ui()
        self.try_connect_to_max()
    
    def init_ui(self):
        self.setWindowTitle("3ds Max to Unreal Pipeline (Pro)")
        self.setGeometry(100, 100, 900, 750)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        title = QLabel("3ds Max -> Unreal Engine Pipeline")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        tabs = QTabWidget()
        self.setup_export_tab(tabs)
        self.setup_import_tab(tabs)
        main_layout.addWidget(tabs)
        
        console_group = QGroupBox("Console Log")
        console_layout = QVBoxLayout()
        self.console_text = QTextEdit()
        self.console_text.setReadOnly(True)
        self.console_text.setMaximumHeight(120)
        console_layout.addWidget(self.console_text)
        console_group.setLayout(console_layout)
        main_layout.addWidget(console_group)

    def setup_export_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        self.status_label = QLabel("Status: Checking...")
        self.status_label.setFont(QFont('Arial', 10, QFont.Bold))
        layout.addWidget(self.status_label)
        
        sel_group = QGroupBox("1. Select Object from Scene")
        sel_layout = QHBoxLayout()
        self.obj_combo = QComboBox()
        self.obj_combo.setMinimumWidth(300)
        self.refresh_btn = QPushButton("Refresh List")
        self.refresh_btn.clicked.connect(self.connect_to_max)
        sel_layout.addWidget(QLabel("Object:"))
        sel_layout.addWidget(self.obj_combo)
        sel_layout.addWidget(self.refresh_btn)
        sel_group.setLayout(sel_layout)
        layout.addWidget(sel_group)
        
        path_group = QGroupBox("2. Export Settings")
        path_layout = QVBoxLayout()
        file_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select where to save the FBX...")
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_export_path)
        file_layout.addWidget(self.path_input)
        file_layout.addWidget(self.browse_btn)
        
        self.lod_checkbox = QCheckBox("Auto-Generate LODs (Levels of Detail)")
        self.lod_checkbox.setChecked(True)
        self.lod_checkbox.setStyleSheet("font-weight: bold; color: #0078d4;")
        self.lod_checkbox.setToolTip("Generates 50%, 25%, and 12% reduction versions.")
        self.nanite_checkbox = QCheckBox("Enable Nanite Support (UE5)")
        self.nanite_checkbox.setChecked(False)
        self.nanite_checkbox.setStyleSheet("font-weight: bold; color: #e83e8c;")
        self.nanite_checkbox.setToolTip("Enables Virtualized Geometry. Note: Nanite meshes typically do not require standard LODs.")

        path_layout.addLayout(file_layout)
        path_layout.addWidget(self.lod_checkbox)
        path_layout.addWidget(self.nanite_checkbox)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        self.export_btn = QPushButton("EXPORT ASSET")
        self.export_btn.setMinimumHeight(50)
        self.export_btn.setStyleSheet("""
            QPushButton { background-color: #0078d4; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; }
            QPushButton:hover { background-color: #005a9e; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.export_btn.clicked.connect(self.export_asset)
        layout.addWidget(self.export_btn)
        
        layout.addStretch()
        tabs.addTab(tab, "Export from Max")

    def setup_import_tab(self, tabs):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        info = QLabel("Select the exported FBX to generate the Unreal Python import script.")
        layout.addWidget(info)
        self.fbx_input = QLineEdit()
        self.fbx_input.setPlaceholderText("Path to exported FBX...")
        layout.addWidget(self.fbx_input)
        
        self.gen_btn = QPushButton("GENERATE UNREAL IMPORT SCRIPT")
        self.gen_btn.setMinimumHeight(50)
        self.gen_btn.setStyleSheet("""
            QPushButton { background-color: #28a745; color: white; font-weight: bold; font-size: 14px; border-radius: 5px; }
            QPushButton:hover { background-color: #218838; }
        """)
        self.gen_btn.clicked.connect(self.generate_script)
        layout.addWidget(self.gen_btn)
        layout.addStretch()
        tabs.addTab(tab, "Import to Unreal")

    def log(self, msg, color="black"):
        self.console_text.append(f'<span style="color:{color}">{msg}</span>')

    def try_connect_to_max(self):
        self.log("Checking connection...", "gray")
        if self.max_interface.test_connection():
            self.status_label.setText("Status: Connected to 3ds Max")
            self.status_label.setStyleSheet("color: green")
            self.log("Connected to 3ds Max", "green")
            self.load_objects()
        else:
            self.status_label.setText("Status: Not Connected (Is monitor.ms running?)")
            self.status_label.setStyleSheet("color: red")
            self.log("Connection failed. Make sure monitor.ms is running in Max.", "red")

    def connect_to_max(self):
        self.try_connect_to_max()

    def load_objects(self):
        try:
            objs = self.max_interface.get_scene_objects()
            self.obj_combo.clear()
            self.obj_combo.addItems(objs)
            self.log(f"Loaded {len(objs)} objects from scene.", "blue")
        except Exception as e:
            self.log(f"Error loading objects: {e}", "red")

    def browse_export_path(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Export", "", "FBX Files (*.fbx)")
        if path:
            self.path_input.setText(path)

    def export_asset(self):
        obj_name = self.obj_combo.currentText()
        export_path = self.path_input.text()
        do_lods = self.lod_checkbox.isChecked()
        do_nanite = self.nanite_checkbox.isChecked()
        
        if not obj_name:
            QMessageBox.warning(self, "Input Error", "Please select an object.")
            return
        if not export_path:
            QMessageBox.warning(self, "Input Error", "Please select an export path.")
            return
        
        self.export_btn.setEnabled(False)
        self.export_btn.setText("EXPORTING... (Processing...)")
        self.log(f"Starting export for '{obj_name}'...", "blue")
        
        self.worker = ExportWorker(self.max_interface, self.exporter, obj_name, export_path, do_lods, do_nanite)
        self.worker.finished.connect(self.on_export_done)
        self.worker.error.connect(self.on_export_fail)
        self.worker.start()

    def on_export_done(self, stats, json_path):
        self.export_btn.setEnabled(True)
        self.export_btn.setText("EXPORT ASSET")
        self.log("Export Successful!", "green")
        self.log(f"Metadata saved: {json_path}", "black")
        self.fbx_input.setText(self.path_input.text())
        QMessageBox.information(self, "Success", f"Asset exported successfully!")

    def on_export_fail(self, err_msg):
        self.export_btn.setEnabled(True)
        self.export_btn.setText("EXPORT ASSET")
        self.log(f"Export Failed: {err_msg}", "red")
        QMessageBox.critical(self, "Export Failed", f"An error occurred:\n{err_msg}")

    def generate_script(self):
        fbx_path = self.fbx_input.text()
        if not fbx_path or not os.path.exists(fbx_path):
            QMessageBox.warning(self, "Error", "FBX file not found.")
            return
        try:
            script_path = self.importer.save_import_script(fbx_path)
            self.log(f"Unreal script generated: {script_path}", "green")
            QMessageBox.information(self, "Script Generated", 
                f"Python script created successfully!\n\nLocation: {script_path}\n\nRun this script inside Unreal Engine.")
        except Exception as e:
            self.log(f"Script generation failed: {e}", "red")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    window = PipelineUI()
    window.show()
    sys.exit(app.exec_())