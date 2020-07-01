#==============================================================================#
"""
Author: Sergi Ponsà Cobas
Version:2 Creation of a DashBoard class that allows as create an object with all the dashboard functions and variables
			That way we will able to have multiple robots , we only have to create one object for each robot
			I also include a function recivedata, to receive the message from our comands
Version:1
Description: DashBoard functions to easy teleoperate the Universal Robots' robots

Functions:
ConnectDashBoard()
DashBoard_SendCommand()
LoadProgram()
RunProgram()
StopProgram()
PauseProgram()
ShutDownRobot()
ProgramState()
RobotState()
ProgramLoaded()
PopUp()
ClosePopUp()
WriteToLog()
CheckSavedProgram()
RobotVersion()
SetOperationalMode()
PowerOn()
PowerOff()
BrakeRelease()
CheckSafetyMode()
UnlockProtectiveStop()
CloseSafetyPopUp()
LoadInstallation()
RestartSafety()
ClearOperationalMode()

"""
import socket
import time
import traceback

class DashBoard_Communication():

	#Variables set when we create the object
	def __init__(self,RobotIPDashBoard):
		self.RobotIPDashBoard=RobotIPDashBoard
		#//////////////////////////////////////////////////////////////////////////////#
		#Global Variables
		self.DashBoard_Connected=False


		self.DashBoard_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)# The socket use IPv4 protocol & Provides sequenced, reliable, two-way, connection-based byte streams.
		self.DashBoard_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Sol_socket allows to read the socket options with getsockopt(), & SO_REUSEADDR means that a socket may bind, except when there is an active listening socket bound to the address
		self.DashBoard_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)#IPPROTO_TCP is a socket option that allows us to do modifications in our TCP protocol & TCP_NODELAY  This means that segments are always sent as soon as possible, even if there is only a small amount of data.
		self.DashBoard_sock.settimeout(2)# liberate the socket after 2 seconds if no data is recived or able to send
		#//////////////////////////////////////////////////////////////////////////////#

	def __enter__(self):
		self.DashBoard_Connect()
		return self

	def __exit__(self, exc_type, exc_value, tb):
		self.DashBoard_sock.close()
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)
			return False


	#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
	#functions

	def DashBoard_Connect(self):
		Port=29999
		Loop=True
		Counter=0
		while (Loop==True) :
			try:
				self.DashBoard_sock.connect((self.RobotIPDashBoard,Port))
				print ("Conexion success")
				#time.sleep(0.08)
				Loop=False
				self.DashBoard_Connected=True
			except:
				Counter+=1
				if  (Counter>=3):
					print(Counter)
					print("DashBoard connection to Robot IP " ,self.RobotIPDashBoard," Failed")
					#time.sleep(0.08)
					Loop=False
					self.DashBoard_Connected=False

	def DashBoard_SendCommand(self,cmd):
		print("Trying to send ",cmd)
		if self.DashBoard_Connected==True :
			try:
				print ("socket connected")
				#time.sleep(0.08)
				print ("command to send " , cmd)
				self.DashBoard_sock.sendall(cmd.encode())
				print("Sended")
				#time.sleep(0.08)
			except:
				self.DashBoard_Connect()
				print ("socket connected")
				try:
					print ("command to send " , cmd)
					self.DashBoard_sock.sendall(cmd.encode())
					print("Sended")
					#time.sleep(0.08)
				except:
					print("Command",cmd," not send")
		else:
			print("dashboard value", self.DashBoard_Connected)
			self.DashBoard_Connect()
			try:
					self.DashBoard_sock.sendall(cmd.encode())
			except:
					print("Command",cmd," not send")

	def DashBoard_GetData(self):
		if self.DashBoard_Connected==True:
			try:
				Data=self.DashBoard_sock.recv(4096) #It saves a maximum of 4096 bytes, from the first package, don't get the rest of packages
				return Data
			except:
				self.DashBoard_Connect()
				print ("socket connected")
				try:
					Data=self.DashBoard_sock.recv(4096) #It saves a maximum of 4096 bytes, from the first package, don't get the rest of packages
					return Data
				except:
					Data="No data received"
					return Data.encode()
		else:
			self.DashBoard_Connect()
			print ("socket connected")
			try:
				Data=self.DashBoard_sock.recv(4096) #It saves a maximum of 4096 bytes, from the first package, don't get the rest of packages
				return Data
			except:
				Data="No data received"
				return Data

	def DashBoard_LoadProgram(self,ProgramName):
		cmd = "load " + str(ProgramName) + ".urp \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_RunProgram(self):
		cmd = "play \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_StopProgram(self):
		cmd = "stop \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_PauseProgram(self):
		cmd = "pause \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_ShutDownRobot(self):
		cmd = "shutdown \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_RobotState(self):
		cmd = "robotmode \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_ProgramState(self):
		cmd = "programState \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_ProgramLoaded(self):
		cmd = "get loaded program \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_PopUp(self,text):
		cmd = "popup "+text+"\n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_ClosePopUp(self):
		cmd = "close popup \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_WriteToLog(self,text):
		cmd = "addToLog "+text+"\n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_CheckSavedProgram(self):
		cmd = "isProgramSaved \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_RobotVersion(self):
		cmd = "PolyscopeVersion \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_SerialNumber(self):
		cmd = "get serial number \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_Model(self):
		cmd = "get robot model \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_SetUserRole (self,option):

		user = "operator" if option == 0\
		 		else "none" if option == 1\
				else "programmer" if option == 2\
				else "locked" if option == 3\
				else "No Mode Selected"

		cmd = "setUserRole "+user+" \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_PowerOn(self):
		cmd = "power on \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_PowerOff(self):
		cmd = "power off \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_BrakeRelease(self):
		cmd = "brake release \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_CheckSafetyMode(self):
		cmd = "safetymode \n"
		self.DashBoard_SendCommand(cmd)# someway I have to obtain the result

	def DashBoard_UnlockProtectiveStop(self):
		cmd = "unlock protective stop \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_CloseSafetyPopUp(self):
		cmd = "close safety popup \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_LoadInstallation(self,InstallationFile):
		cmd = "load installation "+InstallationFile+".installation \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_RestartSafety(self):
		cmd = "restart safety \n"
		self.DashBoard_SendCommand(cmd)

	def DashBoard_ClearOperationalMode(self):
		cmd = "clear operational mode \n"
		self.DashBoard_SendCommand(cmd)

if __name__ == '__main__':
	IP="172.16.139.128"
	DashBoard = DashBoard_Communication(IP)
