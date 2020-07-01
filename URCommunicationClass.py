from URScriptsTcpIpClass import URScript_Comands
from URDashBoardClass import DashBoard_Communication
from URModbusClass import Modbus_Communication
import traceback

class UR_Communication ( DashBoard_Communication,URScript_Comands,Modbus_Communication ):

	#Variables set when we create the object
    def __init__(self,RobotIP,path_data = 'ModBus_server_data.xlsx'):
        self.RobotIP = RobotIP

        DashBoard_Communication.__init__(self,RobotIP)
        URScript_Comands.__init__(self,RobotIP)
        Modbus_Communication.__init__(self,RobotIP,path_data = path_data)
        self.Connect()

    def __enter__(self):
	    self.Connect()
	    return self

    def __exit__(self, exc_type, exc_value, tb):
	    self.Disconnect()
	    if exc_type is not None:
		    traceback.print_exception(exc_type, exc_value, tb)
		    return False

    def Connect(self):
        self.DashBoard_Connect()
        self.Modbus_Connect()
        self.URScript_Connect()

    def Disconnect(self):
        self.DashBoard_sock.close()
        self.Modbus_sock.close()
        self.URScript_sock.close()

    def ChangeIP(IP):
        self.RobotIPDashBoard = IP
        self.RobotIPURScript = IP
        self.RobotIPModbus = IP
        self.RobotIP = IP

if __name__ == '__main__':
    communication = UR_Communication("172.16.139.128")
