import math
import random


#Parameters of Distributions
params = list()
for i in range(4):
    params.append(0)
params[1]= 3 #Will Use for Exponential Ditribution
params[2]= 1 #Will Use for Exponential Ditribution
params[3]= 2 #Will Use for Exponential Ditribution


#Create Uniform Distributed Variables
def uniform(a, b):
    r = random.random()
    return a + (b - a) * r


#Crate Exponential Distributed Varibles
def exponential(lambd):
    r = random.random()
    return -(1 / lambd) * math.log(r)


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

    data['Cumulative Stats']['VIP Cashier Busy Time'] = 0
    data['Cumulative Stats']['Junior Cashier Busy Time'] = 0
    data['Cumulative Stats']['Technical Cashier Busy Time'] = 0


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
            event_time = clock + 1
        elif state['Current Shift'] == 2:
            event_time = clock + 1
        elif state['Current Shift'] == 3:
            event_time = clock + 1

    #Service event maker
    #TODO
    if type == "Service":
        event_time = clock

    #End of Service event maker
    if type == "End of Service":
        if (data['Customers'][customer]['Service Type'] == "Junior"):
            event_time = clock + 10
        else:
            event_time = clock + 10

    #TODO
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
        event_time = clock + 2

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
                if (data['Cumulative Stats']['Max VIP Recall Queue Lenght'] < len(data['Queue VIP Recall Customers'])):
                    data['Cumulative Stats']['Max VIP Recall Queue Lenght'] = len(data['Queue VIP Recall Customers'])

            else:
                r_leave = random.random()
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
                if (data['Cumulative Stats']['Max Normal Recall Queue Lenght'] < len(data['Queue Normal Recall Customers'])):
                    data['Cumulative Stats']['Max Normal Recall Queue Lenght'] = len(data['Queue Normal Recall Customers'])

            else:
                r_leave = random.random()
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
#TODO
def end_of_service(future_event_list, state, clock, data, customer):
    
    first_cutomer_in_queue = None
    flag = 0
    tech_support = False
    #End time of Service records in data
    data['Customers'][customer]['End of Service Time'] = clock
    data['Cumulative Stats']['Time in System of VIP Customer'] += (data['Customers'][customer]['End of Service Time'] - data['Customers'][customer]['Arrival Time'])

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
                            fel_maker(future_event_list, "Recall", state, clock, data, first_cutomer_in_queue)

                else:
                    if (clock % 1440 > 479):
                            data['Customers'][first_cutomer_in_queue]['Service Type'] = "VIP"
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
    data['Cumulative Stats']['Technical Cashier Busy Time'] += clock - data['Customers'][customer]['Time Technical Service Begins']
    state['Available Technical Cashiers'] += 1
    data['Cumulative Stats']['Time in System of VIP Customer'] -= (data['Customers'][customer]['End of Service Time'] - data['Customers'][customer]['Arrival Time'])
    data['Customers'][customer]['End of Service Time'] = clock
    data['Cumulative Stats']['Time in System of VIP Customer'] += (data['Customers'][customer]['End of Service Time'] - data['Customers'][customer]['Arrival Time'])
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
    
    data['Customers'][customer]['Time Service Begins'] = clock

    #Check the type of customer
    if (data['Customers'][customer]['Type'] == "Normal"):
        data['Queue Normal Recall Customers'].pop(customer, None) #Remove the customer from the Queue due start of
    else:
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
    params[1]= 2
    params[2]= 0.5
    params[3]= 1
    fel_maker(future_event_list, "End of System Malfunction", state, clock, data, customer)


#End of System Malfunction at t
def end_malufaction(future_event_list, state, clock, data, customer):
    global params
    params[1]= 3 
    params[2]= 1 
    params[3]= 2
    fel_maker(future_event_list, "Malfunction", state, clock, data, customer)


def print_header():
    print('Event Type'.ljust(20) + '\t' + 'Time'.ljust(15))
    print('-------------------------------------------------------------------------------------------------')


def nice_print(current_state, current_event, current_customer):
    print(str(current_event['Event Type']).ljust(30) + '\t' + str(round(current_event['Event Time'], 3)).ljust(15) + '\t' + str(current_customer).ljust(15))


def simulation(simulation_time):
    state, future_event_list, data = starting_state()
    clock = 0
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
        #nice_print(state, current_event, customer)
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
    vip_cashier_productivity = (data['Cumulative Stats']['VIP Cashier Busy Time'] / simulation_time) / 2
    normal_cashier_productivity = (data['Cumulative Stats']['Junior Cashier Busy Time'] / simulation_time) / 3
    technical_cashier_productivity = (data['Cumulative Stats']['Technical Cashier Busy Time'] / simulation_time) / 2
    print(f"VIP Cahier Productivity: {vip_cashier_productivity}")
    print(f"Normal Cahier Productivity: {normal_cashier_productivity}")
    print(f"Technical Cahier Productivity: {technical_cashier_productivity}")
    print('-------------------------------------------------------------------------------------------------')
    print(f"Number of VIP Customers: {data['Cumulative Stats']['Number of VIP Customers']}")
    print(f"Number of Normal Customers: {data['Cumulative Stats']['Number of Normal Customers']}")
    print(f"Number of VIP Technical Customers: {data['Cumulative Stats']['Number of VIP Technical Customers']}")
    print(f"Number of Normal Technical Customers: {data['Cumulative Stats']['Number of Normal Technical Customers']}")
    print(f"Number of Non Waiting VIP Customers: {data['Cumulative Stats']['Number of Non Waiting VIP Customers']}")
    print(f"Number of Non Waiting Normal Customers: {data['Cumulative Stats']['Number of Non Waiting Normal Customers']}")


simulation(43200)