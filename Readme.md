# Intelligent Refrigerator – Capstone Project

Language used – Python

Sending an Email using Mailgun services when temperature is not within the prescribed range. Sending an SMS when fridge is opened using Twilio services (Using Z-score Analysisi.e. when anomaly in temperature graph is detected.)

## Things used in this project

**Hardware components**
1) Bolt WiFi Module - WiFi Module that gives the Hardware connection internet access for transfer of data over cloud
2) Temperature Sensor - LM35 Sensor
3) Jumper wires (generic) - To connect the LM35 to the Wifi Module
4) USB-A to Micro-USB Cable - To connect the module to power supply

**Software apps and online services**
1) Twilio SMS Messaging API - To receive SMS when anomaly(i.e. When fridge door is opened) is detected.
2) Mailgun - To receive mail when temperature crosses threshold
3) Bolt Cloud - To upload data recorded by the module and process the data

# Steps :
**1) Connect the LM35 to the bolt Module**

Step 1: Hold the sensor in a manner such that you can read LM35 written on it.

Step 2: In this position, identify the pins of the sensor as VCC, Output and Gnd from your left to right.

In the above image, VCC is connected to the red wire, Output is connected to the orange wire and Gnd is connected to the brown wire.Step 3: Using male to female wire connect the 3 pins of the LM35 to the Bolt Wifi Module as follows:

VCC pin of the LM35 connects to 5v of the Bolt Wifi module.
Output pin of the LM35 connects to A0 (Analog input pin) of the Bolt Wifi module.
Gnd pin of the LM35 connects to the Gnd.

**2) Creating a product on Bolt cloud to get the upper, lower temperature limits of the Refrigerator**

**3) Writing Code for the product**
Save the code and exits.

Later link the product to the bolt module and deploy the configuration.

**4) Let the module rest for about 2 hours and see the output.**

**5) Analyse the output and decide the maximum and the minimum limit**
As you can see the sudden change is when the module is kept in the fridge.

From the graph it is clear that :

minimum_limit = 1 degree i.e. 10.24(in terms of sensor value)

maximum_limit = 5 degree i.e. 51.2(in terms of sensor value)

**6) Writhing python code on the terminal or any other virtual system**

You can create a new folder and enter it using the following command.

```bash
mkdir Anomaly_Detection;
cd Anomaly_Detection;
```

a) 
Note : You need a mailgun account before this step. In case you don't have one refer to your bolt iot traning for the same.

Login into the server by entering the IP address of your digital ocean droplet. If you have not used Digital Ocean droplet, you can directly login to your Virtual Machine via VirtualBox or VMWare.

After successful login, create a file named email_conf.py which will store all the credentials related to Mailgun. To create a new file type sudo nano email_conf.py in the terminal. After that write below code to save all the credentials in a single file.

Save the file.

b)
Note : You need a twilio account before this step. In case you don't have one refer to your bolt iot traning for the same.

Login into the putty by entering the IP address of your digital ocean droplet.

After successful login, create a file named sms_conf.py which will store all the credentials related to Twilio. To create a new file type sudo nano sms_conf.py in the terminal. After that write below code to save all the credentials in a single file.

Save the file.

c)
Now create one more file named anomaly_detction.py, using the following command
```bash
sudo nano anomaly_detection.py
```
Algorithm:

1) Fetch the latest sensor value from the Bolt device.
2) Store the sensor value in a list, that will be used for computing z-score.
3) Compute the z-score and upper and lower threshold bounds for normal and anomalous readings.
4) Check if the sensor reading is within the range for normal readings. i.e. no sudden increase in temperature
5) If it is not in range, send the mail.
6) Check if the sensor value is in the range specified in our min and max values.
7) If it is not in range, send the SMS.
8) Wait for 10 seconds.
9) Repeat from step 1.

Code :
We have to import our ( sms_conf & email_conf ) files which have all the credentials, json and time.
Also we import our Bolt python library which will let us fetch the data stored in Bolt Cloud and then based on value send Email and SMS.
The math and statistics libraries will be required for calculating the Z-score and the threshold boundaries.
```bash
import email_conf, sms_conf, json, time, math, statistic
from boltiot import Email, Bolt, Sms
```
The following lies code helps define a function which calculates the Z-score and the using the Z-score calculates the boundaries required for anomaly detection.
```bash
def compute_bounds(history_data,frame_size,factor):
```
The above line helps defines a function, which takes 3 input variables: history_data, frame_size and factor.
```bash
if len(history_data)<frame_size :
        return None
if len(history_data)>frame_size :
    del history_data[0:len(history_data)-frame_size]
```
The above code checks whether enough data has been accumulated to calculate the Z-score, and if there is too much data, then the code deletes the older data.
```bash
Mn=statistics.mean(history_data)
```
The above code calculates the mean (Mn) value of the collected data points.

```bash
Variance=0    
for data in history_data :        
    Variance += math.pow((data-Mn),2)
```
This code helps to calculate the Variance of the data points.

```bash
Zn = factor * math.sqrt(Variance / frame_size)    
High_bound = history_data[frame_size-1]+Zn    
Low_bound = history_data[frame_size-1]-Zn    
return [High_bound,Low_bound]
```
Here we calculate the Z score (Zn) for the data and use it to calculate the upper and lower threshold bounds required to check if a new data point is normal or anomalous.

Now we will initialize two variables which will store minimum and maximum threshold value. You can initialize any minimum and maximum integer limits to them.

This would send an alert if the temperature reading goes below the minimum limit or goes above the maximum limit.

```bash
minimum_limit = 10.24
maximum_limit = 51.2

mybolt = Bolt(email_conf.API_KEY, email_conf.DEVICE_ID)
```
The above code will automatically fetch your API key and Device ID that you have initialized in email_conf.py file.

```bash
mailer = Email(email_conf.MAILGUN_API_KEY, email_conf.SANDBOX_URL, email_conf.SENDER_EMAIL, email_conf.RECIPIENT_EMAIL)
```
The above code will automatically fetch your MAILGUN_API_KEY, SANDBOX_URL, SENDER_EMAIL and RECIPIENT_EMAIL that you have initialized in email_conf.py file. Make sure you have entered the correct values in email_conf.py file.

To collect data and send SMS alerts. Here we also initialize an empty list with the name 'history_data' which we will use to store older data, so that we can calculate the Z-score.

```bash
sms = Sms(sms_conf.SSID, sms_conf.AUTH_TOKEN, sms_conf.TO_NUMBER, sms_conf.FROM_NUMBER)
history_data=[]
```
The following while loop contains the code required to run the algorithm of anomaly detection.

```bash
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
```