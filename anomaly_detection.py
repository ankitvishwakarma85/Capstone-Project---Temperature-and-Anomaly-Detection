import email_conf, sms_conf, json, time, math, statistics
from boltiot import Email, Bolt, Sms

def compute_bounds(history_data,frame_size,factor):
    if len(history_data)<frame_size :
        return None
    if len(history_data)>frame_size :
        del history_data[0:len(history_data)-frame_size]
    Mn=statistics.mean(history_data)
    Variance=0    
    for data in history_data :        
       Variance += math.pow((data-Mn),2)
    Zn = factor * math.sqrt(Variance / frame_size)    
    High_bound = history_data[frame_size-1]+Zn    
    Low_bound = history_data[frame_size-1]-Zn    
    return [High_bound,Low_bound]

minimum_limit = 10.24
maximum_limit = 51.2

mybolt = Bolt(email_conf.API_KEY, email_conf.DEVICE_ID)
mailer = Email(email_conf.MAILGUN_API_KEY, email_conf.SANDBOX_URL, email_conf.SENDER_EMAIL, email_conf.RECIPIENT_EMAIL)
sms = Sms(sms_conf.SSID, sms_conf.AUTH_TOKEN, sms_conf.TO_NUMBER, sms_conf.FROM_NUMBER)
history_data=[]

while True:    
    response = mybolt.analogRead('A0')    
    data = json.loads(response)    
    if data['success'] != 1:
        print("There was an error while retriving the data.")
        print("This is the error:"+data['value'])
        time.sleep(10)
        continue
    print ("This is the value "+data['value'])
    sensor_value=0
    try:
        sensor_value = int(data['value'])
    except e:
        print("There was an error while parsing the response: ",e)
        continue
    bound = compute_bounds(history_data,sms_conf.FRAME_SIZE,sms_conf.MUL_FACTOR)
    if not bound:
        required_data_count=sms_conf.FRAME_SIZE-len(history_data)
        print("Not enough data to compute Z-score. Need ",required_data_count," more data points")
        history_data.append(int(data['value']))
        time.sleep(10)
        continue

    print("bound[0]",bound[0])
    print("bound[1]",bound[1])
    try:
        if sensor_value > bound[0] :
            print ("The Temperature increased suddenly. Sending a sms through Twilio.")
            print ("The Current temperature is: "+str(sensor_value))
            response = sms.send_sms("Alert! Someone has opened the fridge door")
            print("Response :",response)
        elif sensor_value > maximum_limit or sensor_value < minimum_limit:
            print("Alert! The temperature condition can destroy the tablets. Sending an email through Mailgun.")
            print ("The Current temperature is:" +str(sensor_value))
            response = mailer.send_email("Alert!","The current temperature can destroy the tablets.")
            print("Response:",response)
        history_data.append(sensor_value);
    except Exception as e:
        print ("Error",e)
    time.sleep(10)