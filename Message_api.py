#import all neccessary modules

import requests
from requests.auth import HTTPBasicAuth
import json


# plivo authid & token details

authid = 'MAODUZYTQ0Y2FMYJBLOW'
authtoken ='ODgyYmQxYTQ2N2FkNDFiZTNhZWY4MDAwYWY4NzY0'


'''
Case1:

Use any two numbers available in the account.Get all numbers api to find any two numbers. 

'''


# use get list of all numbers from number api and store in the list
def get_all_nums():
    get_num_url='https://api.plivo.com/v1/Account/'+authid+'/Number/'
    get_numbers = requests.get(get_num_url,auth=HTTPBasicAuth(authid, authtoken))
    response = get_numbers.json()
    a = response.get('objects')
    global numbers
    numbers =[]
    for i in range(len(a)):
        numbers.append(str(a[i].get('number')))
    print('list of available numbers are : '+str(numbers))


# Before sending the message, check the balance, this will help us to verify the amount is deducted properly or not.

def cash_credits_before_call():
    verify_acct_details_uri='https://api.plivo.com/v1/Account/'+authid+'/'
    verify_acct_details = requests.get(verify_acct_details_uri,auth=HTTPBasicAuth(authid, authtoken))
    verify_acct_details_res = verify_acct_details.json()
    global credit_details_before_call
    credit_details_before_call = verify_acct_details_res.get('cash_credits')
    print('Cash_credits available before running the call:'+credit_details_before_call)

'''
Case 2


Use message api to send an sms from a number to another number.One can use both number bought as above to do this.

'''

#pick fist 2 numbers from number list returned in case 1 and send message from number1 to number2

def send_msg():
    snd_msg_url= 'https://api.plivo.com/v1/Account/'+authid+'/Message/'
    fields = {'src':numbers[0],
            'dst':numbers[1],
            'text':'Hello World'}
    print('we are going to send message from '+numbers[0]+' to '+numbers[1])
    snd_msg = requests.post(snd_msg_url,auth=HTTPBasicAuth(authid, authtoken), data = fields)
    json_b = snd_msg.json()
    print('sending message is successful')
    global uuid_sndmsg
    uuid_sndmsg = json_b.get('message_uuid')[0]
    print('uuid for the message is : '+str(uuid_sndmsg))


'''
Case 3


Once message api is successful, response give message uuid.Using this message uuid get the details of the message using details api.

'''
#Get the details about message based on uuid

def msg_details():
    
    get_msg_details='https://api.plivo.com/v1/Account/'+authid+'/Message/'+uuid_sndmsg+'/'
    print('we are going to get message details using uuid'+str(uuid_sndmsg))
    snd_msg = requests.get(get_msg_details,auth=HTTPBasicAuth(authid, authtoken))
    snd_msg_res = snd_msg.json()
    #snd_msg_res_formating = snd_msg_res.get('objects')
    global total_rate
    #total_rate = str(snd_msg_res_formating[0].get('total_rate'))
    total_rate = str(snd_msg_res.get('total_rate'))
    to_number = snd_msg_res.get('to_number')
    from_number = snd_msg_res.get('from_number')
    message_uuid = snd_msg_res.get('message_uuid')

    if uuid_sndmsg == message_uuid:
        print('Getting the message details is successful')
    else:
        print('Getting the message details is failed')


'''
Case 4
Use pricing api to determine the rate of the message which is outbound rate under message object in this case.

'''
#get the price plan defined for sending message

def pricing_plan():
    get_price_plan_url='https://api.plivo.com/v1/Account/'+authid+'/Pricing/'
    data_price_plan ={'country_iso':'US'}
    print('we are going to get the price plan for sending message')
    snd_price_plan = requests.get(get_price_plan_url,auth=HTTPBasicAuth(authid, authtoken),params = data_price_plan)
    get_price_plan_res = snd_price_plan.json()
    global rate
    rate = str((get_price_plan_res.get('message')).get('outbound').get('rate'))
    #rate1 = str((get_price_plan_res.get('message')).get('outbound_networks_list')[0].get('rate'))
    print("pricing plan  for sending message is :"+str(rate))


'''
Case 5

Verify the rate and the price deducted for the sending message, should be same.
'''


#Verify charging is done properly for sending SMS

def check_proper_charging():
    if rate == total_rate:
        print('Charging done properly')
    else:
        print('Charging not done properly')

'''

Case 6

And finally after sending message, using account details api, account cash credit should be less than by the deducted amount.

'''

# Verify Account details, sms charge has been deducted from balance.

def verify_balance_deducted():
    
    verify_acct_details_uri='https://api.plivo.com/v1/Account/'+authid+'/'
    verify_acct_details = requests.get(verify_acct_details_uri,auth=HTTPBasicAuth(authid, authtoken))
    verify_acct_details_res = verify_acct_details.json()
    credit_details_after_call = verify_acct_details_res.get('cash_credits')


    if float(credit_details_after_call) == float(credit_details_before_call) - float(total_rate):
        print('amount deducted properly from cash_credits account')
    else:
        print('amount not deducted properly from cash_credits account')


if __name__ == '__main__':
    get_all_nums()
    cash_credits_before_call()
    send_msg()
    msg_details()
    pricing_plan()
    check_proper_charging()
    verify_balance_deducted()
