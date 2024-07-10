# Webex_bulk_user_deletion

Please follow the below instructions to ensure a smooth execution of the activity:
Access the Virtual Desktop Infrastructure (VDI) environment.
Install the necessary software tools, including PyCharm and any other dependencies required for the script.
 
What needs to be done: - 
 
1) Download and Install Python Compiler from - https://www.python.org/downloads/ (Python 3.12.3 and above)
2) Then same PyCharm community version IDE from - https://www.jetbrains.com/pycharm/download/?section=windows
 
Please make sure to follow the steps - Next > Next > (as shown below) > Next > Install > (let it complete) > Reboot now.
 

 
3) Download the attached Python scripts in VDI or Copy the exact script from this file - New_webex_del.py

New Steps: - after installation - 
4) Create a folder name "Webex Deletion".
5) Add the files name "New_webex_del.py", ".env', "requirements.txt" in the folder (Rename the files name as mentioned if not)
6) Go to PyCharm > File > Open > (search the directory - Webex Deletion) and Open.
6) there will be a requirement.txt file, Run it in the terminal through the PyCharm.
 
What needs to be taken care of while activity: - 
 
1) Keep the API token handy - https://developer.webex.com/docs/getting-started

 
2) Do make sure NOT TO delete/deactivate the same users. This may cause some issues otherwise.
3) Make sure that each on of us should use their different Access Token and that the list of users that we are working on does not overlap, because in that case we might end up with API response errors.
4) We'll be using 100 users per csv file so, make sure file should not exceed the user limit.
