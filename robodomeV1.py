import sys
from time import sleep
import serial
import datetime as dt
import ephem

######To Do######
# Check full movement cycle
# Determine error in move function
# Upload to Bitbucket
# User manual
# Look into Work study at U of T (CLN), SURF, Datakind

class Dome:
    '''This is the virtual representation of the robodome,
    connecting the python program to the electronics.'''

    def __init__(self):
        self.tty=serial.Serial('COM3', 9600, timeout=2)
        self.shutter = 'Unknown'
        self.az = 'Unknown'


    def readfrom(self):
        ''' This is a method of reading information from the dome 
        serial cable. If nothing is received for 2 seconds, bail.  
        But if anything is received, then keep listening until you 
        get a full response GINF statement.

        See documentation for ROBODOME
        
        '''
            
        start = dt.datetime.now()
        loop = True        
        command = False
        text = ''
        print ''
        while loop:
                                    
            n = self.tty.inWaiting()
            if n != 0:
                command = True
                text = text + self.tty.read(n)
                temp = text.split('\r')
                if temp[-1] == '' and len(temp) > 1:
                    #print '\033[1F\033[K'+temp[-2]
                    print temp[-2]
                    if len(temp[-2]) > 30:
                        ## This separates out smaller communication
                        ## from a full GINF response.
                        #print temp
                        return 1,temp[-2]
            if command == False:
                interval = dt.datetime.now() - start
                if interval.seconds > 2:
                    loop = False
            sleep(0.01)

        return 0,'none'

            
    def write_command(self,param):
        print 'Sending {0}'.format(param)
        self.tty.write(param)




def parseinfo(message):
    text = message.split(',')
    dome.az = round(359. * float(text[4]) / float(text[1]),1)
    temp = int(text[6])
    if temp == 1:
        dome.shutter = 'Closed'
    elif temp == 2:
        dome.shutter = 'Opened'
    else:
        dome.shutter = 'Unknown'
    print 'Current Dome Status:\n\tShutter: {0}\n\tAzimuth: {1}'.format(dome.shutter, dome.az)

def move(position):#check if in position multiple times maybe
	hundreds = int(position/100)
	tens = (int((position-100*hundreds)/10))
	ones = int(position-100*hundreds-10*tens)
	location = 'G'+str(hundreds)+str(tens)+str(ones)
	dome.write_command(location) 
	return
	
def weatherTimeAccurate(vaisalaTime):
	return True #remove when doing real-time
	'''dTime = dt.datetime.utcnow()
	dTime = dTime.strftime("%H:%M:%S")
	#print dTime
	h1, m1 , s1 = map(float, vTime.split(':'))
	h2, m2, s2 = map(float, dTime.split(':'))
	if abs((s1 + 60*(m1 + 60*h1))-(s2 + 60*(m2+ 60*h2)))>=5:
		return False
	else:
		return True'''
	
	
def goodWeather():
	return True #for testing
	'''print "\nChecking weather..."
	file = open("vaisalaData.txt", "r")
	line_list = file.readlines()
	last_line = line_list[-1]
	file.close()
	lineArr = last_line.split(",")
	if weatherTimeAccurate(lineArr[1]) == False:
		print "\nVaisala Time error, offset by more than 5 minutes"
		print "\nPlease check the Vaisala Reader"
		return False
	elif float(lineArr[6]) >=10: #arr[6]=wsavg, 7=wsmax, 9=RH, 13=rainintensity 
		print "\nAverage windspeed too high"
		return False
	elif float(lineArr[7]) >=15:
		print "\nMax windpeed too high"
		return False
	elif float(lineArr[9]) >=90:
		print "\nMax humidity too high"
		return False
	elif float(lineArr[13]) >0:
		print "\nRain Detected"
		return False
	else:
		return True'''


def positionAccurate(azimuth):
	print "\nChecking position..."
	print "\nSun Position %s" %(57.2958*float(azimuth))
	print "\nDome Position %s" %(dome.az)
	
	if abs(57.2958*float(azimuth) - float(dome.az))>2: #change back to 10
		return False
	else:
		return True

		
def checkMovement(position):
	count = 0;
	while positionAccurate(position)==False and count <=5:
		move(position)
		sleep(10)
	
def automate():
	pos = ephem.city("Toronto")#need to enter exact coordinates
	sun = ephem.Sun()
	timer = 0

	try:
		sun.compute(pos)
		if dome.shutter == 'Unknown':
			dome.write_command('GHOM')
			sleep(30)
			dome.write_command('GCLS')
			sleep(30)
		if goodWeather() == True and dome.shutter == 'Closed' and sun.alt>0:
			dome.write_command("GOPN")
			sleep(30) 
			move(sun.az)
			sleep(30)
			timer +=1
		while True:
			print "\nAutomation has been running for approximately %d minutes" %(timer)
			pos.date = ephem.now()

			sun.compute(pos)
			dome.write_command('GINF')
			result,message = dome.readfrom()
			if result == 1:
				parseinfo(message)
			else:
				print '\t Contact Failed.  Dome status unknown.'
			if dome.shutter == 'Opened':
				if sun.alt <0:
					dome.write_command('GCLS')
					for i in range(60):
						sleep(1)
					print "\nNight time -- Dome closed"
				elif goodWeather() == False:
					dome.write_command('GCLS')
					sleep(30)
					print "\nPoor weather conditions detected -- Dome closed"
				elif timer%5==0 and positionAccurate(sun.az) == False and goodWeather()==True: 
					move(57.2958*float(sun.az))
					sleep(30)
					print "dome moved"
				for i in range(60):
					sleep(1) #enables keyboardinterrupt to be processed right away
				timer += 1
				
			else:
				if goodWeather() == True  and sun.alt>0: #separate bad weather/night
					dome.write_command("GOPN")
					for i in range(30):
						sleep(1)
					move(sun.az)
					sleep(30)
					timer+=1
				else:
					timer += 10
					for i in range(600):
						sleep(1)
			
			
			
		
	except KeyboardInterrupt:
		print "\nKeyboardInterrupt -- exiting automation"
		print "\nAutomation has terminated at approximately %d minutes" %(timer)
		return
	

if __name__ == '__main__':
	
	dome = Dome() 
	leave_loop = False
	print '\n\nrobodome_comm_v2.py\n----'

    ## Clear Serial Line
	dome.tty.read(dome.tty.inWaiting())
    
	## Do an inital check of the dome status.
	dome.write_command('GINF')
	result,message = dome.readfrom()
	if result == 1:
        #print message
		parseinfo(message)
	else:
		print '\tInitial Contact Failed.  Dome status unknown.'


    ## Loop until user quits.
	while not leave_loop:
		try:
			command = raw_input('\nWhat next? (q to quit): ')
			if  command in ['q','Q']:
				leave_loop = True
			elif command in ['a','A']:
				automate()
			else:
				dome.write_command(command)
				result,message = dome.readfrom()
				if result == 0:
					print '\tNO RESPONSE...'
				else:
                    #print message
					parseinfo(message)
		except KeyboardInterrupt:
			print '\nUSER INTERRUPT -- Sending all stop command'
			dome.write_command('GINF')
			result,message = dome.readfrom()
			if result == 0:
				print '\tNO RESPONSE...'
			else:
                #print message
				parseinfo(message)
		except:
			raise
           
	sys.exit()
