"""
Simulation of Alibaba Call Center
Input Distributions:
    1- Entering population: poisson with mean = 3 people per hour
        (Inter-arrival time: Exponential with mean = 20 minutes)
    2- Service time: uniform(10, 25) minutes
No limits on queue length
People get served based on a FIFO discipline
Outputs:
    1- Average queue length
    2- Average waiting time in queue
    3- Server utilization
System starts at an empty state

Author: A. Hajibeygi - A. Imankhan
Date: 24 June 2022
"""

import math
import random
import pandas as pd


#Parameters of Distributions
params = list()
for i in range(4):
    params.append(0)
params[1]= 1/3 #Will Use for Exponential Ditribution
params[2]= 1 #Will Use for Exponential Ditribution
params[3]= 1/2 #Will Use for Exponential Ditribution


#Create Uniform Distributed Variables
def uniform(a, b):
    r = random.random()
    return a + (b - a) * r


#Crate Exponential Distributed Varibles
def exponential(lambd):
    r = random.random()
    return -(1 / lambd) * math.log(1 - r,math.e)


def starting_state():
    
    #State Variables
    state = dict()
    state['Available VIP Cashiers'] = 2 #Number of available vip cashiers: Known as VC -> 0 ,1 ,2
    state['Available Junior Cashiers'] = 3 #Number of available juniro cashiers: Known as JC -> 0 ,1 ,2 ,3
    state['Available Technical Cashiers'] = 2 #Number of available technical cashiers: Known as TC -> 0 ,1 ,2
    state['Current Shift'] = 3 #Current Shift -> 1 ,2 ,3

    # Data: will save everything
    data = dict()
    data['Customers'] = dict()  # To track each customer, saving their arrival time, time service begins, etc.
    
    # Customer: Arrival Time, used to find first customer in queue
    data['Queue VIP Customers'] = dict() 
    data['Queue Normal Customers'] = dict() 
    data['Queue VIP Recall Customers'] = dict() 
    data['Queue Normal Recall Customers'] = dict() 
    data['Queue Technical Customers'] = dict()

    # Cumulative Stats
    data['Cumulative Stats'] = dict()
    data['Cumulative Stats']['Number of VIP Customers'] = 0
    data['Cumulative Stats']['Number of Normal Customers'] = 0
    data['Cumulative Stats']['Number of VIP Technical Customers'] = 0
    data['Cumulative Stats']['Number of Normal Technical Customers'] = 0

    data['Cumulative Stats']['Number of Non Waiting VIP Customers'] = 0
    data['Cumulative Stats']['Number of Non Waiting Normal Customers'] = 0

    data['Cumulative Stats']['Time in System of VIP Customer'] = 0

    data['Cumulative Stats']['Max VIP Queue Lenght'] = 0
    data['Cumulative Stats']['Max Normal Queue Lenght'] = 0
    data['Cumulative Stats']['Max VIP Recall Queue Lenght'] = 0
    data['Cumulative Stats']['Max Normal Recall Queue Lenght'] = 0
    data['Cumulative Stats']['Max Technical Queue Lenght'] = 0

    data['Cumulative Stats']['Max VIP Waiting Time'] = 0
    data['Cumulative Stats']['Max Normal Waiting Time'] = 0

    data['Cumulative Stats']['VIP Cashier Busy Time'] = 0
    data['Cumulative Stats']['Junior Cashier Busy Time'] = 0
    data['Cumulative Stats']['Technical Cashier Busy Time'] = 0

    data['Cumulative Stats']['Number of Served VIP Customers'] = 0
    data['Cumulative Stats']['Number of Served Normal Customers'] = 0
    data['Cumulative Stats']['Number of Served VIP Technical Customers'] = 0
    data['Cumulative Stats']['Number of Served Normal Technical Customers'] = 0

    data['Cumulative Stats']['Total VIP Waiting Time'] = 0
    data['Cumulative Stats']['Total Normal Waiting Time'] = 0
    data['Cumulative Stats']['Total Technical Waiting Time'] = 0

    data['Cumulative Stats']['Area Under VIP Queue Length Curve'] = 0
    data['Last Time VIP Queue Length Changed'] = 0
    data['Cumulative Stats']['Area Under Normal Queue Length Curve'] = 0
    data['Last Time Normal Queue Length Changed'] = 0
    data['Cumulative Stats']['Area Under Technical Queue Length Curve'] = 0
    data['Last Time Technical Queue Length Changed'] = 0
    data['Cumulative Stats']['Area Under VIP Recall Queue Length Curve'] = 0
    data['Last Time VIP Recall Queue Length Changed'] = 0
    data['Cumulative Stats']['Area Under Normal Recall Queue Length Curve'] = 0
    data['Last Time Normal Recall Queue Length Changed'] = 0


    #Starting FEL
    future_event_list = list()

    #First Arrival
    future_event_list.append({'Event Type': 'Arrival', 'Event Time': 0, 'Customer': 'C1'})

    #First Malfunction
    n = random.randint(1, 30)
    future_event_list.append({'Event Type': 'Malfunction', 'Event Time': n * 1440, 'Customer': None})

    #First Shift Change
    future_event_list.append({'Event Type': 'Change Shift', 'Event Time': 0, 'Customer': None})

    return state, future_event_list, data


# Gets an Event Type
# Generates activity time for that particular Event Type
# Creates an event (or more precisely an event notice)
# Appends the event to FEL
def fel_maker(future_event_list, type, state, clock, data, customer=None):
    
    event_time = 0

    #Arrival event maker
    #Diffrent distribution affects the time based on shift
    if type == "Arrival":
        if state['Current Shift'] == 1:
            event_time = clock + exponential(params[1])
        elif state['Current Shift'] == 2:
            event_time = clock + exponential(params[2])
        elif state['Current Shift'] == 3:
            event_time = clock + exponential(params[3])

    #Service event maker
    if type == "Service":
        event_time = clock

    #End of Service event maker
    if type == "End of Service":
        if (data['Customers'][customer]['Service Type'] == "Junior"):
            event_time = clock + exponential(1/7)
        else:
            event_time = clock + exponential(1/3)

    #Leave the Queue event maker
    if type == "Leave the Queue":
        if (data['Customers'][customer]['Type'] == "Normal"):
            event_time = clock + uniform(5, len(data['Queue Normal Customers']))
        else:
            event_time = clock + uniform(5, len(data['Queue VIP Customers']))

    #Technical Arrival event maker
    if type == "Technical Arrival":
        event_time = clock

    #Technical Service event maker
    if type == "Technical Service":
        event_time = clock

    #End of Technical Service event maker
    if type == "End of Technical Service":
        event_time = clock + exponential(1/10)

    #Change Shift event maker
    if type == "Change Shift":
        event_time = clock + 480

    #Recall event maker
    #TODO
    if type == "Recall":
        event_time = clock

    #System Malfunction event maker
    if type == "Malfunction":
        r = random.randint(1,30)
        f = 43200 - (clock % 43200)
        n = f + (r * 1440)
        event_time = clock + n


    #End of System Malfunction event maker
    if type == "End of System Malfunction":
        event_time = clock + 1440

    new_event = {'Event Type': type, 'Event Time': event_time, 'Customer': customer}
    future_event_list.append(new_event)


def arrival(future_event_list, state, clock, data, customer):
    #Handle arrival of a customer

    data['Customers'][customer] = dict()
    data['Customers'][customer]['Is Recall'] = 0
    data['Customers'][customer]['Arrival Time'] = clock  # track every move of this customer
    data['Customers'][customer]['Time Service Begins'] = None # make start time none for every customer to make sure they service time is not started yet
    data['Customers'][customer]['Has Waiting'] = 0

    #70% of customers are Normal and 30% of them are VIP
    r = random.random()
    
    #VIP Customer
    if r < 0.3:
        data['Cumulative Stats']['Number of VIP Customers'] += 1
        data['Customers'][customer]['Type'] = "VIP"
        if state['Available VIP Cashiers'] > 0:  # if we have free VIP cashiers
            data['Customers'][customer]['Service Type'] = "VIP"
            data['Cumulative Stats']['Number of Non Waiting VIP Customers'] += 1
            fel_maker(future_event_list, 'Service', state, clock, data, customer)
        else:
            r_recall = random.random()
            data['Customers'][customer]['Has Waiting'] = 1
            if (len(data['Queue VIP Customers']) > 5) and (r_recall < 0.5):
                data['Queue VIP Recall Customers'][customer] = clock
                data['Cumulative Stats']['Area Under VIP Recall Queue Length Curve'] += len((data['Queue VIP Recall Customers'])) * (clock - data['Last Time VIP Recall Queue Length Changed'])
                data['Last Time VIP Recall Queue Length Changed'] = clock
                if (data['Cumulative Stats']['Max VIP Recall Queue Lenght'] < len(data['Queue VIP Recall Customers'])):
                    data['Cumulative Stats']['Max VIP Recall Queue Lenght'] = len(data['Queue VIP Recall Customers'])

            else:
                r_leave = random.random()
                data['Cumulative Stats']['Area Under VIP Queue Length Curve'] += len((data['Queue VIP Customers'])) * (clock - data['Last Time VIP Queue Length Changed'])
                data['Last Time VIP Queue Length Changed'] = clock
                data['Queue VIP Customers'][customer] = clock
                if (data['Cumulative Stats']['Max VIP Queue Lenght'] < len(data['Queue VIP Customers'])):
                    data['Cumulative Stats']['Max VIP Queue Lenght'] = len(data['Queue VIP Customers'])
                if (r_leave < 0.15):
                    fel_maker(future_event_list, 'Leave the Queue', state, clock, data, customer)
                    


    #Normal Cutomer        
    else:
        data['Cumulative Stats']['Number of Normal Customers'] += 1
        data['Customers'][customer]['Type'] = "Normal"
        if state['Available Junior Cashiers'] > 0:  # if we have free Juniors cashiers
            data['Customers'][customer]['Service Type'] = "Junior"
            data['Cumulative Stats']['Number of Non Waiting Normal Customers'] += 1
            fel_maker(future_event_list, 'Service', state, clock, data, customer)
        elif state['Available VIP Cashiers'] > 0:  # if we have free VIP cashiers:
            data['Customers'][customer]['Service Type'] = "VIP"
            data['Cumulative Stats']['Number of Non Waiting Normal Customers'] += 1
            fel_maker(future_event_list, 'Service', state, clock, data, customer)
        else:
            r_recall = random.random()
            data['Customers'][customer]['Has Waiting'] = 1
            if (len(data['Queue Normal Customers']) > 5) and (r_recall < 0.5):
                data['Queue Normal Recall Customers'][customer] = clock
                data['Cumulative Stats']['Area Under Normal Recall Queue Length Curve'] += len((data['Queue Normal Recall Customers'])) * (clock - data['Last Time Normal Recall Queue Length Changed'])
                data['Last Time Normal Recall Queue Length Changed'] = clock
                if (data['Cumulative Stats']['Max Normal Recall Queue Lenght'] < len(data['Queue Normal Recall Customers'])):
                    data['Cumulative Stats']['Max Normal Recall Queue Lenght'] = len(data['Queue Normal Recall Customers'])

            else:
                r_leave = random.random()
                data['Cumulative Stats']['Area Under Normal Queue Length Curve'] += len((data['Queue Normal Customers'])) * (clock - data['Last Time Normal Queue Length Changed'])
                data['Last Time Normal Queue Length Changed'] = clock
                data['Queue Normal Customers'][customer] = clock
                if (data['Cumulative Stats']['Max Normal Queue Lenght'] < len(data['Queue Normal Customers'])):
                    data['Cumulative Stats']['Max Normal Queue Lenght'] = len(data['Queue Normal Customers'])
                if (r_leave < 0.15):
                    fel_maker(future_event_list, 'Leave the Queue', state, clock, data, customer)

    # Scheduling the next arrival
    # We know the current customer
    # Who will be the next customer? (Ex.: Current Customer = C1 -> Next Customer = C2)
    next_customer = 'C' + str(int(customer[1:]) + 1)
    fel_maker(future_event_list, 'Arrival', state, clock, data, next_customer)


#Get Service at t
def service(future_event_list, state, clock, data, customer):
    #Check if customer is still in Queue
    if (customer in data['Customers']):

        #Start time of Service records in data
        data['Customers'][customer]['Time Service Begins'] = clock

        #Check the type of customer
        if (data['Customers'][customer]['Type'] == "Normal"):
            data['Queue Normal Customers'].pop(customer, None) #Remove the customer from the Queue due start of service
        elif (data['Customers'][customer]['Type'] == "VIP") :
            data['Queue VIP Customers'].pop(customer, None) #Remove the customer from the Queue due start of service

        #Check service type
        if (data['Customers'][customer]['Service Type'] == "Junior"):
            state['Available Junior Cashiers'] -= 1
            
        else:
            state['Available VIP Cashiers'] -= 1

        #Create an "End of Service" event for this service
        fel_maker(future_event_list, "End of Service", state, clock, data, customer)


#End of Sevice at t
def end_of_service(future_event_list, state, clock, data, customer):
    
    first_cutomer_in_queue = None
    flag = 0
    tech_support = False
    #End time of Service records in data
    data['Customers'][customer]['End of Service Time'] = clock
    data['Customers'][customer]['Waiting Time'] = (data['Customers'][customer]['End of Service Time'] - data['Customers'][customer]['Arrival Time'])
    if (data['Customers'][customer]['Type'] == "VIP"):
        data['Cumulative Stats']['Number of Served VIP Customers'] += 1
        if (data['Customers'][customer]['Is Recall'] == 0):
            data['Cumulative Stats']['Total VIP Waiting Time'] += data['Customers'][customer]['Waiting Time']
            data['Cumulative Stats']['Time in System of VIP Customer'] += data['Customers'][customer]['Waiting Time']
        else:
            data['Cumulative Stats']['Area Under VIP Recall Queue Length Curve'] += len((data['Queue VIP Recall Customers'])) * (clock - data['Last Time VIP Recall Queue Length Changed'])
            data['Last Time VIP Recall Queue Length Changed'] = clock
        data['Cumulative Stats']['Area Under VIP Queue Length Curve'] += len((data['Queue VIP Customers'])) * (clock - data['Last Time VIP Queue Length Changed'])
        data['Last Time VIP Queue Length Changed'] = clock
        if (data['Cumulative Stats']['Max VIP Waiting Time'] < data['Customers'][customer]['Waiting Time']):
            data['Cumulative Stats']['Max VIP Waiting Time'] = data['Customers'][customer]['Waiting Time']
    else:
        data['Cumulative Stats']['Number of Served Normal Customers'] += 1
        if (data['Customers'][customer]['Is Recall'] == 0):
            data['Cumulative Stats']['Total Normal Waiting Time'] += data['Customers'][customer]['Waiting Time']
            data['Cumulative Stats']['Area Under Normal Queue Length Curve'] += len((data['Queue Normal Customers'])) * (clock - data['Last Time Normal Queue Length Changed'])
        else:
            data['Cumulative Stats']['Area Under Normal Recall Queue Length Curve'] += len((data['Queue Normal Recall Customers'])) * (clock - data['Last Time Normal Recall Queue Length Changed'])
            data['Last Time Normal Recall Queue Length Changed'] = clock
        data['Last Time Normal Queue Length Changed'] = clock
        if (data['Cumulative Stats']['Max Normal Waiting Time'] < data['Customers'][customer]['Waiting Time']):
            data['Cumulative Stats']['Max Normal Waiting Time'] = data['Customers'][customer]['Waiting Time']


    #Check type of service
    #VIP Service Type
    if (data['Customers'][customer]['Service Type'] == "VIP"):
        state['Available VIP Cashiers'] += 1
        data['Cumulative Stats']['VIP Cashier Busy Time'] += (clock - data['Customers'][customer]['Time Service Begins'])

        #Will the customer need Technical Service?
        r = random.random()

        if r < 0.15: #Needs Technical Support
            fel_maker(future_event_list, "Technical Arrival", state, clock, data, customer)
            tech_support = True
        
        #Who served next?
        if (len(data['Queue VIP Customers']) != 0):
            first_cutomer_in_queue = min(data['Queue VIP Customers'], key=data['Queue VIP Customers'].get)
            flag = 1
        elif (len(data['Queue Normal Customers']) != 0):
            first_cutomer_in_queue = min(data['Queue Normal Customers'], key=data['Queue Normal Customers'].get)
            flag = 2
        elif (len(data['Queue VIP Recall Customers']) != 0):
            first_cutomer_in_queue = min(data['Queue VIP Recall Customers'], key=data['Queue VIP Recall Customers'].get)
            flag = 3
        elif (len(data['Queue Normal Recall Customers']) != 0):
            first_cutomer_in_queue = min(data['Queue Normal Recall Customers'], key=data['Queue Normal Recall Customers'].get)
            flag = 4
        
        if (len(data['Queue VIP Customers']) == 0):
            
            if (len(data['Queue Normal Customers']) == 0):
                
                if (len(data['Queue VIP Recall Customers']) == 0):
                    
                    if (len(data['Queue Normal Recall Customers']) > 0):
                        if (clock % 1440 > 479):
                            data['Customers'][first_cutomer_in_queue]['Service Type'] = "VIP"
                            data['Customers'][first_cutomer_in_queue]['Is Recall'] = 1
                            fel_maker(future_event_list, "Recall", state, clock, data, first_cutomer_in_queue)

                else:
                    if (clock % 1440 > 479):
                            data['Customers'][first_cutomer_in_queue]['Service Type'] = "VIP"
                            data['Customers'][first_cutomer_in_queue]['Is Recall'] = 1
                            fel_maker(future_event_list, "Recall", state, clock, data, first_cutomer_in_queue)

            else:
                data['Customers'][first_cutomer_in_queue]['Service Type'] = "VIP"
                fel_maker(future_event_list, "Service", state, clock, data, first_cutomer_in_queue)

        else:
            data['Customers'][first_cutomer_in_queue]['Service Type'] = "VIP"
            fel_maker(future_event_list, "Service", state, clock, data, first_cutomer_in_queue)
    
    #Junior Service Type
    else:
        state['Available Junior Cashiers'] += 1
        data['Cumulative Stats']['Junior Cashier Busy Time'] += clock - data['Customers'][customer]['Time Service Begins']

        #Will the customer need Technical Service?
        r = random.random()

        if r < 0.15: #Needs Technical Support
            fel_maker(future_event_list, "Technical Arrival", state, clock, data, customer)
            tech_support = True
        
        #Who served next?
        if (len(data['Queue Normal Customers']) != 0):
            first_cutomer_in_queue = min(data['Queue Normal Customers'], key=data['Queue Normal Customers'].get)
            flag = 2
        elif (len(data['Queue Normal Recall Customers']) != 0):
            first_cutomer_in_queue = min(data['Queue Normal Recall Customers'], key=data['Queue Normal Recall Customers'].get)
            flag = 4
 
        if (len(data['Queue Normal Customers']) == 0): 
            if (len(data['Queue Normal Recall Customers']) > 0):
                        if (clock % 1440 > 479):
                            data['Customers'][first_cutomer_in_queue]['Service Type'] = "Junior"
                            data['Customers'][first_cutomer_in_queue]['Is Recall'] = 1
                            fel_maker(future_event_list, "Recall", state, clock, data, first_cutomer_in_queue)

        else:
            data['Customers'][first_cutomer_in_queue]['Service Type'] = "Junior"
            fel_maker(future_event_list, "Service", state, clock, data, first_cutomer_in_queue)                    



    #Remove Customer
    if (tech_support == False):
        data['Customers'].pop(customer, None)

    # This customer no longer belongs to queue
    if flag == 1:
        data['Queue VIP Customers'].pop(first_cutomer_in_queue, None)
    elif flag == 2:
        data['Queue Normal Customers'].pop(first_cutomer_in_queue, None)
    elif flag == 3:
        data['Queue VIP Recall Customers'].pop(first_cutomer_in_queue, None)
    elif flag == 4:
        data['Queue Normal Recall Customers'].pop(first_cutomer_in_queue, None)


#Leave the Queue at t
def leave_queue(future_event_list, state, clock, data, customer):
    if  (customer in data['Customers'].keys()) and (data['Customers'][customer]['Time Service Begins'] == None):
        if (data['Customers'][customer]['Type'] == "Normal"):
            data['Queue Normal Customers'].pop(customer, None) #Remove the customer from the Queue leaving the Queue
        else:
            data['Queue VIP Customers'].pop(customer, None) #Remove the customer from the Queue leaving the Queue
        data['Customers'].pop(customer, None)


#Technical arrival of customer at t
def technical_arrival(future_event_list, state, clock, data, customer):
    data['Cumulative Stats']['Area Under Technical Queue Length Curve'] += len((data['Queue Technical Customers'])) * (clock - data['Last Time Technical Queue Length Changed'])
    data['Last Time Technical Queue Length Changed'] = clock
    data['Queue Technical Customers'][customer] = clock
    if (data['Cumulative Stats']['Max Technical Queue Lenght'] < len(data['Queue Technical Customers'])):
        data['Cumulative Stats']['Max Technical Queue Lenght'] = len(data['Queue Technical Customers'])

    if (data['Customers'][customer]['Type'] == "Normal"):
        data['Cumulative Stats']['Number of Normal Technical Customers'] += 1
    else:
        data['Cumulative Stats']['Number of VIP Technical Customers'] += 1
    
    if state['Available Technical Cashiers'] > 0:
        fel_maker(future_event_list, "Technical Service", state, clock, data, customer)
    else:
        data['Customers'][customer]['Has Waiting'] = 1


#Start of Technical Service at t
def technical_service(future_event_list, state, clock, data, customer):
    data['Queue Technical Customers'].pop(customer, None)
    data['Customers'][customer]['Time Technical Service Begins'] = clock
    state['Available Technical Cashiers'] -= 1
    fel_maker(future_event_list, "End of Technical Service", state, clock, data, customer)


#End of Technical Service at t
def end_of_technical_service(future_event_list, state, clock, data, customer):
    state['Available Technical Cashiers'] += 1
    data['Customers'][customer]['Waiting Time'] = (data['Customers'][customer]['End of Service Time'] - data['Customers'][customer]['Arrival Time'])
    
    if (data['Customers'][customer]['Type'] == "VIP"):
        data['Cumulative Stats']['Time in System of VIP Customer'] -= data['Customers'][customer]['Waiting Time']
    
    data['Customers'][customer]['End of Service Time'] = clock
    data['Customers'][customer]['Waiting Time'] = (data['Customers'][customer]['End of Service Time'] - data['Customers'][customer]['Arrival Time'])
    
    data['Cumulative Stats']['Area Under Technical Queue Length Curve'] += len((data['Queue Technical Customers'])) * (clock - data['Last Time Technical Queue Length Changed'])
    data['Last Time Technical Queue Length Changed'] = clock

    if (data['Customers'][customer]['Type'] == "VIP"):
        data['Cumulative Stats']['Number of Served VIP Technical Customers'] += 1
        data['Cumulative Stats']['Total Technical Waiting Time'] += data['Customers'][customer]['Waiting Time']
        data['Cumulative Stats']['Time in System of VIP Customer'] += data['Customers'][customer]['Waiting Time']
        if (data['Cumulative Stats']['Max VIP Waiting Time'] < data['Customers'][customer]['Waiting Time']):
            data['Cumulative Stats']['Max VIP Waiting Time'] = data['Customers'][customer]['Waiting Time']
    else:
        data['Cumulative Stats']['Number of Served Normal Technical Customers'] += 1
        if (data['Cumulative Stats']['Max Normal Waiting Time'] < data['Customers'][customer]['Waiting Time']):
            data['Cumulative Stats']['Max Normal Waiting Time'] = data['Customers'][customer]['Waiting Time']
            
    data['Cumulative Stats']['Technical Cashier Busy Time'] += data['Customers'][customer]['End of Service Time'] - data['Customers'][customer]['Time Technical Service Begins']
    if (len(data['Queue Technical Customers']) != 0):
        first_cutomer_in_queue = min(data['Queue Technical Customers'], key=data['Queue Technical Customers'].get)
    if (len(data['Queue Technical Customers']) > 0):
        fel_maker(future_event_list, "Technical Service", state, clock, data, first_cutomer_in_queue)


#Changing Shift
def change_shift(future_event_list, state, clock, data, customer):
    if (state['Current Shift'] == 1):
        state['Current Shift'] = 2
    elif (state['Current Shift'] == 2):
        state['Current Shift'] = 3
    else:
        state['Current Shift'] = 1

    fel_maker(future_event_list, "Change Shift", state, clock, data, customer)


#Recall at t
def recall(future_event_list, state, clock, data, customer):
    
    data['Customers'][customer]['Arrival Time'] = clock
    data['Customers'][customer]['Time Service Begins'] = clock

    #Check the type of customer
    if (data['Customers'][customer]['Type'] == "Normal"):
        data['Cumulative Stats']['Area Under Normal Recall Queue Length Curve'] += len((data['Queue Normal Recall Customers'])) * (clock - data['Last Time Normal Recall Queue Length Changed'])
        data['Last Time Normal Recall Queue Length Changed'] = clock
        data['Queue Normal Recall Customers'].pop(customer, None) #Remove the customer from the Queue due start of
    else:
        data['Cumulative Stats']['Area Under VIP Recall Queue Length Curve'] += len((data['Queue VIP Recall Customers'])) * (clock - data['Last Time VIP Recall Queue Length Changed'])
        data['Last Time VIP Recall Queue Length Changed'] = clock
        data['Queue VIP Recall Customers'].pop(customer, None) #Remove the customer from the Queue due start of service

    #Check service type
    if (data['Customers'][customer]['Service Type'] == "Junior"):
        state['Available Junior Cashiers'] -= 1
    else:
        state['Available VIP Cashiers'] -= 1

    #Create an "End of Service" event for this service
    fel_maker(future_event_list, "End of Service", state, clock, data, customer)


#System Malfunction at t
def malfunction(future_event_list, state, clock, data, customer):
    global params
    params[1]= 1/2
    params[2]= 2
    params[3]= 1
    fel_maker(future_event_list, "End of System Malfunction", state, clock, data, customer)


#End of System Malfunction at t
def end_malufaction(future_event_list, state, clock, data, customer):
    global params
    params[1]= 1/3 
    params[2]= 1 
    params[3]= 1/2
    fel_maker(future_event_list, "Malfunction", state, clock, data, customer)


def print_header():
    print('Event Type'.ljust(20) + '\t' + 'Time'.ljust(15))
    print('-------------------------------------------------------------------------------------------------')


def nice_print(current_state, current_event, current_customer):
    print(str(current_event['Event Type']).ljust(30) + '\t' + str(round(current_event['Event Time'], 3)).ljust(15) + '\t' + str(current_customer).ljust(15))


def create_row(step, current_event, state, data, future_event_list):
    # This function will create a list, which will eventually become a row of the output Excel file

    sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])

    # What should this row contain?
    # 1. Step, Clock, Event Type and Event Customer
    row = [step, current_event['Event Time'], current_event['Event Type'], current_event['Customer']]
    # 2. All state variables
    row.extend(list(state.values()))
    # 3. All Cumulative Stats
    row.extend(list(data['Cumulative Stats'].values()))

    # row = [step, current_event['Event Type'], current_event['Event Time'],
    #        state['Queue Length'], state['Server Status'], data['Cumulative Stats']['Server Busy Time'],
    #        data['Cumulative Stats']['Queue Waiting Time'],
    #        data['Cumulative Stats']['Area Under Queue Length Curve'], data['Cumulative Stats']['Service Starters']]

    # 4. All events in fel ('Event Time', 'Event Type' & 'Event Customer' for each event)
    for event in sorted_fel:
        row.append(event['Event Time'])
        row.append(event['Event Type'])
        row.append(event['Customer'])
    return row


def justify(table):
    # This function adds blanks to short rows in order to match their lengths to the maximum row length

    # Find maximum row length in the table
    row_max_len = 0
    for row in table:
        if len(row) > row_max_len:
            row_max_len = len(row)

    # For each row, add enough blanks
    for row in table:
        row.extend([""] * (row_max_len - len(row)))


def create_main_header(state, data):
    # This function creates the main part of header (returns a list)
    # A part of header which is used for future events will be created in create_excel()

    # Header consists of ...
    # 1. Step, Clock, Event Type and Event Customer
    header = ['Step', 'Clock', 'Event Type', 'Event Customer']
    # 2. Names of the state variables
    header.extend(list(state.keys()))
    # 3. Names of the cumulative stats
    header.extend(list(data['Cumulative Stats'].keys()))
    return header


def create_excel(table, header):
    # This function creates and fine-tunes the Excel output file

    # Find length of each row in the table
    row_len = len(table[0])

    # Find length of header (header does not include cells for fel at this moment)
    header_len = len(header)

    # row_len exceeds header_len by (max_fel_length * 3) (Event Type, Event Time & Customer for each event in FEL)
    # Extend the header with 'Future Event Time', 'Future Event Type', 'Future Event Customer'
    # for each event in the fel with maximum size
    i = 1
    for col in range((row_len - header_len) // 3):
        header.append('Future Event Time ' + str(i))
        header.append('Future Event Type ' + str(i))
        header.append('Future Event Customer ' + str(i))
        i += 1

    # Dealing with the output
    # First create a pandas DataFrame
    df = pd.DataFrame(table, columns=header, index=None)

    # Create a handle to work on the Excel file
    writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')

    # Write out the Excel file to the hard drive
    df.to_excel(writer, sheet_name='Single-server Queue Output', header=False, startrow=1, index=False)

    # Use the handle to get the workbook (just library syntax, can be found with a simple search)
    workbook = writer.book

    # Get the sheet you want to work on
    worksheet = writer.sheets['Single-server Queue Output']

    # Create a cell-formatter object (this will be used for the cells in the header, hence: header_formatter!)
    header_formatter = workbook.add_format()

    # Define whatever format you want
    header_formatter.set_align('center')
    header_formatter.set_align('vcenter')
    header_formatter.set_font('Times New Roman')
    header_formatter.set_bold('True')

    # Write out the column names and apply the format to the cells in the header row
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_formatter)

    # Auto-fit columns
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i - 1, i - 1, width)

    # Create a cell-formatter object for the body of excel file
    main_formatter = workbook.add_format()
    main_formatter.set_align('center')
    main_formatter.set_align('vcenter')
    main_formatter.set_font('Times New Roman')

    # Apply the format to the body cells
    for row in range(1, len(df) + 1):
        worksheet.set_row(row, None, main_formatter)

    # Save your edits
    writer.save()


def get_col_widths(dataframe):
    # Copied from https://stackoverflow.com/questions/29463274/simulate-autofit-column-in-xslxwriter
    # First we find the maximum length of the index column
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    # Then, we concatenate this to the max of the lengths of column name and its values for each column, left to right
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]


def simulation(simulation_time):
    state, future_event_list, data = starting_state()
    clock = 0
    table = []  # a list of lists. Each inner list will be a row in the Excel output.
    step = 1  # every event counts as a step.
    future_event_list.append({'Event Type': 'End of Simulation', 'Event Time': simulation_time, 'Customer': None})


    while clock < simulation_time:
        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])
        #print('-------------------------------------------------------------------------------------------------')
        #print(data)
        #print(sorted_fel)
        current_event = sorted_fel[0]
        clock = current_event['Event Time']
        customer = current_event['Customer']
        #print(state["VIP Queue Length"])
        if clock < simulation_time:  # if current_event['Event Type'] != 'End of Simulation'
            if current_event['Event Type'] == 'Arrival':
                arrival(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'Service':
                service(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'End of Service':
                end_of_service(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'Leave the Queue':
                leave_queue(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'Technical Arrival':
                technical_arrival(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'Technical Service':
                technical_service(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'End of Technical Service':
                end_of_technical_service(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'Change Shift':
                change_shift(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'Recall':
                recall(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'Malfunction':
                malfunction(future_event_list, state, clock, data, customer)
            elif current_event['Event Type'] == 'End of System Malfunction':
                end_malufaction(future_event_list, state, clock, data, customer)
            future_event_list.remove(current_event)
        else:
            future_event_list.clear()
         # create a row in the table
        table.append(create_row(step, current_event, state, data, future_event_list))
        step += 1
        #nice_print(state, current_event, customer)
    
    excel_main_header = create_main_header(state, data)
    justify(table)
    create_excel(table, excel_main_header)
    
    print('-------------------------------------------------------------------------------------------------')
    avg_time_vip_customers = data['Cumulative Stats']['Time in System of VIP Customer'] / data['Cumulative Stats']['Number of VIP Customers']
    print(f"Average Time in System of VIP Customers: {avg_time_vip_customers}")
    print('-------------------------------------------------------------------------------------------------')
    num_non_waiting_vip = 0
    for customer in data['Customers']:
        if (data['Customers'][customer]['Type'] == "VIP") and (data['Customers'][customer]['Has Waiting'] == 0):
            num_non_waiting_vip += 1
    percent_non_waiting_vip = int(num_non_waiting_vip / data['Cumulative Stats']['Number of VIP Customers'] * 100)
    print(f"Percent of Non Waiting VIP Cutomers: {percent_non_waiting_vip}%")
    print('-------------------------------------------------------------------------------------------------')
    print(f"Max VIP Queue Lenght: {data['Cumulative Stats']['Max VIP Queue Lenght']}")
    print(f"Max Normal Queue Lenght: {data['Cumulative Stats']['Max Normal Queue Lenght']}")
    print(f"Max VIP Recall Queue Lenght: {data['Cumulative Stats']['Max VIP Recall Queue Lenght']}")
    print(f"Max Normal Recall Queue Lenght: {data['Cumulative Stats']['Max Normal Recall Queue Lenght']}")
    print(f"Max Technical Queue Lenght: {data['Cumulative Stats']['Max Technical Queue Lenght']}")
    print('-------------------------------------------------------------------------------------------------')
    normal_cashier_productivity = int((data['Cumulative Stats']['Junior Cashier Busy Time'] / simulation_time)*100 / 3)
    vip_cashier_productivity = int((data['Cumulative Stats']['VIP Cashier Busy Time'] / simulation_time)*100 / 2)
    technical_cashier_productivity = int((data['Cumulative Stats']['Technical Cashier Busy Time'] / simulation_time)*100 / 2)
    print(f"VIP Cahier Productivity: {vip_cashier_productivity}%")
    print(f"Normal Cahier Productivity: {normal_cashier_productivity}%")
    print(f"Technical Cahier Productivity: {technical_cashier_productivity}%")
    print('-------------------------------------------------------------------------------------------------')
    print(f"Max VIP Waiting Time: {data['Cumulative Stats']['Max VIP Waiting Time']}")
    print(f"Max Normal Waiting Time: {data['Cumulative Stats']['Max Normal Waiting Time']}")
    print('-------------------------------------------------------------------------------------------------')
    print(f"Average Daily Number of Served VIP Customers: {int(data['Cumulative Stats']['Number of Served VIP Customers'] / 30)}")
    print(f"Average Daily Number of Served Normal Customers: {int(data['Cumulative Stats']['Number of Served Normal Customers'] / 30)}")
    print(f"Average Daily Number of Served VIP Technical Customers: {int(data['Cumulative Stats']['Number of Served VIP Technical Customers'] / 30)}")
    print(f"Average Daily Number of Served Normal Technical Customers: {int(data['Cumulative Stats']['Number of Served Normal Technical Customers'] / 30)}")
    print('-------------------------------------------------------------------------------------------------')
    print(f"Average VIP Waiting Time: {data['Cumulative Stats']['Total VIP Waiting Time'] / data['Cumulative Stats']['Number of Served VIP Customers']}")
    print(f"Average Normal Waiting Time: {data['Cumulative Stats']['Total Normal Waiting Time'] / data['Cumulative Stats']['Number of Served Normal Customers']}")
    print(f"Average Technical Waiting Time: {data['Cumulative Stats']['Total Technical Waiting Time'] / (data['Cumulative Stats']['Number of Served VIP Technical Customers'] + data['Cumulative Stats']['Number of Served Normal Technical Customers'])}")
    print('-------------------------------------------------------------------------------------------------')
    print(f"Average VIP Queue Length: {data['Cumulative Stats']['Area Under VIP Queue Length Curve'] / simulation_time}")
    print(f"Average Normal Queue Length: {data['Cumulative Stats']['Area Under Normal Queue Length Curve'] / simulation_time}")
    print(f"Average Technical Queue Length: {data['Cumulative Stats']['Area Under Technical Queue Length Curve'] / simulation_time}")
    print(f"Average VIP Recall Queue Length: {data['Cumulative Stats']['Area Under VIP Recall Queue Length Curve'] / simulation_time}")
    print(f"Average Normal Recall Queue Length: {data['Cumulative Stats']['Area Under Normal Recall Queue Length Curve'] / simulation_time}")
    print('-------------------------------------------------------------------------------------------------')
    print(f"Number of VIP Customers: {data['Cumulative Stats']['Number of VIP Customers']}")
    print(f"Number of Normal Customers: {data['Cumulative Stats']['Number of Normal Customers']}")
    print(f"Number of VIP Technical Customers: {data['Cumulative Stats']['Number of VIP Technical Customers']}")
    print(f"Number of Normal Technical Customers: {data['Cumulative Stats']['Number of Normal Technical Customers']}")
    print(f"Number of Non Waiting VIP Customers: {data['Cumulative Stats']['Number of Non Waiting VIP Customers']}")
    print(f"Number of Non Waiting Normal Customers: {data['Cumulative Stats']['Number of Non Waiting Normal Customers']}")


simulation(43200)