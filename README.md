# Background
_For the powerpoint presentation of the project: *https://drive.google.com/open?id=0B20K5XixvBSyeHkyS3R2NW5PQms*_

This repo contains the code for project Lockee's **backend**, an **IoT project** aiming at creating an universal **smart lock**. The brainchild of a team of five and three months of hard work, Lockee has won the **first prize** in the **FOR IT 2016 Cluj tech competition**, a contest whose purpose was to introduce high school students into the IT world. The project had the following features:
- **The ability the open/close a door using the door's key**
- The ability to create an account/login on the Lockee platform & Android app
- The ability to add the ownership over a lock using an ID code unique to each hypotetical lock (we only made 1 prototype )
- **The ability the generate "share ID's" which could be used to share a lock with a friend who only had to install the Lockee app**

# About the code
The code is basically a REST API connected to a MySQL DB that served three type of clients
- Web clients
- Android clients
- The IoT devices ( based on **Arduino** )

**The API handles the following**
    - User login/register _although_ it does not check for the validity of the registration mail
    - DB updates of a Lockee's status
    - Answering queries made by web/android clients
    - **Generation and validity check for the share IDs ( the share IDs can be time restricted)**
    - **Enhancing the Android app with real time checks ( e.g. valid/invalid email field, password too weak message )**
    - Serving HTML/CSS dynamic web pages to the web clients
    
# Behind the scenes
The code was written using the Django Framework and MySQL for DB

# Kudos
##### Team Glimpse 
- Sturza Bogdan, Team's mentor and the coolest guy I know https://github.com/sturza
- Popa Adrian, Android application and the software side for the Arduino https://github.com/AdiPoPa
- Cristurean Roxana, Frontend
- Miron Dănuț, Arduino Hardware
- Dan Tudor, Project demo and editing
