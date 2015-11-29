import socket 

import MergeSort    #Imports mergesort functions 
import random 
import time

import argparse

# argument parser
parser = argparse.ArgumentParser(description="Demonstration of Ditributed Computing")

# positional arguments

# optional arguments
parser.add_argument("-n", "--nodes", help="Specify number of nodes in cluster", type=int, default=1)
parser.add_argument("-s", "--size", help="Sets the size of the array to be sorted", type=int, default=100000)

args = parser.parse_args()





#breaks down array into n sections where n is the number of processors 
def breakarray(array, n): 


    sectionlength = len(array)/n    #length of each section 

    result = [] 

    for i in range(n):

        if i < n - 1:
            result.append( array[ i * sectionlength : (i+1) * sectionlength ] )
            #include all remaining elements for the last section 
        else:
            result.append( array[ i * sectionlength : ] )

    return result

#Create an array to be sorted 
arraylength = args.size    #Length of array to be sorted 
print 'Length of array is', arraylength 
array = range(arraylength)  #Creates array 
random.shuffle(array)   #Jumbles up array 


#Specify info on processors/computers 
procno = args.nodes  #number of processors 
print 'Number of processors:', procno 
procID = 0  #ID of this processor(server) 
addr_list = []  #list of client addresses
conn_list = []

if procno == 1:
    # for a single node, just sort array and time process
    start_time = time.time()
    print 'Sorting array . . .'
    array = MergeSort.mergesort(array)
    print 'Array sorted'
    
    time_taken = time.time() - start_time

    print 'Time taken to sort is ', time_taken, 'seconds.'

elif procno > 1:
    # for multiple nodes

    #Sets up network 
    HOST = '' 
    PORT = 50007 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    s.bind((HOST, PORT)) 

    s.listen(procno - 1)    #Listens for (n) number of client connections 
    #print 'Waiting for {}  client/s...'.format(proco-1-i) 

    for i in range(procno - 1): #Connects to all clients
        
        print 'Waiting for {}  client/s...'.format(procno-1-i) 
        conn, addr = s.accept() #Accepts connection from client
        # issue was here: conn is overwritten by the second connection, so the first client connection falls away
        # this is a crude method using multiple connection, other solutions exist
        # could possibly be sped up with threads?

        print 'Connected by', addr 
        addr_list.append(addr)  #Adds address to address list
        conn_list.append(conn)

    print addr_list
    print 'All clients connected. Proceeding to ditribute workload . . .'

    #Start and time distributed computing sorting process   
    start_time = time.time()    #Records start time 

    sections = breakarray(array, procno)    #splits array into sections for every client 

    for i in range(procno - 1): #Converts array section into string to be sent

        arraystring = repr(sections[i+1]) 
        conn_list[i].sendto( arraystring , addr_list[i] )   #Sends array string
        #print 'Data: {}'.format(arraystring)
        print 'Data sent to {}, sorting array...'.format(addr_list[i])

    array = MergeSort.mergesort(sections[procID])   #Sorts section and stores it in array 
    print 'Array sorted.' 

    for i in range(procno - 1): #Receives sorted sections from each client

        arraystring = '' 
        print 'Receiving data from clients...' 
        while 1:
            # same issue as above here. Seperate conn is required for each client. TCP protocol is used. Maybe try UDP?
            data = conn_list[i].recv(4096)  #Receives data in chunks 
            arraystring += data #Adds data to array string 
            if ']' in data: #When end of data is received

                break
        print 'Data received, merging arrays...'    
        array = MergeSort.merge(array, eval(arraystring))   #Merges current array with section from client  
        print 'Arrays merged.'

    conn.close() 
    time_taken = time.time() - start_time   #Calculates and records time_taken 

    print 'Time taken to sort is ', time_taken, 'seconds.'

else:
    print 'Invalid number of nodes'
