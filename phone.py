#
# Look for "NEXT:" to continue next time:
#
# NEXT:  1/3/26 valid that if it is an Android, it won't pick iOS and vice versa.
#

import os, time, sys

from sqlalchemy import create_engine, Column, Integer, String, Enum, text
from sqlalchemy.orm import declarative_base, sessionmaker

from sqlalchemy.inspection import inspect


# GLOBAL Variables:


# by default, this is True for CLI but from PyQT6 GUI, it MUST be set to False before calling any CLI functions
CLI = True  


# Setup

engine = create_engine('sqlite:///phones.db')  # "phones" is the database name
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# enumerated type for status

statusEnum = Enum("ACTIVE", "UNASSIGNED", "RETIRED", name="statusEnum")


# class Phone defines the structure of the "phone" table in the database

# PhoneUpdate class for updating a phone endpoint:
# ################################################

class Phone(Base):
    # class variable __tablename__ sets the table name in the database:  "phone"
    __tablename__ = "phone"
    __table_args__ = {"sqlite_autoincrement": True}
    
    id =            Column(Integer, primary_key=True, autoincrement=True)  # auto increment   
    brand =         Column(String, nullable=False)          # "Samsung", "Apple"
    model =         Column(String, nullable=False)
    os =            Column(String, nullable=False)          # "Android", "iOS"
    os_version =    Column(String, nullable=False)          # "18", "17"
    serial_number = Column(String, nullable=False, unique=True)
    imei =          Column(String, nullable=False, unique=True)
    status =        Column(statusEnum, default="UNASSIGNED")  
    workstation =   Column(String, default="UNASSIGNED")

    def __repr__(self):
        return (f"Phone(id={self.id}, brand={self.brand}, model={self.model}, os={self.os}, os_version={self.os_version}, serial_number={self.serial_number}, imei={self.imei}, status={self.status}), workstation={self.workstation})")


# initalize the database so phone ID will start at 1000
def initDB():
    
    # only use drop for testing, not the final app
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    with engine.connect() as conn:
        
        # check to see if phone database already has data so won't insert dummy phone
        result = conn.execute(text("SELECT COUNT(*) FROM phone"))
        count = result.scalar()
        
        # running for the first time:  phone database is empty so seed autoincrement at 1000
        if count == 0:
        
            # force sqlite_sequence to exist by inserting a dummy row with phone ID to force autoincrement at 1000
            conn.execute(text("""
                INSERT INTO phone (id, brand, model, os, os_version, serial_number, imei)
                VALUES (999, 'dummy', 'dummy', 'dummy', '0', 'x', 'y')
            """))
            conn.execute(text("DELETE FROM phone WHERE id = 999"))
    
            # set next phone ID to 1000
            conn.execute(text("UPDATE sqlite_sequence SET seq = 999 WHERE name = 'phone'"))
            conn.commit()
    

# CLI Menu
def CLIMenu():

    actions = {
        '1': ("\nAdding a phone...", addPhone),
        'a': ("\nAdding a phone...", addPhone),
        '2': ("\nUpdating a phone...", updatePhone),
        'u': ("\nUpdating a phone...", updatePhone),
        '3': ("\nDeleting a phone...", deletePhone),
        'd': ("\nDeleting a phone...", deletePhone),
        '4': ("\nViewing a phone...", viewPhone),
        'v': ("\nViewing a phone...", viewPhone),
        '5': ("\nViewing a phone...", viewPhones),
        'va': ("\nViewing a phone...", viewPhones),
        '6': ("\nBye - bye!!", exitMenu),
        'e': ("\nBye - bye!!", exitMenu),        
        'x': ("\nBye - bye!!", exitMenu)        
    }

    while True:
        clearScreen()        
        
        print("Workstation Phone Management CLI")
        print("--------------------------------")
        print("1/a.   Add a Phone")
        print("2/u.   Update a Phone")
        print("3/d.   Delete a Phone")
        print("4/v.   View a Phone")
        print("5/va.  View All Phones")
        print("6/e/x. Exit")
        print("---------------------")

        choice = input("Enter a choice: ").strip().lower()
        if choice not in actions:
            print("ERROR: Please enter 1-6.")
            print("Please try again.")                   
            continue

        message, action = actions[choice]
        print(message)  
        #print("Please try again.")                   

        try:    
            action()
        except Exception as e:
            print(f"ERROR: An error occurred while performing the action: {e}")
            print("Please try again.")                   


# Validation functions:
# ---------------------

# validate the first letter of the brand entered and return SAMSUNG, APPLE, OTHER or None
def validateBrand(brand=None):  # brand should be S, A, O
    BRANDS = {'S': 'Samsung', 'A': 'Apple', 'O': 'Other'}

    if not brand:
        print("ERROR:  Brand is required.")
        return None

    key = brand.upper()
    if key not in BRANDS:
        return None
    
    return BRANDS[key].upper()  # returns SAMSUNG, APPLE, OTHER


# validate the model and return model or the model or None
def validateModel(model=None):
    if not model or not model.strip():
        print("ERROR:  Model is required.")
        return None

    model = model.strip().upper()

    # validate against "OTHER" models
    if model == 'OTHER':
        print("INFO:  'Other' model selected.")
        return model
    
    # validate Android models
    # -----------------------
    
    samsungPres = ['S', 'A', 'FOLD', 'FLIP']
    
    # S and A models
    if model.startswith(samsungPres[0]) or model.startswith(samsungPres[1]):
        number = model[1:]  # S22 -> S, 22; A23 -> A, 23; 
        
        if number.isdigit():
            return model
        else:
            return None
        
    # FLIP or FOLD models
    elif model.startswith(samsungPres[2]) or model.startswith(samsungPres[3]):
        number = model[4:]  # FOLD7 -> FOLD, 7; FLIP7 -> FLIP, 7
    
        if number.isdigit():
            return model
        else:
            return None

    # validate iOS models
    # -------------------
    
    iphoneParts = model.split()  # split 'IPHONE 14' into 'IPHONE' and '14' or more parts

    if len(iphoneParts) == 2 and iphoneParts[0] == 'IPHONE' and (iphoneParts[1].isdigit() or iphoneParts[1] == 'SE'):
        return model  # valid iOS model

    print("ERROR:  Model is not valid (neither Android nor iOS).")
    return None


# validate and return ANDROID or IOS
def validateOSName(os_name=None):
    OS_NAMES = {'A': 'ANDROID', 'I': 'IOS'}
    
    if not os_name :
        print("ERROR:  OS name is required.")
        return False
    
    key = os_name.upper()
    if key not in OS_NAMES:
        print("ERROR:  Enter A for ANROID and I for IOS.")
        return False
    
    return OS_NAMES[key]  # returns ANDROID or IOS


# validate the OS version
def validateOSVersion(version=None):
    VERSIONS = {13, 14, 15, 16, 17, 18, 26}
    
    if not version:
        print("ERROR:  OS Version is required.")
        return None
    
    if not version.isdigit():
        print(f"ERROR:  OS {version} is invalid.  Please enter a number in {VERSIONS}.")
        print("Please try again.")                   
        return None         

    version = int(version)  # convert to integer since it is NOT a string
    if not version in VERSIONS:
        print(f"ERROR:  OS {version} is invalid.  Please enter a number in {VERSIONS}.")
        print("Please try again.")                   
        return None 
    
    return version


# validate the Serial Number, True: it exists in the database, False: it does not exist
def validateSerialNumber(serial_number=None):
    if not serial_number:
        print("ERROR:  Serial number is required.")
        return False

    # Check if the serial number already exists just to confirm with the phone ID
    existing_phone = session.query(Phone).filter_by(serial_number=serial_number).first()
    
    if existing_phone:
        #print(f"LOG:  Serial number {serial_number} exists.")
        return True  # it exists in the database

    #print("ERROR:  Serial number does NOT exist.")
    return False  # it does NOT exist in the database


# validate the IMEI to check if it already exists in the database
def validateIMEI(imei=None):
    if not imei:
        print("ERROR:  IMEI is required.")
        return False

    # Check if the IMEI already exists in the database
    existing_phone = session.query(Phone).filter_by(imei=imei).first()
    
    if existing_phone:
        #print(f"ERROR:  IMEI {imei} already exists.")
        return True

    return False


# validate and return the STATUS of the phone
def validateStatus(status=None):
    STATUSES = {'A': 'ACTIVE', 'U': 'UNASSIGNED', 'R': 'RETIRED'}
    
    if not status:
        print("ERROR:  Status is required.")
        return None
    
    key = status.strip().upper()
    if key not in STATUSES:
        print("ERROR:  Enter A for Active, U for UNASSIGNED and R for RETIRED.")
        return None
    
    return STATUSES[key]


# validate the workstation 
def validateWorkstation(workstation=None) -> bool:
    WS_PRE = ["WS", "UNASSIGNED"]  # all workstation names start with "WS" or it is "UNASSIGNED" initially
    
    if not workstation:
        print("ERROR:  Workstation is required.")
        return False
       
    # starts with "WS"
    if workstation.startswith(WS_PRE[0]):
        return True 

    if workstation.upper() == WS_PRE[1]:
        return True

    # workstation doesn't start with "WS" nor is it "UNASSIGNED", thus it is invalid
    return False  
    

# Add a phone
def addPhone(phone=None): 
    clearScreen()    

    # no phone was provided, run menu to get phone details
    if not phone:
        while True:
            try:
                # "In" at the end of each name means the input from the user
                
                brandIn = input("Brand (Samsung, Apple, Other) [S, A, O]: ").strip().upper()
                brandIn = validateBrand(brandIn)
                if not brandIn:
                    print("LOG:  Please try again.")
                    continue

                modelIn = input("Model (S22, iPhone 14, Other, ...): ").strip().upper()
                modelIn = validateModel(modelIn)
                if not modelIn:
                    continue    

                osNameIn = input("OS (Android, iOS) [A, I]: ").strip().upper()
                osNameIn = validateOSName(osNameIn)
                if not osNameIn:
                    print("LOG:  Please try again.")                  
                    continue

                osVersionIn = input("OS Version (13, 14, 15, 16, 17, 18, 26): ").strip()
                osVersionIn = validateOSVersion(osVersionIn)    
                if not osVersionIn:
                    print("LOG:  Please try again.")                   
                    continue

                serialNumberIn = input("Serial Number: ").strip().upper()  
                
                # True:  serial number already exists; can't add this phone (serial numbers are unique)
                if validateSerialNumber(serialNumberIn):  
                    print("LOG:  The serial number already exists in the database.  Please try again.")                   
                    continue
                
                imeiIn = input("IMEI: ").strip().upper()       
                
                # True: IMEI already exists; can't add this phone (IMEIs are unique)
                if validateIMEI(imeiIn): 
                    print("LOG: The IMEI already exists in the database. Please try again.")
                    continue
                
                statusIn = input("Status (ACTIVE, UNASSIGNED, RETIRED) [A, U, R]: ").strip().upper()
                statusIn = validateStatus(statusIn)
                if not statusIn:
                    print("LOG:  Please try again.")                                       
                    continue    
                
                # properly update workstation to UNASSIGNED if status is UNASSIGNED or RETIRED
                if statusIn == "ACTIVE":
                    workstationIn = input("Workstation: ").strip().upper()
                    if not validateWorkstation(workstationIn):
                        print("LOG:  Please try again.")                   
                        continue
                    
                elif statusIn in ["UNASSIGNED", "RETIRED"]:
                    workstationIn = "UNASSIGNED"
                    print(f"LOG: Status is {statusIn}, workstation automatically set to UNASSIGNED.")                
                
                workstationIn = input("Workstation: ").strip().upper()
                if not validateWorkstation(workstationIn):
                    print("LOG:  Please try again.")                   
                    continue
                    
                # create the phone: s23 = Phone(....) after all the details have been validated then break
                phone = Phone(
                            brand=brandIn,    
                            model=modelIn,
                            os=osNameIn,                 
                            os_version=osVersionIn,     
                            serial_number=serialNumberIn,
                            imei=imeiIn,
                            status=statusIn,
                            workstation=workstationIn        
                            )   
                break

            except ValueError:
                print("ERROR:  One or more details was invalid. Please try again.")

    # a phone was passed in
    try:
        # capitalize all phone details for uniformity
        capPhoneDetails(phone)
        
        # add the phone to the database regardless if it was passed in or created through the menu        
        session.add(phone)
        session.commit()
        print(f"INFO:  Phone {phone.brand} {phone.model} added successfully!")
    except Exception as e:
        session.rollback()
        print(f"ERROR:  Couldn't add the phone:  {e}")
    
    input("Press Enter to continue ...")


# delete a phone by its ID  
def deletePhone(phoneID=None):
    """
    Delete a phone by ID, providedor prompted for.
    Return:  True for successful deletion, False otherwise
    """
    
    if CLI:
        clearScreen()
    
        phoneID = input("Enter ID: ").strip()
    
        if not phoneID.isdigit():
            print("ERROR:  Enter a numeric ID!")
            return False
    
        # phoneID is an int
        phoneID = int(phoneID)
        phone = session.query(Phone).filter_by(id=phoneID).first()
        if phone:
            session.delete(phone)
            session.commit()
            print(f"INFO: Phone with ID {phoneID} deleted successfully!")      
            input("Press Enter to continue ...")
            return True
        else:
            print(f"ERROR: Phone with ID {phoneID} not found.")
            input("Press Enter to continue ...")
            return False
        
    # not called from CLI mode but GUI mode        
    else:
        from PyQt6.QtWidgets import QMessageBox
        
        if not phoneID.isdigit():
            QMessageBox.warning(None, "Error", "Enter a numeric ID!")
            return False
    
        # phoneID is an int
        phoneID = int(phoneID)        
        phone = session.query(Phone).filter_by(id=phoneID).first()      
        if phone:
            session.delete(phone)
            session.commit()     
            return True
        
        return False


# empty the "phone" database but keep the seeding
def deleteAllPhones():
    """
    Delete all phones.
    Return:  Not Applicable
    """
    
    session.query(Phone).delete() 
    session.commit()

# update a phone
def updatePhone(phoneID=None):
    """
    Update a phone.
    Return:  Not Applicable
    """
    
    clearScreen()

    #if not phoneID:
        #print("ERROR: A phone ID was required.")
        #time.sleep(2)
        #return

    # REF 1:  if this variable is False, commit is NOT needed (no details were updated)
    commit = False
    
    phone = None
    
    # a phoneID is provided
    if phoneID:
    
        # search for the phoneID and return the phone
        phone = session.query(Phone).filter_by(id=phoneID).first()
    
        if not phone:
            print(f"ERROR: Phone ID {phoneID} not found.")
            input("Press Enter to continue ...")
            return

    # no phoneID is provided, prompt for it
    phoneID = input("Enter a phone ID: ").strip()
    if not int(phoneID):
        print(f"ERROR:  Phone ID {phoneID} must be a number.")
        input("Press Enter to continue ...")
        return

    # search for the phoneID and return the phone
    phone = session.query(Phone).filter_by(id=phoneID).first()        


    # update functions, one per detail
    # ############################################################################# #

    def updateBrand():
        val = input("Brand [Samsung, Apple, Other] (S, A, O, Enter): ").strip()
        
        if not val:
            return 
        
        new = validateBrand(val)
        if new:
            phone.brand = new
            
            nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
            commit = True
        else:
            print(f"ERROR: Invalid brand {new}.")
            input("Press Enter to continue ...")

    def updateModel():      
        val = input("Model (S22, iPhone 14, Enter): ").strip()
        
        if not val:          
            return 
        
        new = validateModel(val)
        if new:
            phone.model = new.upper()
            
            nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
            commit = True            
        else:
            print(f"ERROR: Invalid model {new}.")
            input("Press Enter to continue ...")

    def updateOS():        
        val = input("OS [Android, iOS] (A, I, Enter): ").strip()
        
        if not val:
            #print("LOG:  Enter was pressed.  Skipping OS.")
            #time.sleep(2)            
            return 
        
        new = validateOSName(val)
        if new:
            phone.os = new
            
            nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
            commit = True            
        else:
            print(f"ERROR: Invalid OS {new}.")
            input("Press Enter to continue ...")

    def updateOSVersion():
        val = input("OS Version (13, ..., 18, 26, Enter): ").strip()
        
        # Enter was entered, skipping
        if not val:        
            return 
        
        # a non integer was entered
        elif not val.isdigit():
            print(f"ERROR:  OS {val} is invalid.  Please enter a number.")
            input("Press Enter to continue ...")
            return
            
        val = int(val)  # a number (integer) was entered, convert it to an integer
        new = validateOSVersion(val)
        if new:          
            phone.os_version = new  # new (OS) is an integer
            
            nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
            commit = True            
        else:
            print(f"ERROR: Invalid OS version {new}.")
            input("Press Enter to continue ...")            

    def updateSerialNumber():
        val = input("Serial Number (Enter to skip): ").strip()
        
        if not val:     
            return 
        
        #
        # by unique = True and nullable = False, the serial number already exists in the database
        #
        
        # update it to allow for a change
        phone.serial_number = val.upper()
            
        nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
        commit = True            
        
    def updateIMEI():
        val = input("IMEI (Enter to skip): ").strip()
        
        if not val:        
            return 
        
        new = validateIMEI(val)
        if not new:
            phone.imei = val
            
            nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
            commit = True            
        else:
            print(f"ERROR: IMEI {new} already exists.")
            input("Press Enter to continue ...")

    def updateStatus():
        val = input("Status [ACTIVE, UNASSIGNED, RETIRED] (A, U, R, Enter): ").strip()
        
        if not val:       
            return 
        
        new = validateStatus(val)
        if new:

            if new == "ACTIVE":
                print("INFO:  When status is ACTIVE, workstation must be assigned.")
                ws = input("Enter workstation: ").strip().upper()

                if validateWorkstation(ws):
                    phone.workstation = ws
                else:
                    print(f"ERROR:  Invalid workstation {ws}. Update status aborted.")
                    input("Press Enter to continue ...")
                    return            
                        
            if new in ["UNASSIGNED", "RETIRED"]:
                phone.workstation = "UNASSIGNED"       

            phone.status = new
            
            nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
            commit = True            
        else:
            print(f"ERROR: Invalid status {new}.")
            input("Press Enter to continue ...")

    def updateWorkstation():
        val = input("Workstation (Enter to skip): ").strip().upper()
        
        if not val:
            return 
        
        if validateWorkstation(val):
            phone.workstation = val
            
            nonlocal commit  # using nonlocal (in updatePhone scope) to update commit
            commit = True            
        else:
            print(f"ERROR: Invalid workstation {val}.")
            input("Press Enter to continue ...")

    # save (commit) then exit
    def saveExit():
        if commit:
            # REF 1:  commit because one or more phone details has been updated by the user
            session.commit()
            print(f"INFO: Phone ID {phone.id} was updated successfully!  Exiting ...")
            input("Press Enter to continue ...")

    # Menu Map
    # ############################################################################# #

    menuMap = {
        "1": ("Brand", updateBrand),
        "2": ("Model", updateModel),
        "3": ("OS Name", updateOS),
        "4": ("OS Version", updateOSVersion),
        "5": ("Serial Number", updateSerialNumber),
        "6": ("IMEI", updateIMEI),
        "7": ("Status", updateStatus),
        "8": ("Workstation", updateWorkstation),
        "10": ("Save and Exit", saveExit)
    }

    while True:
        clearScreen()
        print(f"Updating Phone ID : {phoneID}")
        print("--------------------------------")
        print(f"1.  Brand         : {phone.brand}")
        print(f"2.  Model         : {phone.model}")
        print(f"3.  OS Name       : {phone.os}")
        print(f"4.  OS Version    : {phone.os_version}")
        print(f"5.  Serial Number : {phone.serial_number}")
        print(f"6.  IMEI          : {phone.imei}")
        print(f"7.  Status        : {phone.status}")
        print(f"8.  Workstation   : {phone.workstation}")
        print("--------------------------------")
        print("10.  Save and Exit")
        print("--------------------------------")

        choice = input("Enter a choice [1-8, 10]: ").strip()

        if choice in menuMap:
            _, handler = menuMap[choice]
            handler()
            
            if choice == "10":
                break
        else:
            print(f"ERROR: Invalid choice {choice}.")
            input("Press Enter to continue ...")


# view a phone by its ID, IMEI, serial number or workstation
def viewPhone(phoneID=None, imei=None, serialNumber=None, workstation=None):
    clearScreen()
            
    phone = None
    if phoneID:
        phone = session.query(Phone).filter_by(id=phoneID).first()
    elif imei:
        phone = session.query(Phone).filter_by(imei=imei).first()   
    elif serialNumber:
        phone = session.query(Phone).filter_by(serial_number=serialNumber).first()
    elif workstation:
        phone = session.query(Phone).filter_by(workstation=workstation).first()

    if phone:
        print(phone)
        input("Press Enter to continue ...")
        return
    else:
        print("LOG:  Please try again.")                   
        return
         
    # search by menu
    while True:
        print("Search By:")
        print("-----------------")
        print("1. Phone ID: ")
        print("2. IMEI: ")
        print("3. Serial Number: ")
        print("4. Exit")
        print("-----------------")
    
        choice = input("Enter a number [1-4]:").strip()
        
        if choice == '4':
            return
        
        if choice == '1':
            val = input("ID: ").strip().upper()
            phone = session.query(Phone).filter_by(id=val).first()
            
            if phone:
                print(phone)
                input("Press Enter to continue ...")
                break
            
            else:  # the phone does not exist
                print(f"ERROR: Phone not found by ID {val}.")
                input("Press Enter to continue ...")                
                continue
        
        if choice == '2':
            val = input("IMEI: ").strip().upper()            
            phone = session.query(Phone).filter_by(imei=val).first()   
            
            if phone:
                print(phone)
                input("Press Enter to continue ...")
                break
            
            else:  # the phone does not exist
                print(f"ERROR: Phone not found by IMEI {val}.")
                input("Press Enter to continue ...")                
                continue

        if choice == '3':
            val = input("Serial Number: ").strip().upper()            
            phone = session.query(Phone).filter_by(serial_number=val).first()
            
            if phone:
                print(phone)
                input("Press Enter to continue ...")
                break
            
            else:  # the phone does not exist
                print(f"ERROR: Phone not found by serial number {val}.")
                input("Press Enter to continue ...")                
                continue
    

# View all phones in the database
def viewPhones():
    phones = session.query(Phone).all()
    
    # terminal mode by default
    if CLI:
        clearScreen()
    
        print(f"Phones in the database \"{Phone.__tablename__}\":")
        print("-------------------------------")
        for phone in phones:
            status_str = "Active" if phone.status else "Inactive"
            print(f"Phone ID: {phone.id}, Brand: {phone.brand}, Model: {phone.model}, OS: {phone.os} {phone.os_version}, "
                  f"Serial Number: {phone.serial_number}, IMEI: {phone.imei}, Status: {status_str}, "
                  f"Workstation: {phone.workstation}\n")
        
        input("Press Enter to continue ...")
    else:
        return phones  # return phones to PyQT6 GUI's show_view_all_phones


# exit menu
def exitMenu():
    # close the session and exit
    session.close()
    sys.exit(0) 


# Utility functions:
# ------------------

# clear the screen
def clearScreen():
    os.system('cls' if os.name == 'nt' else 'clear')    


# capitalize all phone details for uniformity
def capPhoneDetails(phone=None):
    if not phone:
        print("ERROR:  No phone is provided.")
        return
            
    mapper = inspect(phone.__class__)
    for column in mapper.columns:
        detail = column.key  # each phone detail (an attribute):  id, brand, model, ...
        value = getattr(phone, detail)
        if isinstance(value, str):
            setattr(phone, detail, value.upper())


# seed the phones for testing
def seedTestPhones():
    a = Phone(
        brand="Samsung",
        model="S22",
        os="Android",
        os_version="18",
        serial_number="XX112233YY-1014",
        imei="998877665544332211-1014",
        status="ACTIVE",
        workstation="WS1014"
    )
    
    b = Phone(
        brand="Samsung",
        model="S23",
        os="Android",
        os_version="18",
        serial_number="XX112233YY-1015",
        imei="998877665544332211-1015",
        status="ACTIVE",
        workstation="WS1015"
    )
    
    c = Phone(
        brand="Samsung",
        model="S24",
        os="Android",
        os_version="18",
        serial_number="XX112233YY-1016",
        imei="998877665544332211-1016",
        status="ACTIVE",
        workstation="WS1016"
    )
    
    d = Phone(
        brand="Samsung",
        model="Fold5",
        os="Android",
        os_version="18",
        serial_number="XX112233YY-1017",
        imei="998877665544332211-1017",
        status="ACTIVE",
        workstation="WS1017"
    )
    
    e = Phone(
        brand="Samsung",
        model="Flip5",
        os="Android",
        os_version="18",
        serial_number="XX112233YY-1018",
        imei="998877665544332211-1018",
        status="ACTIVE",
        workstation="WS1018"
    )
    
    f = Phone(
        brand="Apple",
        model="iPhone 13",
        os="iOS",
        os_version="17",
        serial_number="AA556677BB-1019",
        imei="112233445566778899-1019",
        status="ACTIVE",
        workstation="WS1019"
    )
    
    g = Phone(
        brand="Apple",
        model="iPhone 14",
        os="iOS",
        os_version="17",
        serial_number="AA556677BB-1020",
        imei="112233445566778899-1020",
        status="ACTIVE",
        workstation="WS1020"
    )
    
    h = Phone(
        brand="Apple",
        model="iPhone 15",
        os="iOS",
        os_version="17",
        serial_number="AA556677BB-1021",
        imei="112233445566778899-1021",
        status="ACTIVE",
        workstation="WS1021"
    )
    
    i = Phone(
        brand="Apple",
        model="iPhone 15 Pro",
        os="iOS",
        os_version="17",
        serial_number="AA556677BB-1022",
        imei="112233445566778899-1022",
        status="ACTIVE",
        workstation="WS1022"
    )
    
    j = Phone(
        brand="Apple",
        model="iPhone 16",
        os="iOS",
        os_version="18",
        serial_number="AA556677BB-1023",
        imei="112233445566778899-1023",
        status="ACTIVE",
        workstation="WS1023"
    )

    addPhone(a)
    addPhone(b)
    addPhone(c)
    addPhone(d)
    addPhone(e)
    addPhone(f)
    addPhone(g)
    addPhone(h)
    addPhone(i)
    addPhone(j)    
    

# main
if __name__ == "__main__":

    # init the DB
    initDB()
    
    # delete all phones for testing
    deleteAllPhones()

    # seed the phones for testing
    seedTestPhones()

    while True:
        CLIMenu()
