#
# PyQt6 GUI 
#


# imports for main GUI
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QMessageBox,
    QDialog, QLabel, QLineEdit, QComboBox, QFormLayout, QHBoxLayout    
)
import sys

# imports for view all phones GUI
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox
)

from PyQt6.QtGui import QFont

from PyQt6.QtCore import Qt

# import existing functions from phone.py
from phone import addPhone, updatePhone, deletePhone, viewPhone, viewPhones


# ################################################
# sub GUIs
# ################################################

# add a phone

# NEXT:  To be completed next weekend 1/11/26

class AddPhoneDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a Phone")
        self.setGeometry(400, 400, 500, 400)
        
        # Create form layout
        layout = QFormLayout()
        
        # Brand combo box
        self.brand_combo = QComboBox()
        self.brand_combo.addItems(["Samsung", "Apple", "Other"])
        layout.addRow("Brand:", self.brand_combo)
        
        # Model input
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("e.g., S22, iPhone 14, Other")
        layout.addRow("Model:", self.model_input)
        
        # OS combo box
        self.os_combo = QComboBox()
        self.os_combo.addItems(["Android", "iOS"])
        layout.addRow("OS:", self.os_combo)
        
        # OS Version combo box
        self.os_version_combo = QComboBox()
        self.os_version_combo.addItems(["13", "14", "15", "16", "17", "18", "26"])
        layout.addRow("OS Version:", self.os_version_combo)
        
        # Serial Number input
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("e.g., XX112233YY-1234")
        layout.addRow("Serial Number:", self.serial_input)
        
        # IMEI input
        self.imei_input = QLineEdit()
        self.imei_input.setPlaceholderText("e.g., 998877665544332211-1234")
        layout.addRow("IMEI:", self.imei_input)
        
        # Status combo box
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ACTIVE", "UNASSIGNED", "RETIRED"])
        layout.addRow("Status:", self.status_combo)
        
        # Workstation input
        self.workstation_input = QLineEdit()
        self.workstation_input.setPlaceholderText("e.g., WS1234")
        layout.addRow("Workstation:", self.workstation_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        
        btn_save.clicked.connect(self.save_phone)
        btn_cancel.clicked.connect(self.reject)
        
        button_layout.addWidget(btn_save)
        button_layout.addWidget(btn_cancel)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    def save_phone(self):
        """Validate and save the phone"""
        from phone import (
            Phone, validateBrand, validateModel, validateOSName,
            validateOSVersion, validateSerialNumber, validateIMEI,
            validateStatus, validateWorkstation, session
        )
        
        # Get values
        brand_text = self.brand_combo.currentText()
        model_text = self.model_input.text().strip()
        os_text = self.os_combo.currentText()
        os_version_text = self.os_version_combo.currentText()
        serial_text = self.serial_input.text().strip()
        imei_text = self.imei_input.text().strip()
        status_text = self.status_combo.currentText()
        workstation_text = self.workstation_input.text().strip()
        
        # Validate brand
        brand = validateBrand(brand_text[0])  # Pass first letter (S, A, O)
        if not brand:
            QMessageBox.warning(self, "Error", "Invalid brand!")
            return
        
        # Validate model
        model = validateModel(model_text)
        if not model:
            QMessageBox.warning(self, "Error", "Invalid model!")
            return
        
        # Validate OS
        os_name = validateOSName(os_text[0])  # Pass first letter (A, I)
        if not os_name:
            QMessageBox.warning(self, "Error", "Invalid OS!")
            return
        
        # Validate OS Version
        os_version = validateOSVersion(os_version_text)
        if not os_version:
            QMessageBox.warning(self, "Error", "Invalid OS version!")
            return
        
        # Check if serial number already exists
        if not serial_text:
            QMessageBox.warning(self, "Error", "Serial number is required!")
            return
        if validateSerialNumber(serial_text.upper()):
            QMessageBox.warning(self, "Error", "Serial number already exists!")
            return
        
        # Check if IMEI already exists
        if not imei_text:
            QMessageBox.warning(self, "Error", "IMEI is required!")
            return
        if validateIMEI(imei_text.upper()):
            QMessageBox.warning(self, "Error", "IMEI already exists!")
            return
        
        # Validate status
        status = validateStatus(status_text[0])  # Pass first letter (A, U, R)
        if not status:
            QMessageBox.warning(self, "Error", "Invalid status!")
            return
        
        # Handle workstation based on status
        if status == "ACTIVE":
            if not workstation_text:
                QMessageBox.warning(self, "Error", "Workstation required for ACTIVE status!")
                return
            if not validateWorkstation(workstation_text.upper()):
                QMessageBox.warning(self, "Error", "Invalid workstation!")
                return
            workstation = workstation_text.upper()
        else:
            workstation = "UNASSIGNED"
        
        # Create the phone
        try:
            phone = Phone(
                brand=brand,
                model=model,
                os=os_name,
                os_version=str(os_version),
                serial_number=serial_text.upper(),
                imei=imei_text.upper(),
                status=status,
                workstation=workstation
            )
            
            session.add(phone)
            session.commit()
            
            QMessageBox.information(self, "Success", f"Phone {brand} {model} added successfully!")
            self.accept()  # Close dialog with success
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Failed to add phone: {e}")



# GUI with the bottons on top and the results on the bottom frame
class MainWindow(QWidget):
    # init
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workstation Phone Management GUI")
        self.setGeometry(300, 300, 400, 200)

        # track active dialog boxes (windows)
        self.active_dialog = None

        main_layout = QVBoxLayout()

        # --- TOP BUTTON BAR ---
        button_bar = QVBoxLayout()
        button_bar.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignTop)        

        btn_add = QPushButton("Add a Phone")
        btn_update = QPushButton("Update a Phone")
        btn_delete = QPushButton("Delete a Phone")
        btn_view = QPushButton("View a Phone")
        btn_view_all = QPushButton("View All Phones")
        btn_exit = QPushButton("Exit")

        # set the max width for the buttons
        buttons = [btn_add, btn_update, btn_delete, btn_view, btn_view_all, btn_exit]
        for b in buttons:
            b.setMaximumWidth(200)
        
        # wiring
        btn_add.clicked.connect(self.show_add_phone)
        btn_update.clicked.connect(self.show_update_phone)
        btn_delete.clicked.connect(self.show_delete_phone)
        btn_view.clicked.connect(self.show_view_phone)
        btn_view_all.clicked.connect(self.show_view_all_phones)
        btn_exit.clicked.connect(self.close)

        # add buttons
        button_bar.addWidget(btn_add)
        button_bar.addWidget(btn_update)
        button_bar.addWidget(btn_delete)
        button_bar.addWidget(btn_view)
        button_bar.addWidget(btn_view_all)
        button_bar.addWidget(btn_exit)

        main_layout.addLayout(button_bar)

        # --- BOTTOM CONTENT AREA ---
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)

        main_layout.addWidget(self.content_area)

        self.setLayout(main_layout)

    # show add a phone
    def show_add_phone(self):
        QMessageBox.information(self, "Add Phone", "Add Phone clicked!")
    # show update a phone
    def show_update_phone(self):
        QMessageBox.information(self, "Update Phone", "Update Phone clicked!")
    # show delete a phone
    def show_delete_phone(self):
        QMessageBox.information(self, "Delete Phone", "Delete Phone clicked!")
    # show view a phone
    def show_view_phone(self):
        QMessageBox.information(self, "View Phone", "View Phone clicked!")
    # show view all phones
    def show_view_all_phones(self):
        QMessageBox.information(self, "View All", "View All Phones clicked!")
# main

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())