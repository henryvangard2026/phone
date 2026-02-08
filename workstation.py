#
# Workstation Management
#
# This keeps track of the workstations
#
#

class Workstation(Base):
    workstation_id: int
    phone_id: int
    software_id: int
    workstation =   Column(String, default="UNASSIGNED")
    status = Column(statusEnum, default="UNASSIGNED") 
    
    
