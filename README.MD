## Documentation structure

[**About this repo**](README.MD#about-this-repo)  
[**Building blocks**](README.MD#building-blocks)  
[**Clone this repository**](README.MD#clone-this-repository)  
[**Configure Appformix to add network devices to monitor**](README.MD#configure-appformix-to-add-network-devices-to-monitor)  
[**Configure the network devices with the SNMP community used by Appformix**](README.MD#configure-the-network-devices-with-the-snmp-community-used-by-appformix)  
[**Configure the network devices for JTI telemetry**](README.MD#configure-the-network-devices-for-jti-telemetry)  
[**Webhooks**](README.MD#webhooks)  
[**Event driven automation**](README.MD#event-driven-automation)  
[**How to reproduce the event driven automation demo**](README.MD#how-to-reproduce-the-event-driven-automation-demo)  
[**Automated data collection demo**](README.MD#automated-data-collection-demo)  
[**Looking for more automation solutions**](README.MD#looking-for-more-automation-solutions)  

## About this repo

This repository has scripts to quickly demo network devices monitoring using Appformix.   
![appformix_network_devices_monitoring.png](resources/appformix_network_devices_monitoring.png)  

It has also scripts to demo event driven automation leveraging Appformix.  
Based on Appformix webhook notifications, automatically collect additional data from the "faulty" device and automatically upload the data collected on a Git server  
![automated-data-collection.png](resources/automated-data-collection.png)  

Here are more details about the automation content available in this repository. It has automation content to:  
- Add network devices to Appformix
- Configure the network devices with the SNMP community used by Appformix to monitor them
- Modify the IP address configured by Appformix for telemetry on the network devices
- Trigger Appformix alarms  
- Listen to the webhooks notifications sent by Appformix
- React to the webhooks notifications sent by Appformix (event driven automation). The reactions triggered automatically are python scripts to collect additional data on the "faulty" device and upload them on a Git server  
   
I am using them with an Appformix standalone setup running version 2.15.2 installed on Ubuntu 16.04

This repository doesn’t cover how to install Appformix

## Building blocks

This repository uses the following main building blocks: 
- Juniper vMX devices. 
  - Other Junos devices can be used. 
- Appformix 
  - To collect data (using SNMP and JTI native streaming telemetry) from Junos devices. 
  - To generate webhooks notifications. 
- A webhook listener. This is a python script that: 
  - Listens to webhooks
  - Extracts data from the webhooks (the network device name as example)
  - Maps the webhooks to python functions
  - Passes the data extracted from the webhooks to the mapped python function
  - Executes the mapped python function. 
- Python scripts to trigger Appformix alarms  
- Python scripts triggered automatically by the webhook listener to make actions against Junos devices and a Git server
 
## Clone this repository

Run these commands to clone this repository:
```
sudo -s
git clone https://github.com/JNPRAutomate/automated_junos_show_commands_collection_with_appformix_python.git
```

## Requirements to use this repository 

Run these commands to install the python library junos-eznc (also know as PyEZ) and its dependencies.
```
sudo -s
cd automated_junos_show_commands_collection_with_appformix_python
apt-get update && apt-get upgrade
apt-get install -y python-dev libxml2-dev python-pip libxslt1-dev build-essential libssl-dev libffi-dev git curl
pip install -r requirements.txt
```

## Configure Appformix to add network devices to monitor

Appformix supports network devices monitoring using SNMP and JTI (Juniper Telemetry Interface) native streaming telemetry.  
- For SNMP, the polling interval is 60s.  
- For JTI streaming telemetry, Appformix automatically configures the network devices. The interval configured on network devices is 60s.  

Here's the [**documentation**](https://www.juniper.net/documentation/en_US/appformix/topics/concept/appformix-ansible-configure-network-device.html)  

In order to configure AppFormix for network devices monitoring, here are the steps:
- manage the 'network devices json configuration' file. This file is used to define the list of devices you want to monitor using Appformix, and the details you want to collect from them.    
- Indicate to the 'Appformix installation Ansible playbook' which 'network devices json configuration file' to use. This is done by setting the variable ```network_device_file_name``` in ```group_vars/all```
- Set the flag to enable appformix network device monitor. This is done by setting the variable ```appformix_network_device_monitoring_enabled``` to ```true``` in ```group_vars/all```
- Enable the Appformix plugins for network devices monitoring. This is done by setting the variable ```appformix_plugins``` in ```group_vars/all```
- re run the 'Appformix installation Ansible playbook'.

Here's how to manage the 'network devices json configuration file' with automation:  
Define the list of devices you want to monitor using Appformix, and the details you want to collect from them:    
```
cd automated_junos_show_commands_collection_with_appformix_python
vi configure_appformix/network_devices.yml
```

Execute the python script [**network_devices.py**](configure_appformix/network_devices.py). It renders the template [**network_devices.j2**](configure_appformix/network_devices.j2) using the variables [**network_devices.yml**](configure_appformix/network_devices.yml). The rendered file is [**network_devices.json**](configure_appformix/network_devices.json).  
```
python configure_appformix/network_devices.py
more configure_appformix/network_devices.json
```

From your appformix directory, update ```group_vars/all``` file: 
```
cd appformix-2.15.2/
vi group_vars/all
```
to make sure it contains this:
```
network_device_file_name: /path_to/network_devices.json
appformix_network_device_monitoring_enabled: true
appformix_jti_network_device_monitoring_enabled: true
appformix_plugins:
   - plugin_info: 'certified_plugins/jti_network_device_usage.json'
   - plugin_info: 'certified_plugins/snmp_network_device_routing_engine.json'
   - plugin_info: 'certified_plugins/snmp_network_device_usage.json'
```

Then, from your appformix directory, re-run the 'Appformix installation Ansible playbook':
```
cd appformix-2.15.2/
ansible-playbook -i inventory appformix_standalone.yml
```
## Configure the network devices with the SNMP community used by Appformix

You need to configure the network devices with the SNMP community used by Appformix. The script [**snmp.py**](configure_junos/snmp.py) renders the template [**snmp.j2**](configure_junos/snmp.j2) using the variables [**network_devices.yml**](configure_appformix/network_devices.yml). The rendered file is [**snmp.conf**](configure_junos/snmp.conf). This file is then loaded and committed on all network devices used with SNMP monitoring.
 
```
python configure_junos/snmp.py
configured device 172.30.52.85 with snmp community public
configured device 172.30.52.86 with snmp community public
```
```
more configure_junos/snmp.conf
```

## Configure the network devices for JTI telemetry

For JTI streaming telemetry, Appformix uses NETCONF to automatically configure the network devices:  
```
lab@vmx-1-vcp> show system commit
0   2018-03-22 16:32:37 UTC by lab via netconf
1   2018-03-22 16:32:33 UTC by lab via netconf
```
```
lab@vmx-1-vcp> show configuration | compare rollback 1
[edit services analytics]
+    sensor Interface_Sensor {
+        server-name appformix-telemetry;
+        export-name appformix;
+        resource /junos/system/linecard/interface/;
+    }

lab@vmx-1-vcp> show configuration | compare rollback 2
[edit]
+  services {
+      analytics {
+          streaming-server appformix-telemetry {
+              remote-address 172.30.52.157;
+              remote-port 42596;
+          }
+          export-profile appformix {
+              local-address 192.168.1.1;
+              local-port 21112;
+              dscp 20;
+              reporting-rate 60;
+              format gpb;
+              transport udp;
+          }
+          sensor Interface_Sensor {
+              server-name appformix-telemetry;
+              export-name appformix;
+              resource /junos/system/linecard/interface/;
+          }
+      }
+  }

lab@vmx-1-vcp>
```
Run this command to show the installed sensors: 
```
lab@vmx-1-vcp> show agent sensors
```

If Appformix has serveral ip addresses, and you want to configure the network devices to use a different IP address than the one configured by appformix for telemetry server, execute the python script [**telemetry.py**](configure_junos/telemetry.py). 
The python script [**telemetry.py**](configure_junos/telemetry.py) renders the template [**telemetry.j2**](configure_junos/telemetry.j2) using the variables [**network_devices.yml**](configure_appformix/network_devices.yml). The rendered file is [**telemetry.conf**](configure_junos/telemetry.conf). This file is then loaded and committed on all network devices used with JTI telemetry.  

```
cd automated_junos_show_commands_collection_with_appformix_python
more configure_appformix/network_devices.yml
```
```
configure_junos/telemetry.py
configured device 172.30.52.155 with telemetry server ip 192.168.1.100
configured device 172.30.52.156 with telemetry server ip 192.168.1.100
```
```
# more configure_junos/telemetry.conf
set services analytics streaming-server appformix-telemetry remote-address 192.168.1.100
```
Verify on your network devices: 
```
lab@vmx-1-vcp> show configuration services analytics streaming-server appformix-telemetry remote-address
remote-address 192.168.1.100;

lab@vmx-1-vcp> show configuration | compare rollback 1
[edit services analytics streaming-server appformix-telemetry]
-    remote-address 172.30.52.157;
+    remote-address 192.168.1.100;

lab@vmx-1-vcp> show system commit
0   2018-03-23 00:34:47 UTC by lab via netconf

```
```
lab@vmx-1-vcp> show agent sensors

Sensor Information :

    Name                                    : Interface_Sensor
    Resource                                : /junos/system/linecard/interface/
    Version                                 : 1.1
    Sensor-id                               : 150000323
    Subscription-ID                         : 562950103421635
    Parent-Sensor-Name                      : Not applicable
    Component(s)                            : PFE

    Server Information :

        Name                                : appformix-telemetry
        Scope-id                            : 0
        Remote-Address                      : 192.168.1.100
        Remote-port                         : 42596
        Transport-protocol                  : UDP

    Profile Information :

        Name                                : appformix
        Reporting-interval                  : 60
        Payload-size                        : 5000
        Address                             : 192.168.1.1
        Port                                : 21112
        Timestamp                           : 1
        Format                              : GPB
        DSCP                                : 20
        Forwarding-class                    : 255

```
## Webhooks

A webhook is notification using an HTTP POST. A webhook is sent by a system A to push data (json body as example) to a system B when an event occurred in the system A. Then the system B will decide what to do with these details. Usage is event driven automation.   

Appformix supports webhooks. A notification is generated when the condition of an alarm is observed. You can configure an alarm to post notifications to an external HTTP endpoint. AppFormix will post a JSON payload to the endpoint for each notification.  

## Event driven automation

The script [**webhook_listener.py**](webhook_listener.py) listens to webhooks and binds a function to each URL.   

It binds the webhook ```http://x.x.x.x:12345/junos/collect_data``` (POST with JSON body) from appformix to the script [**push_to_git.py**](push_to_git.py).  
The device name is extracted from the JSON body and passed as an argument to the script [**push_to_git.py**](push_to_git.py).  
The script [**push_to_git.py**](push_to_git.py) then collects data on this junos device (junos show commands output) and upload the data collected to a Git server.  

## How to reproduce the event driven automation demo

Define webhooks on Appformix.  
From the GUI, select: ```settings```, ```notification settings```, ```notification services```, ```add service``` (provide a service name and a service endpoint), ```setup```.  

Create Appformix alarms, and map these alarms to webhooks.  
You can do it from the Appformix GUI. Select add rule. Then it should be obvious. ```scope```: select network devices, ```generate```: select generate alert, ```notification```: select custom service, ```services```: select the service name you created (webhook), then ```save```.

Start the listener [**webhook_listener.py**](webhook_listener.py):
```
# python webhook_listener.py
 * Running on http://0.0.0.0:12345/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 290-737-301
```

## Automated data collection demo

Have Appformix to generate a webhook notification. You can use the scripts in the [**trigger_alarms**](trigger_alarms) directory.  

The python script [**webhook_listener.py**](webhook_listener.py) will receive HTTP POST and bind them to other python functions.  

The script [**webhook_listener.py**](webhook_listener.py) binds the Webhook ```http://webhook_listener_ip:12345/junos/collect_data``` to the script [**push_to_git.py**](push_to_git.py).  
The script [**webhook_listener.py**](webhook_listener.py) also extracts the device name from the JSON body and passes it to the script [**push_to_git.py**](push_to_git.py).  
The script [**push_to_git.py**](push_to_git.py) collect junos show commands on the faulty device (the one notified by Appformix) and pushes the data collected to a Git server.   
Here's the output of [**webhook_listener.py**](webhook_listener.py) for this webhook 
```
172.18.0.5 - - [27/Mar/2018 13:11:30] "POST /junos/collect_data HTTP/1.1" 201 -
```
The data is automatically collected from the faulty device and saved to the local repository:
```
# ls data_collected/vmx104/
show chassis hardware.txt  show interfaces extensive.txt  show version.txt
```
The data collected is then pushed automatically on the remote repository:  
```
# git status
```
```
# git log -1
```
So the data collected is available on the remote repository: [**vmx104**](data_collected/vmx104)  

