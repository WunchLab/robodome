# This file is to simulate Vaisala Data
# Opens a set txt file and imputs its lines at a rate to another file, dataLive
# The dataLive.txt file will be the active vaisala data that my code will read

import sys
import datetime as dt
from time import sleep
'''
def convertMatrix(content):
	contentMat = []
	for line in content:
		lineList=line.split(",")
		contentMat.append(lineList)
	return contentMat
'''
#convertMatrix better for interpreting data, not writing
def writeLive(content):
	for i in range(1,len(content)-1):
		arr1 = content[i].split(",")
		arr2 = content[i+1].split(",")
		h1, m1 , s1 = map(float, arr1[1].split(':'))
		h2, m2, s2 = map(float, arr2[1].split(':'))
		time_diff = (s2 + 60*(m2+ 60*h2))-(s1 + 60*(m1 + 60*h1))
		print str(content[i])+"\r\n"

		data=open("vaisalaData.txt","a")
		data.write(content[i])
		data.close()
		sleep(time_diff)
		i+=1
	return
	
if __name__ == '__main__':
	file = open("exampleData.txt","r")
	content = file.readlines()
	create = open("vaisalaData.txt","w+")
	create.close()
	writeLive(content)
