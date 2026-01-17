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
import phone


# ################################################
# sub GUIs
# ################################################

# TODO:  
# add a phone

# DONE:
# add a phone  1/17/25
# update a phone  1/17/25


# class for add a phone dialog (widget, window)
class AddPhoneDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a Phone")
        self.setGeometry(400, 400, 400, 300)
        
        # create form layout
        layout = QFormLayout()
        
        # brand combo box
        self.brand_combo = QComboBox()
        self.brand_combo.addItems(["Samsung", "Apple", "Other"])
        layout.addRow("Brand:", self.brand_combo)
        
        # model input
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
        
        # serial Number input
        self.serial_input = QLineEdit()
        self.serial_input.setPlaceholderText("e.g., XX112233YY-1234")
        layout.addRow("Serial Number:", self.serial_input)
        
        # IMEI input
        self.imei_input = QLineEdit()
        self.imei_input.setPlaceholderText("e.g., 998877665544332211-1234")
        layout.addRow("IMEI:", self.imei_input)
        
        # status combo box
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ACTIVE", "UNASSIGNED", "RETIRED"])
        self.status_combo.setCurrentText("UNASSIGNED")  # to make sure Status is UNASSIGNED in the GUI by default
        layout.addRow("Status:", self.status_combo)
        
        # workstation input
        self.workstation_input = QLineEdit()
        self.workstation_input.setPlaceholderText("e.g., WS1234")
        layout.addRow("Workstation:", self.workstation_input)
        
        # buttons, aligned horizontally
        button_layout = QHBoxLayout()
        
        btn_save = QPushButton("Save")
        btn_cancel = QPushButton("Cancel")
        
        btn_save.clicked.connect(self.save_phone)
        btn_cancel.clicked.connect(self.reject)

        button_layout.addWidget(btn_cancel)        
        button_layout.addWidget(btn_save)
        
        layout.addRow(button_layout)
        
        self.setLayout(layout)
    
    
    def save_phone(self):
        
        # validate and save the phone
        
        from phone import (
            Phone, validateBrand, validateModel, validateOSName,
            validateOSVersion, validateSerialNumber, validateIMEI,
            validateStatus, validateWorkstation, session
        )
        
        # get values from the widgets
        brand_text = self.brand_combo.currentText()
        model_text = self.model_input.text().strip()
        os_text = self.os_combo.currentText()
        os_version_text = self.os_version_combo.currentText()
        serial_text = self.serial_input.text().strip()
        imei_text = self.imei_input.text().strip()
        status_text = self.status_combo.currentText()
        workstation_text = self.workstation_input.text().strip()
        
        # validate brand
        brand = validateBrand(brand_text[0])  # pass first letter (S, A, O)
        if not brand:
            QMessageBox.warning(self, "Error", "Invalid brand!")
            return
        
        # validate model
        model = validateModel(model_text)
        if not model:
            QMessageBox.warning(self, "Error", "Invalid model!")
            return
        
        # validate OS
        os_name = validateOSName(os_text[0])  # pass first letter (A, I)
        if not os_name:
            QMessageBox.warning(self, "Error", "Invalid OS!")
            return
        
        # validate OS Version
        os_version = validateOSVersion(os_version_text)
        if not os_version:
            QMessageBox.warning(self, "Error", "Invalid OS version!")
            return
        
        # check if serial number already exists
        if not serial_text:
            QMessageBox.warning(self, "Error", "Serial number is required!")
            return
        if validateSerialNumber(serial_text.upper()):
            QMessageBox.warning(self, "Error", "Serial number already exists!")
            return
        
        # check if IMEI already exists
        if not imei_text:
            QMessageBox.warning(self, "Error", "IMEI is required!")
            return
        if validateIMEI(imei_text.upper()):
            QMessageBox.warning(self, "Error", "IMEI already exists!")
            return
        
        # validate status
        status = validateStatus(status_text[0])  # Pass first letter (A, U, R)
        if not status:
            QMessageBox.warning(self, "Error", "Invalid status!")
            return
        
        # handle workstation based on status
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
        
        # create the phone
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
            self.accept()  # close dialog with success
            
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Failed to add phone: {e}")




# class for updating a phone dialog (widget, window)
class UpdatePhoneDialog(QDialog):
    def __init__(self, phone_obj, parent=None):
        super().__init__(parent)
        self.phone = phone_obj  # SQLAlchemy Phone instance

        self.setWindowTitle(f"Update Phone ID {self.phone.id}")
        self.setGeometry(400, 400, 400, 300)

        layout = QFormLayout()

        # Brand
        self.brand_combo = QComboBox()
        self.brand_combo.addItems(["Samsung", "Apple", "Other"])
        self.brand_combo.setCurrentText(self.phone.brand.capitalize())
        layout.addRow("Brand:", self.brand_combo)

        # Model
        self.model_input = QLineEdit(self.phone.model)
        layout.addRow("Model:", self.model_input)

        # OS
        self.os_combo = QComboBox()
        self.os_combo.addItems(["Android", "iOS"])
        self.os_combo.setCurrentText(self.phone.os.capitalize())
        layout.addRow("OS:", self.os_combo)

        # OS Version
        self.os_version_combo = QComboBox()
        self.os_version_combo.addItems(["13", "14", "15", "16", "17", "18", "26"])
        self.os_version_combo.setCurrentText(str(self.phone.os_version))
        layout.addRow("OS Version:", self.os_version_combo)

        # Serial Number
        self.serial_input = QLineEdit(self.phone.serial_number)
        layout.addRow("Serial Number:", self.serial_input)

        # IMEI
        self.imei_input = QLineEdit(self.phone.imei)
        layout.addRow("IMEI:", self.imei_input)

        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["ACTIVE", "UNASSIGNED", "RETIRED"])
        self.status_combo.setCurrentText(self.phone.status)
        layout.addRow("Status:", self.status_combo)

        # Workstation
        self.workstation_input = QLineEdit(self.phone.workstation)
        layout.addRow("Workstation:", self.workstation_input)

        # Buttons
        button_layout = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_save = QPushButton("Save")

        btn_cancel.clicked.connect(self.reject)
        btn_save.clicked.connect(self.save_updates)

        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_save)
        layout.addRow(button_layout)

        self.setLayout(layout)

    def save_updates(self):
        from phone import (
            validateBrand, validateModel, validateOSName, validateOSVersion,
            validateSerialNumber, validateIMEI, validateStatus,
            validateWorkstation, session
        )

        # Brand
        brand = validateBrand(self.brand_combo.currentText()[0])
        if not brand:
            QMessageBox.warning(self, "Error", "Invalid brand")
            return

        # Model
        model = validateModel(self.model_input.text().strip())
        if not model:
            QMessageBox.warning(self, "Error", "Invalid model")
            return

        # OS
        os_name = validateOSName(self.os_combo.currentText()[0])
        if not os_name:
            QMessageBox.warning(self, "Error", "Invalid OS")
            return

        # OS Version
        os_version = validateOSVersion(self.os_version_combo.currentText())
        if not os_version:
            QMessageBox.warning(self, "Error", "Invalid OS version")
            return

        # Serial Number
        serial = self.serial_input.text().strip().upper()
        if not serial:
            QMessageBox.warning(self, "Error", "Serial number required")
            return

        # Only check uniqueness if changed
        if serial != self.phone.serial_number and validateSerialNumber(serial):
            QMessageBox.warning(self, "Error", "Serial number already exists")
            return

        # IMEI
        imei = self.imei_input.text().strip().upper()
        if not imei:
            QMessageBox.warning(self, "Error", "IMEI required")
            return

        if imei != self.phone.imei and validateIMEI(imei):
            QMessageBox.warning(self, "Error", "IMEI already exists")
            return

        # Status
        status = validateStatus(self.status_combo.currentText()[0])
        if not status:
            QMessageBox.warning(self, "Error", "Invalid status")
            return

        # Workstation rules
        ws_text = self.workstation_input.text().strip().upper()

        if status == "ACTIVE":
            if not validateWorkstation(ws_text):
                QMessageBox.warning(self, "Error", "Invalid workstation for ACTIVE status")
                return
            workstation = ws_text
        else:
            workstation = "UNASSIGNED"

        # Apply updates
        self.phone.brand = brand
        self.phone.model = model
        self.phone.os = os_name
        self.phone.os_version = str(os_version)
        self.phone.serial_number = serial
        self.phone.imei = imei
        self.phone.status = status
        self.phone.workstation = workstation

        try:
            session.commit()
            QMessageBox.information(self, "Success", "Phone updated successfully")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Error", f"Failed to update phone: {e}")


# GUI with the bottons on top and the results on the bottom frame
class MainWindow(QWidget):

    # init
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Workstation Phone Management GUI")
        # widened window to fit horizontal buttons and table
        self.setGeometry(300, 300, 800, 600)
    
        # 1. The Master Vertical Layout
        main_layout = QVBoxLayout()
    
        # 2. THE TOP: Horizontal Button Bar
        button_bar = QHBoxLayout()
        # ensure buttons stay at the top of the horizontal layout
        button_bar.setAlignment(Qt.AlignmentFlag.AlignTop) 
    
        btn_add = QPushButton("Add a Phone")
        btn_update = QPushButton("Update a Phone")
        btn_delete = QPushButton("Delete a Phone")
        #btn_view = QPushButton("View a Phone")
        btn_view_all = QPushButton("View All Phones")
        btn_exit = QPushButton("Exit")
    
        #buttons = [btn_add, btn_update, btn_delete, btn_view, btn_view_all, btn_exit]
        buttons = [btn_add, btn_update, btn_delete, btn_view_all, btn_exit]
        
        for b in buttons:
            b.setMinimumWidth(120)
    
        # wiring
        btn_add.clicked.connect(self.show_add_phone)
        btn_update.clicked.connect(self.show_update_phone)
        btn_delete.clicked.connect(self.show_delete_phone)
        #btn_view.clicked.connect(self.show_view_phone)
        btn_view_all.clicked.connect(self.show_view_all_phones)
        btn_exit.clicked.connect(self.close)
    
        # add buttons to the bar
        for b in buttons:
            button_bar.addWidget(b)
    
        # add the horizontal bar to the top of our vertical layout
        main_layout.addLayout(button_bar)
    
        # 3. THE BOTTOM: Content Area (Output Window)
        self.content_area = QWidget()
        # give it a background color or border if you want to see the "window"
        self.content_area.setStyleSheet("background-color: #2b2b2b; border: 1px solid #3f3f3f;")
        self.content_layout = QVBoxLayout()
        self.content_area.setLayout(self.content_layout)
    
        # add the content area to the layout
        # give it a 'stretch factor' of 1 so it expands to fill the space
        main_layout.addWidget(self.content_area, 1) 
    
        # 4. Finalize
        self.setLayout(main_layout)


    # show add a phone
    def show_add_phone(self):
        #QMessageBox.information(self, "Add Phone", "Add Phone clicked!")
        
        dialog = AddPhoneDialog(self)
        if dialog.exec():
            # iff the user successfully added a phone, refresh the table
            self.show_view_all_phones()
        
                
    # show update a phone
    def show_update_phone(self):
        if not hasattr(self, 'table'):
            QMessageBox.warning(self, "INFO:", "Please 'View All Phones' and select a phone first.")
            return
    
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "INFO", "Select a phone to update.")
            return
    
        row = selected[0].row()
        phone_id = int(self.table.item(row, 0).text())
    
        phone_obj = phone.session.query(phone.Phone).filter_by(id=phone_id).first()
    
        dialog = UpdatePhoneDialog(phone_obj, self)
        if dialog.exec():
            self.show_view_all_phones()
       
        
    # show delete a phone       
    def show_delete_phone(self):
        #QMessageBox.information(self, "Delete Phone", "Delete Phone clicked!")

        # 1. check if the table has been created/loaded
        if not hasattr(self, 'table'):
            QMessageBox.warning(self, "INFO:", "Please 'View All Phones' and select a phone first.")
            return
    
        # 2. set the current selection
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "INFO:", "Please click on a row in the table or a cell within it to select a phone.")
            return
    
        # 3. set the ID from the first column of the selected row
        row = selected_items[0].row()
        phone_id = self.table.item(row, 0).text()
        brand = self.table.item(row, 1).text()
        model = self.table.item(row, 2).text()
    
        # 4. confirm deletion
        confirm = QMessageBox.question(
                self, "Confirm Delete", 
                f"Are you sure you want to delete:\nID: {phone_id} - {brand} {model}?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
    
        if confirm == QMessageBox.StandardButton.Yes:
            # toggle CLI mode in your phone module
            import phone
            phone.CLI = False
    
            # call the logic function from phone.py
            # ensure your deletePhone(id) function in phone.py handles the ID argument
            success = deletePhone(phone_id)  # phone_id is kept as a str and will convert to int inside deletePhone 
    
            phone.CLI = True
    
            if success:
                QMessageBox.information(self, "Success", "Phone deleted successfully.")
                # refresh the table to show the current state of the DB
                self.show_view_all_phones()
            else:
                QMessageBox.critical(self, "Error", "Failed to delete phone from database.")        
        
               
    # show view all phones
    def show_view_all_phones(self):
        #QMessageBox.information(self, "View All", "View All Phones clicked!")
                
        # set global variable CLI to False because we are not running in CLI mode
        phone.CLI = False
        
        # 1. get data from the database 
        phones = phone.viewPhones() # from phone.py        
        
        # reset CLI to True
        phone.CLI = True
        
        # 2. remove any existing widgets in the content area
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
        if not phones:
            self.content_layout.addWidget(QLabel("No phones found in the database."))
            return
    
        # 3. create the Table
        self.table = QTableWidget()
        self.table.setRowCount(len(phones))
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Brand", "Model", "OS", "Version", "Serial", "IMEI", "Status"])
    
        # 4. populate the Table
        for row, ph in enumerate(phones): 
            self.table.setItem(row, 0, QTableWidgetItem(str(ph.id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(ph.brand)))
            self.table.setItem(row, 2, QTableWidgetItem(str(ph.model)))
            self.table.setItem(row, 3, QTableWidgetItem(str(ph.os)))
            self.table.setItem(row, 4, QTableWidgetItem(str(ph.os_version)))
            self.table.setItem(row, 5, QTableWidgetItem(str(ph.serial_number)))
            self.table.setItem(row, 6, QTableWidgetItem(str(ph.imei)))
            self.table.setItem(row, 7, QTableWidgetItem(str(ph.status)))
    
        # make the table look nice
        self.table.resizeColumnsToContents()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # make it read-only
    
        self.content_layout.addWidget(self.table)
    
        # adjust main window size to fit the table
        self.resize(800, 600)
    
        
# main
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())