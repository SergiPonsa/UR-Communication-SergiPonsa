#==============================================================================#
"""
Author: Sergi Ponsà Cobas

Version:1

clean_data
From an excel which has columns: Address | Pre 3.0 | 3.0 | R | W | Description
Extracts the UR Modbus registers (Considering that, any element in the first column which is different from Nan and float is a register)
If it finds again Address, It's a different mapping which it's not the decired one so from there I erase all below

find_value
Return the file and columns that contains the specified value

get_read_registers/get_write_registers
Returns the index or the address of the read and write registers, depending if you provide parameter address True or False.
It knows which are read or Write , thanks to the columns read and write, if they are different from NaN ,so there is something writen they are read or write

desciption_add_read_and_write


Functions:
1-clean_data | 2-find_value() | 3-get_read_registers | 4-get_write_registers | 5-desciption_add_read_and_write
5-
"""
import socket
import time
import sys

import numpy as np
import pandas as pd
import math


class Modbus_Communication():
	#//////////////////////////////////////////////////////////////////////////////#
	#Global Variables


	#Variables set when we create the object
	def __init__(self,RobotIPModbus, path_data = 'ModBus_server_data.xlsx'):
		self.RobotIPModbus=RobotIPModbus
		self.Modbus_df = self.Modbus_clean_data(path_data)
		self.Modbus_df_reg = self.Modbus_df.loc[:,["Address","R","W","Description"]]
		self.Modbus_df_reg["Data"] = [0]*len(self.Modbus_df_reg.index)
		general_purpose_addresses = list(range(128,257))
		print(general_purpose_addresses)
		general_purpose_descriptions = ["General purpose"] * len(general_purpose_addresses)
		general_purpose_read = ["*"]* len(general_purpose_addresses)
		general_purpose_write = ["*"]* len(general_purpose_addresses)
		general_purpose_data = [0]* len(general_purpose_addresses)
		self.Modbus_add_registers(general_purpose_addresses,general_purpose_descriptions,general_purpose_read,general_purpose_write,general_purpose_data)



		self.Modbus_registers_all_ind = list(self.Modbus_df_reg.index)
		self.Modbus_registers_read_ind = list(self.Modbus_get_read_registers(Address = False))
		self.Modbus_registers_write_ind = list(self.Modbus_get_write_registers(Address = False))


		self.Modbus_registers_all = list(self.Modbus_df_reg.loc[:,"Address"])
		self.Modbus_registers_read = list(self.Modbus_get_read_registers(Address = True))
		self.Modbus_registers_write = list(self.Modbus_get_write_registers(Address = True))

		self.Modbus_desciption_add_read_and_write(self.Modbus_registers_read_ind,self.Modbus_registers_write_ind)

		self.Modbus_registers_all_description = list(self.Modbus_df_reg.loc[:,"Description"])
		self.Modbus_registers_all_data = list(self.Modbus_df_reg.loc[:,"Data"])

		#Socket elements
		#//////////////////////////////////////////////////////////////////////////////#
		#Global Variables
		self.Modbus_Connected=False
		self.Modbus_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)# The socket use IPv4 protocol & Provides sequenced, reliable, two-way, connection-based byte streams..
		self.Modbus_sock.settimeout(10)# liberate the socket after 2 seconds if no data is recived or able to send


	#//////////////////////////////////////////////////////////////////////////////#

	#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
	#functions
	def Modbus_clean_data(self,path_data = 'ModBus_server_data.xlsx' ):
		#Create a dataframe with the Excel data given by UR of the Modbus registers
		df_URModbus = pd.read_excel('ModBus_server_data.xlsx',sheet_name = 'Sheet1')
		#Show the head to check that data it's ok
		#print(df_URModbus.head())

		#Delete the rows which has a NaN in the first column
		df_URModbus = df_URModbus.dropna(axis = 0,how = 'any', subset = [df_URModbus.columns[0]])
		#Show the head to check that data it's ok
		#print(df_URModbus.head(n=33))

		#Delete the columns which has all NaN in the column
		df_URModbus = df_URModbus.dropna(axis = 1,how = 'all')
		df_URModbus = df_URModbus.reindex()
		#Show the head to check that data it's ok
		#print(df_URModbus.head(n=33))

		#Change names to the right one
		Data_names = df_URModbus.iloc[0,0:len(df_URModbus.columns)-1]
		#print(Data_names)
		#Convert object to String array
		Data_names_string = []
		for name in Data_names:
			Sname = str(name)
			Data_names_string.append(name.strip())
		#Ensure the list has the same size
		while(len(df_URModbus.columns)-len(Data_names_string) != 0):
			Data_names_string.append("Description")
		#print(Data_names_string)

		#Change the names
		df_URModbus.columns = Data_names_string

		#Delete the first row
		df_URModbus = df_URModbus.drop(index = 0)

		#Search the Adrres row to delte the bit data
		#print("\n")
		#print(list(df_URModbus.columns))
		#print(list(df_URModbus.index))
		try:
			aux_result = self.find_value ("address",df_URModbus)
			#print(aux_result)
			[ind,col] = aux_result.pop()

			df_URModbus = df_URModbus.loc[:ind-1, :]
			print("Second mapping erased")
		except:
			print("There is not a second mapping")

		#Delete rows which don't have numbers
		aux_df = df_URModbus.loc[:,df_URModbus.columns[0]]
		#print("\n")
		#print(aux_df)
		aux_df = pd.to_numeric(aux_df, errors =  'coerce')
		#print(aux_df)
		index = aux_df.index[aux_df.apply(np.isnan)]
		df_URModbus = df_URModbus.drop(index = index)
		#print(df_URModbus)
		#print(index)
		new_index = list( range( len(list(df_URModbus.index)) ) )
		print(new_index)
		df_URModbus.index = new_index

		#Show the head to check that data it's ok
		#print(df_URModbus.head(n=250))
		df_URModbus.to_excel("Clean Data.xlsx")

		return df_URModbus

	def Modbus_add_registers(self,addresses_to_add,descriptions_to_add,fill_read,fill_write,fill_data):
		new_registers_df = pd.DataFrame({})
		new_registers_df["Address"] = addresses_to_add
		new_registers_df["R"] = fill_read
		new_registers_df["W"] = fill_read
		new_registers_df["Description"] = descriptions_to_add
		new_registers_df["Data"] = fill_data
		print(len(list(new_registers_df.index)))
		print(len(list(self.Modbus_df_reg.index)))
		self.Modbus_df_reg = pd.concat([self.Modbus_df_reg, new_registers_df], ignore_index=False)
		print(len(list(self.Modbus_df_reg.index)))
		self.Modbus_df_reg.tail(len(addresses_to_add))
		new_index = list( range( len(list(self.Modbus_df_reg.index)) ) )
		print(new_index)
		self.Modbus_df_reg.index = new_index
		print(self.Modbus_df_reg.index)


	def Modbus_find_value (self, value, dataframe,case_sens = False,once = False,\
	 				in_row = None, end_row = None, in_col = None, end_col = None):
		if (in_row == None):
			in_row = 0
		if (end_row == None):
			rows = list(dataframe.index)
			#print("rows")
			#print(rows)
			#end_row = len(rows)
		if (in_col == None):
			in_col = 0
		if (end_col == None):
			columns = list(dataframe.columns)
			#print("columns ")
			#print(columns)
			end_col = len(dataframe.columns)
		aux_df = dataframe
		rows_columns =  []
		#print("\n")
		for col in aux_df.columns[in_col:end_col]:
			#print(col)
			#print(aux_df[col].str.contains(value,case = case_sens).any())
			if aux_df[col].str.contains(value,case = case_sens).any():
				for row in aux_df.index[in_row:end_row]:
					#print(row)
					#print(aux_df.at[row,col])
					if case_sens == True:
						if(value in aux_df.at[row,col]):
							rows_columns.append([row,col])
							if once :
								return rows_columns
					else:
						if( str(value).lower()  in str( aux_df.at[row,col] ).lower() ):
							rows_columns.append([row,col])
							if once :
								return rows_columns

		return rows_columns

	def Modbus_get_read_registers(self,Address = False):
		ModBus_df = self.Modbus_df_reg
		R_df = ModBus_df.loc[:,"R"]
		#print(R_df)
		R_df = R_df.dropna()
		index = R_df.index
		if Address:
			return ModBus_df.loc[index,"Address"]
		else:
			return index

	def Modbus_get_write_registers(self,Address = False):
		ModBus_df = self.Modbus_df_reg
		W_df = ModBus_df.loc[:,"W"]
		#print(W_df)
		W_df = W_df.dropna()
		index = W_df.index
		if Address:
			return ModBus_df.loc[index,"Address"]
		else:
			return index

	def Modbus_desciption_add_read_and_write(self,ind_registers_read,ind_registers_write):
		ModBus_df = self.Modbus_df_reg

		for ind_register in ModBus_df.index:

			Address = ModBus_df.loc[ind_register,"Address"]
			Description = ModBus_df.loc[ind_register,"Description"]
			read_string = "-"
			write_string = "-"

			if ind_register in ind_registers_read:
				read_string = "R"

			if ind_register in ind_registers_write:
				write_string = "W"

			self.Modbus_df_reg.loc[ind_register,"Description"] =read_string +"/" +write_string+" "+ ModBus_df.loc[ind_register,"Description"]
			#print(self.Modbusdf_reg.loc[ind_register,"Description"])

	def Modbus_Connect(self):
		Port=502
		Loop=True
		Counter=0
		print("Doing something")
		while (Loop==True) :
			try:
				print("Hi")
				self.Modbus_sock.connect((self.RobotIPModbus,Port))
				self.Modbus_Connected=True
				Loop=False
				print("Connected")

			except:
				Counter+=1
				print(Counter)
				if  (Counter>=2):
					print("Modbus connection to Robot IP " ,self.RobotIPModbus," Failed")
					#time.sleep(0.08)
					Loop=False
					self.Modbus_Connected=False


	def Modbus_SendCommand(self,cmd):
		cmd = cmd +"\n"
		print("Trying to send ",cmd.encode())
		if self.Modbus_Connected==True :
			try:
				self.Modbus_sock.sendall(cmd.encode())
			except:
				self.Modbus_Connect()
				try:
					self.Modbus_sock.sendall(cmd.encode())
				except:
					print("Oops!", sys.exc_info()[0], "occured.")
					print("Command",cmd," not send")
		else:
			self.Modbus_Connect()
			try:
					self.Modbus_sock.sendall(cmd.encode()+"\n")
			except:
					print("Command",cmd," not send")

	def Modbus_GetData(self):
		if self.Modbus_Connected==True:
			try:
				Data=self.Modbus_sock.recv(4096) #It saves a maximum of 4096 bytes, from the first package, don't get the rest of packages
				return Data
			except:
				self.Modbus_Connect()
				print ("socket connected")
				try:
					Data=self.Modbus_sock.recv(4096) #It saves a maximum of 4096 bytes, from the first package, don't get the rest of packages
					return Data
				except:
					Data = "No data received"
					print(Data)
					return Data
		else:
			self.Modbus_Connect()
			print ("socket connected")
			try:
				Data=self.Modbus_sock.recv(4096) #It saves a maximum of 4096 bytes, from the first package, don't get the rest of packages
				return Data
			except:
				print("No data received")
				return Data

	def Modbus_Request_to_write(self,Adrres_dec,Value_to_write_dec,printb = False):
		Sequence_number_modbus = "\x00\x01"
		Protocol_identifier_modbus = "\x00\x00"
		Message_length_modbus = "\x00\x06"
		Unit_identifier_modbus = "\x02"
		Function_code_modbus = "\x06"

		Adrres_hex_hight_modbus,Adrres_hex_low_modbus = self.Modbus_dec_to_hex(Adrres_dec)
		Value_hex_hight_modbus,Value_hex_low_modbus = self.Modbus_dec_to_hex(Value_to_write_dec)

		cmd = Sequence_number_modbus+Protocol_identifier_modbus+Message_length_modbus \
			+Unit_identifier_modbus+Function_code_modbus+Adrres_hex_hight_modbus+Adrres_hex_low_modbus \
			+Value_hex_hight_modbus+Value_hex_low_modbus

		self.Modbus_SendCommand(cmd)
		time.sleep(0.1)
		Data = self.Modbus_GetData()
		if(printb==True):
			print("Data recieved")
			print(Data)
			print(type(Data))

		Recv_Sequence_number = Data[0]*256+Data[1]
		Recv_Protocol_identifier = Data[2]*256+Data[3]
		Recv_Message_length = Data[4]*256 + Data[5]
		Recv_Unit_identifier = Data[6]
		Recv_Function_code = Data[7]
		Recv_Number_of_registers = Data[8]*256+Data[9]
		BytesValue = Recv_Message_length-4
		value = 0
		for i in range(BytesValue):
			value += Data[9+1++i]*(256**(BytesValue-1-i))

		if(printb==True):
			print("Recv_Sequence_number")
			print(Recv_Sequence_number)
			print("Recv_Protocol_identifier")
			print(Recv_Protocol_identifier)
			print("Recv_Message_length")
			print(Recv_Message_length)
			print("Recv_Unit_identifier")
			print(Recv_Unit_identifier)
			print("Recv_Function_code")
			print(Recv_Function_code)
			print("Recv_Number_of_registers")
			print(Recv_Number_of_registers)
			print("BytesValue")
			print(BytesValue)
			print("value")
			print(value)



	def Modbus_Request_to_read(self,Adrres_dec,printb=False):
		Sequence_number_modbus = "\x00\x04"
		Protocol_identifier_modbus = "\x00\x00"
		Message_length_modbus = "\x00\x06"
		Unit_identifier_modbus = "\x02"
		Function_code_modbus = "\x03"

		Adrres_hex_hight_modbus,Adrres_hex_low_modbus = self.Modbus_dec_to_hex(Adrres_dec)

		Number_of_register_requested = "\x00\x01"

		cmd = Sequence_number_modbus+Protocol_identifier_modbus+Message_length_modbus \
			+Unit_identifier_modbus+Function_code_modbus+Adrres_hex_hight_modbus+Adrres_hex_low_modbus \
			+Number_of_register_requested

		OK = False
		Counter = 0
		while(OK == False):
			self.Modbus_SendCommand(cmd)
			#time.sleep(0.5)

			Data = self.Modbus_GetData()
			if(printb==True):
				print("Data recieved")
				print(Data)
				print(type(Data))


			Recv_Sequence_number = Data[0]*256+Data[1]
			Recv_Protocol_identifier = Data[2]*256+Data[3]
			Recv_Message_length = Data[4]*256 + Data[5]
			Recv_Unit_identifier = Data[6]
			Recv_Function_code = Data[7]
			Recv_Number_of_registers = Data[8]
			BytesValue = Recv_Message_length-3
			value = 0
			if(Recv_Function_code!= 3):
				print("Error happend")
				print("Recv_Function_code")
				print( hex(Recv_Function_code) )
				Counter +=1
				#time.sleep(0.01)

				if(Counter >=3):
					OK = True
					return -1
			else:
				OK=True

		for i in range(BytesValue):
			value += Data[8+1++i]*(256**(BytesValue-1-i))

		if(printb==True):
			print("Recv_Sequence_number")
			print(Recv_Sequence_number)
			print("Recv_Protocol_identifier")
			print(Recv_Protocol_identifier)
			print("Recv_Message_length")
			print(Recv_Message_length)
			print("Recv_Unit_identifier")
			print(Recv_Unit_identifier)
			print("Recv_Function_code")
			print(Recv_Function_code)
			print("Recv_Number_of_registers")
			print(Recv_Number_of_registers)
			print("BytesValue")
			print(BytesValue)
			print("value")
			print(value)

		return value



	def Modbus_dec_to_hex(self,dec_value):
		aux,hex_value = hex(dec_value).split("x")
		if(len(hex_value)==1):

			hex_value_hight_modbus = "\x00"
			hex_value_low_modbus = chr(int(hex_value,16))
		elif (len(hex_value)==2):
			hex_value_hight_modbus = "\x00"
			hex_value_low_modbus = chr(int(hex_value,16))
		elif (len(hex_value)==3):
			hex_value_hight_modbus = chr(int(hex_value[:-2],16))
			hex_value_low_modbus = chr(int(hex_value[-2:],16))
		elif (len(hex_value)==4):
			hex_value_hight_modbus = chr(int(hex_value[:-2],16))
			hex_value_low_modbus = chr(int(hex_value[-2:],16))

		return [hex_value_hight_modbus,hex_value_low_modbus]

	def Modbus_dataframe_update_read_registers(self,printb=False):
		Addresses_to_access = self.Modbus_registers_read
		Indixes_to_modify = self.Modbus_registers_read_ind

		for i in range(len(Addresses_to_access)):
			if(printb==True):
				print("Address")
				print(Addresses_to_access[i])

			time.sleep(0.01)

			self.Modbus_df_reg.loc[Indixes_to_modify[i],"Data"]= self.Modbus_Request_to_read(Addresses_to_access[i],printb=printb)


	def Modbus_get_joint_angles(self,degrees=True):
		index_joint_angle_array = [self.Modbus_registers_read.index(270),\
						self.Modbus_registers_read.index(271),\
						self.Modbus_registers_read.index(272),\
						self.Modbus_registers_read.index(273),\
						self.Modbus_registers_read.index(274),\
						self.Modbus_registers_read.index(275)]
		index_joint_angle_dataframe = [self.Modbus_registers_read_ind[index_joint_angle_array[0]],\
								self.Modbus_registers_read_ind[index_joint_angle_array[1]],\
								self.Modbus_registers_read_ind[index_joint_angle_array[2]],\
								self.Modbus_registers_read_ind[index_joint_angle_array[3]],\
								self.Modbus_registers_read_ind[index_joint_angle_array[4]],\
								self.Modbus_registers_read_ind[index_joint_angle_array[5]]]

		index_joint_revolution_array = [self.Modbus_registers_read.index(320),\
						self.Modbus_registers_read.index(321),\
						self.Modbus_registers_read.index(322),\
						self.Modbus_registers_read.index(323),\
						self.Modbus_registers_read.index(324),\
						self.Modbus_registers_read.index(325)]
		index_joint_revolution_dataframe = [self.Modbus_registers_read_ind[index_joint_revolution_array[0]],\
								self.Modbus_registers_read_ind[index_joint_revolution_array[1]],\
								self.Modbus_registers_read_ind[index_joint_revolution_array[2]],\
								self.Modbus_registers_read_ind[index_joint_revolution_array[3]],\
								self.Modbus_registers_read_ind[index_joint_revolution_array[4]],\
								self.Modbus_registers_read_ind[index_joint_revolution_array[5]]]


		joint_angle_reg_value = list(self.Modbus_df_reg.loc[index_joint_angle_dataframe,"Data"])
		joint_revolution_reg_value = list(self.Modbus_df_reg.loc[index_joint_revolution_dataframe,"Data"])

		Max_Val = 6283 #2pi, 360 degrees

		joint_angle_value=[]
		for i in range(len(joint_angle_reg_value)):
			if(joint_revolution_reg_value[i]>0): #Negative angle
				joint_angle_value.append( -1*(Max_Val-joint_angle_reg_value[i])/(10**3) )
			else: #Positive angle
				joint_angle_value.append( joint_angle_reg_value[i]/(10**3) )

		if(degrees==True):
			joint_angle_value = list( np.array(joint_angle_value) * (180/3.14) )

		return joint_angle_value

	def Modbus_get_tcp_pos(self,degrees=True,rotvec = False):
		index_tcp_pose_array = [self.Modbus_registers_read.index(400),\
						self.Modbus_registers_read.index(401),\
						self.Modbus_registers_read.index(402),\
						self.Modbus_registers_read.index(403),\
						self.Modbus_registers_read.index(404),\
						self.Modbus_registers_read.index(405)]
		index_tcp_pose_dataframe = [self.Modbus_registers_read_ind[index_tcp_pose_array[0]],\
								self.Modbus_registers_read_ind[index_tcp_pose_array[1]],\
								self.Modbus_registers_read_ind[index_tcp_pose_array[2]],\
								self.Modbus_registers_read_ind[index_tcp_pose_array[3]],\
								self.Modbus_registers_read_ind[index_tcp_pose_array[4]],\
								self.Modbus_registers_read_ind[index_tcp_pose_array[5]]]

		tcp_pose_reg_value = list(self.Modbus_df_reg.loc[index_tcp_pose_dataframe ,"Data"])

		Max_Val = 16**4 #2pi, 360 degrees

		tcp_pose_value=[]
		for i in range(3):
			if(tcp_pose_reg_value[i]>Max_Val*0.5): #Negative dist
				tcp_pose_value.append( -1*(Max_Val-tcp_pose_reg_value[i])/(10) )
			else: #Positive distance
				tcp_pose_value.append( tcp_pose_reg_value[i]/(10) )

		for i in range(3):
			if(tcp_pose_reg_value[3+i]>0): #Positive
				tcp_pose_value.append( (Max_Val-tcp_pose_reg_value[3+i])/(10**3) )
			else: #Negative angle
				tcp_pose_value.append( -1*tcp_pose_reg_value[3+i]/(10**3) )
		if(rotvec == True):
			if(degress == True):
				tcp_pose_value[3],tcp_pose_value[4],tcp_pose_value[5] = \
					list( np.array(tcp_pose_value[3],tcp_pose_value[4],tcp_pose_value[5]) * (180/3.14) )


		else:
			print("tcp_pose_value")
			print(tcp_pose_value)
			tcp_pose_value[3],tcp_pose_value[4],tcp_pose_value[5] = \
				self.Modbus_rv2rpy(tcp_pose_value[3],tcp_pose_value[4],tcp_pose_value[5],degrees=degrees)

		return tcp_pose_value


	def Modbus_rpy2rv(self,roll,pitch,yaw,degrees=True):

		if(degrees==True):
	  		alpha = math.radians(yaw)
	  		beta = math.radians(pitch)
	  		gamma = math.radians(roll)
		else:
			alpha = yaw
			beta = pitch
			gamma = roll

		ca = math.cos(alpha)
		cb = math.cos(beta)
		cg = math.cos(gamma)
		sa = math.sin(alpha)
		sb = math.sin(beta)
		sg = math.sin(gamma)

		#compute teh rotation matrix
		r11 = ca*cb
		r12 = ca*sb*sg-sa*cg
		r13 = ca*sb*cg+sa*sg
		r21 = sa*cb
		r22 = sa*sb*sg+ca*cg
		r23 = sa*sb*cg-ca*sg
		r31 = -sb
		r32 = cb*sg
		r33 = cb*cg

		theta = math.acos((r11+r22+r33-1)/2)
		sth = math.sin(theta)
		kx = (r32-r23)/(2*sth)
		ky = (r13-r31)/(2*sth)
		kz = (r21-r12)/(2*sth)

		return [(theta*kx),(theta*ky),(theta*kz)]

	def Modbus_rv2rpy(self,rx,ry,rz,degrees = True):


		theta = math.sqrt(rx*rx + ry*ry + rz*rz)

		print("theta")
		print(theta)
		print("rx")
		print(rx)
		kx = rx/theta
		ky = ry/theta
		kz = rz/theta
		cth = math.cos(theta)
		sth = math.sin(theta)
		vth = 1-math.cos(theta)

		r11 = kx*kx*vth + cth
		r12 = kx*ky*vth - kz*sth
		r13 = kx*kz*vth + ky*sth
		r21 = kx*ky*vth + kz*sth
		r22 = ky*ky*vth + cth
		r23 = ky*kz*vth - kx*sth
		r31 = kx*kz*vth - ky*sth
		r32 = ky*kz*vth + kx*sth
		r33 = kz*kz*vth + cth

		beta = math.atan2(-r31,math.sqrt(r11*r11+r21*r21))

		if (beta > math.radians(89.99)):
			beta = math.radians(89.99)
			alpha = 0
			gamma = math.atan2(r12,r22)
		elif (beta < -math.radians(89.99)):
			beta = -math.radians(89.99)
			alpha = 0
			gamma = -math.atan2(r12,r22)
		else:
			cb = math.cos(beta)
			alpha = math.atan2(r21/cb,r11/cb)
			gamma = math.atan2(r32/cb,r33/cb)

			if(degrees == True):
				return [math.degrees(gamma),math.degrees(beta),math.degrees(alpha)]
			else:
				return [gamma,beta,alpha]








if __name__ == '__main__':
	IP="172.16.139.128"
	Modbus = Modbus_Communication(IP)
	registers_read = Modbus.Modbus_get_read_registers()
	#print("\n"*20)
	#print(registers_read)

	registers_write = Modbus.Modbus_get_write_registers()
	#print(registers_write)

	print("\n"*20)
	print("Indexes all registers")
	print(Modbus.Modbus_registers_all_ind)
	print("Indexes registers read")
	print(Modbus.Modbus_registers_read_ind)
	print("Indexes registers write")
	print(Modbus.Modbus_registers_write_ind)

	print("Adresses all registers")
	print(Modbus.Modbus_registers_all)
	print("Adresses read")
	print(Modbus.Modbus_registers_read)
	print("Adresses write")
	print(Modbus.Modbus_registers_write)

	print("Description all registers")
	print(Modbus.Modbus_registers_all_description)
	print("Data all registers")
	print(Modbus.Modbus_registers_all_data)


	Modbus.Modbus_Connect()
	print(Modbus.Modbus_registers_all[1])
	print(Modbus.Modbus_registers_all_description[1])
	print("Write 14")
	Modbus.Modbus_Request_to_write(Modbus.Modbus_registers_all[1],14,printb = True)
	time.sleep(1)
	value = Modbus.Modbus_Request_to_read(Modbus.Modbus_registers_all[1],printb = True)
	time.sleep(1)
	Modbus.Modbus_dataframe_update_read_registers(printb=False)
	Modbus.Modbus_df_reg.to_excel("Updated_Data.xlsx")
	Angles = Modbus.Modbus_get_joint_angles()
	Position = Modbus.Modbus_get_tcp_pos()

	print("Angles")
	print(Angles)
	print("Position")
	print(Position)
