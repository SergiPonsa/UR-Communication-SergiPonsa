#==============================================================================#
"""
Author: Sergi Ponsà Cobas
Version:2 Creation of a URScript class that allows as create an object with all the dashboard functions and variables
			That way we will able to have multiple robots , we only have to create one object for each robot
Version:1
Description: UR Script commands to send to the robot and teleoperate it via TCP/IP

Functions:
1-RemoteJointControl()[Movej] | 2-RemoteCartesianControl() [MoveL] | 3-SetFreeDrive() | 4-StopFreeDrive() |
5-GetActualJointPositions() | 6-GetActualTcpPose()| 7-RotVec2RPY() this functions are not created yet
"""
import socket
import time
import traceback

class URScript_Comands():

	#Variables set when we create the object
	def __init__(self, RobotIPURScript):
		self.RobotIPURScript=RobotIPURScript
		#//////////////////////////////////////////////////////////////////////////////#
		#Global Variables
		self.URScript_Connected=False
		self.URScript_sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)# The socket use IPv4 protocol & Provides sequenced, reliable, two-way, connection-based byte streams.
		self.URScript_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Sol_socket allows to read the socket options with getsockopt(), & SO_REUSEADDR means that a socket may bind, except when there is an active listening socket bound to the address
		self.URScript_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)#IPPROTO_TCP is a socket option that allows us to do modifications in our TCP protocol & TCP_NODELAY  This means that segments are always sent as soon as possible, even if there is only a small amount of data.
		self.URScript_sock.settimeout(2)# liberate the socket after 2 seconds if no data is recived or able to send

	#//////////////////////////////////////////////////////////////////////////////#
	def __enter__(self):
		self.URScript_Connect()
		return self

	def __exit__(self, exc_type, exc_value, tb):
		self.URScript_sock.close()
		if exc_type is not None:
			traceback.print_exception(exc_type, exc_value, tb)
			return False
	#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%#
	#functions

	def URScript_Connect(self):
		Port=30002
		Loop=True
		Counter=0
		while (Loop==True) :
			try:
				self.URScript_sock.connect((self.RobotIPURScript,Port))
				Loop=False
				self.URScript_Connected=True
			except:
				Counter+=1
				if  Counter>=3:
					print("TcpIP connection to Robot IP " ,self.RobotIPURScript," Failed")
					time.sleep(5.0)
					Loop=False
					self.URScript_Connected=False

	def URScript_SendCommand(self,cmd):
		print("Trying to send ",cmd)
		if self.URScript_Connected==True :
			try:
				self.URScript_sock.sendall(cmd.encode())
			except:
				self.URScript_Connect()
				try:
					self.URScript_sock.sendall(cmd.encode())
				except:
					print("Command",cmd," not send")
		else:
			self.URScript_Connect()
			try:
					self.URScript_sock.sendall(cmd.encode())
			except:
					print("Command",cmd," not send")

	def URScript_SetFreeDrive(self):

		#Create the function on the robot
		cmd =\
"""
def freedrive3():
	popup("Freedrive")
	freedrive_mode()
	while (True):
		sleep(1.0)
	end
end
"""
		self.URScript_SendCommand(cmd)

	def URScript_StopFreeDrive(self):
		#Create the function on the robot
		cmd =\
"""
def end_freedrive2():
	popup("End Freedrive")
	end_freedrive_mode()
	sleep(1.0)
end
"""

		self.URScript_SendCommand(cmd)
	def URScript_StopJoints(self, a=2):
		"""
		a: joint acceleration [rad/s^2]
		"""
		cmd =\
"""
"""+"stopj("+str(a)+""")
"""
		self.URScript_SendCommand(cmd)
	def URScript_MoveJoints(self,q,a=1.4, v=1.05,t=0,r=0):# Has to be tested
		"""
		q: is the joint position we want to move, we can also gie the pose p[] and the robot will do the inverse kinematics
		joint position [base,shoulder,elbow,w1,w2,w3]
		Robot pose p[x,y,z,ax,ay,az] (ax,ay,az, is the rotation vector not intutive we should use a funtion to transform RollPitchYaw to rotation vector)
		a: joint acceleration [rad/s^2]
		v: joint speed [rad/s]
		t: to specify the time to reach the point , then doesn't use the parameter a & v
		[s]
		r: to specify the blend radius[m]

		to use a and v , t=0
		"""
		cmd =\
"""
"""+"movej("+str(q)+",a="+str(a)+",v="+str(v)+",t="+str(t)+",r="+str(r)+""")
"""
		self.URScript_SendCommand(cmd)
	def URScript_MoveToPoseJointSpaceBaseFrame(self,pose,a=1.3962634015954636, v=1.0471975511965976,t=0,r=0):
		"""
		pose: is the robot pose
		Robot pose p[x,y,z,ax,ay,az] (ax,ay,az, is the rotation vector not intutive we use a funtion to transform RollPitchYaw to rotation vector)
		a: tool acceleration [m/s^2]
		v: tool speed [m/s]
		t: to specify the time to reach the point , then doesn't use the parameter a & v
		[s]
		r: to specify the blend radius[m]

		to use a and v , t=0
		"""

		#Function already created and we only have to call it
		cmd=\
"""
def movej_pose_base_frame():

	ori_rv = rpy2rotvec("""+str(pose[3:])+""")
	q=get_inverse_kin(p["""+str(pose[0])+","+str(pose[1])+","+str(pose[2])+""",ori_rv[0],ori_rv[1],ori_rv[2]])
	movej(q,a="""+str(a)+",v="+str(v)+",t="+str(t)+",r="+str(r)+""")
end
"""
		self.URScript_SendCommand(cmd)
	def URScript_MoveToPoseJointSpaceToolFrame(self,pose,a=1.3962634015954636, v=1.0471975511965976,t=0,r=0):#Has to be tested
		"""
		pose: is the robot pose
		Robot pose p[x,y,z,ax,ay,az] (ax,ay,az, is the rotation vector not intutive we use a funtion to transform RollPitchYaw to rotation vector)
		a: tool acceleration [m/s^2]
		v: tool speed [m/s]
		t: to specify the time to reach the point , then doesn't use the parameter a & v
		[s]
		r: to specify the blend radius[m]

		to use a and v , t=0
		"""

		#Function already created and we only have to call it
		cmd=\
"""
def movej_pose_tool_frame():

	ori_rv = rpy2rotvec("""+str(pose[3:])+""")
	tcp_pose = get_actual_tcp_pose()
	pose = pose_trans(tcp_pose,p["""+str(pose[0])+","+str(pose[1])+","+str(pose[2])+""",ori_rv[0],ori_rv[1],ori_rv[2]])
	q=get_inverse_kin(pose)
	movej(q,a="""+str(a)+",v="+str(v)+",t="+str(t)+",r="+str(r)+""")

end
"""
		self.URScript_SendCommand(cmd)
	def URScript_RemoteJointControl(self,q,a=1.4, v=1.05,t=0.008):# Has to be tested
		"""
		q: is the joint position we want to move, we can also gie the pose p[] and the robot will do the inverse kinematics
		joint position [base,shoulder,elbow,w1,w2,w3]
		Robot pose p[x,y,z,ax,ay,az] (ax,ay,az, is the rotation vector not intutive we should use a funtion to transform RollPitchYaw to rotation vector)
		a: joint acceleration [rad/s^2]
		v: joint speed [rad/s]
		t: to specify the time to reach the point , then doesn't use the parameter a & v
		[s]
		r: to specify the blend radius[m]

		to use a and v , t=0
		"""

		#Function already created and we only have to call it
		cmd=\
"""
def RemoteJointControl():
	while(True):
		des_pos_j ="""+"["+str(q[0])+","+str(q[1])+","+str(q[2])+","+str(q[3])+","+str(q[4])+","+str(q[5])+"]"+ """
		act_pos_j = get_actual_joint_positions()
		difference = [des_pos_j[0]-act_pos_j[0],des_pos_j[1]-act_pos_j[1],des_pos_j[2]-act_pos_j[2],des_pos_j[3]-act_pos_j[3],des_pos_j[4]-act_pos_j[4],des_pos_j[5]-act_pos_j[5]]
		count = 0
		Maximum_angle_safe = 5
		servo = True
		look_ahead=0.2
		gain=100
		"""+"t ="+str(t)+"""
		"""+"a ="+str(a)+"""
		"""+"q ="+str(q)+"""
		"""+"v ="+str(v)+"""

		while (count<6):
			if (norm(difference[count])> Maximum_angle_safe):
				servo = False
			end
			count = count + 1
		end
		if(servo == True):
			servoj(q,t=t,lookahead_time=look_ahead,gain=gain)
		else:
			movej(q,a=a,v=v)

		end
	end
end
"""

		self.URScript_SendCommand(cmd)

	def URScript_RemoteCartesianControl(self,pose,a=1.4, v=1.05,t=0.008,tool=False):#Has to be tested
		"""
		pose: is the robot pose
		Robot pose p[x,y,z,ax,ay,az] (ax,ay,az, is the rotation vector not intutive we should use a funtion to transform RollPitchYaw to rotation vector, in radians)
		a: tool acceleration [m/s^2]
		v: tool speed [m/s]
		t: to specify the time to reach the point , then doesn't use the parameter a & v
		[s]
		r: to specify the blend radius[m]

		to use a and v , t=0
		"""
		cmd=\
"""
def RemoteCartesianControl():
	while(True):
		"""+"t ="+str(t)+"""
		"""+"a ="+str(a)+"""
		"""+"v ="+str(v)+"""
		ori_rv = rpy2rotvec("""+str(pose[3:])+""")
		"""+"tool="+str(tool)+"""
		if(tool==True):
			tcp_pose = get_actual_tcp_pose()
			pose = pose_trans(tcp_pose,p["""+str(pose[0])+","+str(pose[1])+","+str(pose[2])+""",ori_rv[0],ori_rv[1],ori_rv[2]])
		else:
			pose = p["""+str(pose[0])+","+str(pose[1])+","+str(pose[2])+""",ori_rv[0],ori_rv[1],ori_rv[2]]
		end
		des_pos_j = get_inverse_kin(pose)
		act_pos_j = get_actual_joint_positions()
		difference = [des_pos_j[0]-act_pos_j[0],des_pos_j[1]-act_pos_j[1],des_pos_j[2]-act_pos_j[2],des_pos_j[3]-act_pos_j[3],des_pos_j[4]-act_pos_j[4],des_pos_j[5]-act_pos_j[5]]
		count = 0
		Maximum_angle_safe = 5
		servo = True
		look_ahead=0.2
		gain=100


		while (count<6):
			if (norm(difference[count])> Maximum_angle_safe):
				servo = False
			end
			count = count + 1
		end
		if(servo == True):
			servoj(des_pos_j,t=t,lookahead_time=look_ahead,gain=gain)
		else:
			movej(des_pos_j,a=a,v=v)

		end
	end
end
"""
		self.URScript_SendCommand(cmd)
	def URScript_RemoteCartesianControl_offset(self,pose,a=1.4, v=1.05,t=0.4,tool=False):#Has to be tested
		"""
		pose: is the robot pose
		Robot pose p[x,y,z,ax,ay,az] (ax,ay,az, is the rotation vector not intutive we should use a funtion to transform RollPitchYaw to rotation vector, in radians)
		a: tool acceleration [m/s^2]
		v: tool speed [m/s]
		t: to specify the time to reach the point , then doesn't use the parameter a & v
		[s]
		r: to specify the blend radius[m]

		to use a and v , t=0
		"""
		cmd=\
"""
def RemoteCartesianControl():
	"""+"t ="+str(t)+"""
	"""+"a ="+str(a)+"""
	"""+"v ="+str(v)+"""

	"""+"tool="+str(tool)+"""
	tcp_pose = get_actual_tcp_pose()

	if(tool==True):
		ori_rv = rpy2rotvec("""+str(pose[3:])+""")
		pose = pose_trans(tcp_pose,p["""+str(pose[0])+","+str(pose[1])+","+str(pose[2])+""",ori_rv[0],ori_rv[1],ori_rv[2]])
	else:
		pose_x ="""+str(pose[0])+""" + tcp_pose[0]
		pose_y ="""+str(pose[1])+""" + tcp_pose[1]
		pose_z ="""+str(pose[2])+""" + tcp_pose[2]

		ori_tcp_rpy = rotvec2rpy([tcp_pose[3],tcp_pose[4],tcp_pose[5]])

		ori_rx = ori_tcp_rpy[0] + """+str(pose[3])+"""
		ori_ry = ori_tcp_rpy[1] + """+str(pose[4])+"""
		ori_rz = ori_tcp_rpy[2] + """+str(pose[5])+"""

		ori_rv = rpy2rotvec([ori_rx,ori_ry,ori_rz])

		pose = p[ pose_x,pose_y,pose_z,ori_rv[0],ori_rv[1],ori_rv[2] ]

	end
	des_pos_j = get_inverse_kin(pose)
	act_pos_j = get_actual_joint_positions()
	difference = [des_pos_j[0]-act_pos_j[0],des_pos_j[1]-act_pos_j[1],des_pos_j[2]-act_pos_j[2],des_pos_j[3]-act_pos_j[3],des_pos_j[4]-act_pos_j[4],des_pos_j[5]-act_pos_j[5]]
	count = 0
	Maximum_angle_safe = 5
	servo = True
	look_ahead=0.2
	gain=100


	while (count<6):
		if (norm(difference[count])> Maximum_angle_safe):
			servo = False
		end
		count = count + 1
	end
	if(servo == True):
		servoj(des_pos_j,t=t,lookahead_time=look_ahead,gain=gain)
	else:
		movej(des_pos_j,a=a,v=v)

	end
end
"""
		self.URScript_SendCommand(cmd)

	def URScript_ScriptFile(self,FilePath):#Has to be tested
		File = open(FilePath,"r")
		cmd = File.read()
		self.URScript_SendCommand(cmd)

if __name__ == '__main__':

	communication = URScript_Comands("172.16.139.128")
	communication.URScript_Connect()
