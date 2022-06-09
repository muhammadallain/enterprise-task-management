# Enterprise Task Management System
Helps you make task-boards for projects so your team can create, share and manage tasks easily.

## Requirements
* Python 3.8
* Google-App-Engine SDK

## Installing Google App Engine SDK
Go to following link:
https://cloud.google.com/sdk/docs/install

The instruction in following lines are for Windows. If you have any other operating system follow the instruction on the page.
* Under Windows tab, download the Google Cloud CLI Installer
* Once downloaded, install.bat will run automatically
* During installation, it will ask following questions
* Do you want to help improve the Google Cloud SDK? (your answer is N)
* Modify your profile to update your $PATH and enable shell command completion (your answer is Y)
* If asked (Enter a path to an rc file to update, or leave blank to use [default] ) -> (accept the default)
* Once done, it will give you a GCloud console similar command prompt
* Run the following commands in Cloud shell to install app-engine-python and app-engine-python-extras

gcloud components install app-engine-python app-engine-python-extras

## Setting up free App Engine Project
Go to following link and signin with google account if necessary
https://console.cloud.google.com/

* Go to the option to add a new project and give it a name.
* Don’t modify the location and hit create. 
* Once the project is created then you should see it in the dashboard.

Go to the hamburger menu on the top left (the three horizontal lines denoting a menu) and under “Serverless” click on “App 
Engine” don’t go into the sub menu here.

* Click on the button “Create Application”.
* Choose your region. (Mine is europe west for Ireland). Click Next.
* Language should be “python” and the environment should be “standard”.

Your app engine project is now setup.

This is a cloud application based on Google App Engine. A working Google cloud account is required to run this application. Follow the steps below to setup a free Google App Engine project to run this app.

