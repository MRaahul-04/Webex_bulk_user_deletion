import requests
import json
import os
import csv
import urllib
import sys
import time
from dotenv import load_dotenv

#############  Load Environment Variables  #############
load_dotenv()
csvFilePaths = os.getenv('CSV_FILE_PATHS').split(',')  # Comma-separated list of CSV file paths
accessToken = os.getenv('ACCESS_TOKEN')

#############  Definitions  #############
loopCount = 0
deletedCount = 0
errorCount = 0
totalDeletedCount = 0
totalErrorCount = 0
userEmails = []
errorMessage = ''
listPeopleURL = 'https://webexapis.com/v1/people'  # Webex CH List People API URL
deletePersonURL = 'https://webexapis.com/v1/people/'  # Webex CH Delete Person API URL
getMyDetailsURL = 'https://webexapis.com/v1/people/me'  # Webex CH Get My Details API URL

#############   Validate Access Token  #############
validationResponse = requests.get(getMyDetailsURL, headers={'Authorization': 'Bearer ' + accessToken})
if validationResponse.status_code == 401:
    print('\nAccess Token was invalid. Please check your .env file and try again.')
    exit()
print('Access Token validated successfully.\n')

#############   Process Each CSV File  #############
for csvFilePath in csvFilePaths:
    csvFilePath = csvFilePath.strip()
    if not os.path.isfile(csvFilePath):
        print(f'No Input CSV file found at: {csvFilePath}')
        continue

    print(f'Processing file: {csvFilePath}')
    userEmails = []
    with open(csvFilePath, 'r') as csvFile:
        readCSV = csv.reader(csvFile, delimiter=',', quotechar='"')
        next(readCSV, None)  # skip header line
        for row in readCSV:
            if len(row) >= 3 and row[3] != '':
                userEmails.append(row[3])
    totalUsers = len(userEmails)

    if totalUsers > 100:
        print(
            'You have attempted to delete more than 100 users in a single file. Please ensure each file has 100 users or less.\n')
        continue

    #############  User Confirmation  #############
    print('Total Users to Delete:', str(totalUsers))
    proceed = input(f'Do you want to proceed with deleting users from {csvFilePath}? (Y/N) ')
    if proceed.upper() != 'Y' and proceed.upper() != 'YES':
        print('You have chosen to skip this file. Moving to the next file.\n')
        continue
    print('\nDelete in progress.  Please wait, the script takes 2 - 3 seconds per user on average...')
    print('*****************************************************************************')
    #############  End User Confirmation  #############

    # Create CSV file for error tracking
    errorFilePath = os.path.join(os.path.dirname(csvFilePath), 'Errors.csv')
    with open(errorFilePath, 'w') as csvfile:
        csvfile.write('User Email,API Call Response Code,Response Message\n')

    #############   Loop to Delete Users from the CSV file  #############
    loopCount = 0
    deletedCount = 0
    errorCount = 0

    while loopCount < totalUsers:
        response = requests.get(listPeopleURL + '?email=' + urllib.parse.quote_plus(userEmails[loopCount]),
                                headers={'Authorization': 'Bearer ' + accessToken})
        while response.status_code == 429:
            print('Webex returned a 429 response (too many API calls at once). Pausing script for 30 seconds...')
            time.sleep(30)
            response = requests.get(listPeopleURL + '?email=' + urllib.parse.quote_plus(userEmails[loopCount]),
                                    headers={'Authorization': 'Bearer ' + accessToken})
        if response.status_code != 200 or len(response.json()['items']) == 0:
            if response.status_code != 200:
                print('Error: Get User ID API call error', str(response.status_code), 'on user',
                      str(userEmails[loopCount]))
                errorMessage = response.json()['message']
            else:
                print('Error: User not found for email', str(userEmails[loopCount]))
                errorMessage = 'No user found with that email.'
            with open(errorFilePath, 'a') as csvfile:
                csvfile.write(str(userEmails[loopCount]) + ',' + str(response.status_code) + ',' + errorMessage + '\n')
            errorCount += 1
        else:
            for users in response.json()['items']:
                deleteResponse = requests.delete(deletePersonURL + users['id'],
                                                 headers={'Authorization': 'Bearer ' + accessToken})
                while deleteResponse.status_code == 429:
                    print(
                        'Webex returned a 429 response (too many API calls at once). Pausing script for 30 seconds...')
                    time.sleep(30)
                    deleteResponse = requests.delete(deletePersonURL + users['id'],
                                                     headers={'Authorization': 'Bearer ' + accessToken})
                if deleteResponse.status_code != 204:
                    print('Error: Delete User API call error', str(deleteResponse.status_code), 'on user',
                          str(userEmails[loopCount]))
                    errorMessage = deleteResponse.json()['message']
                    with open(errorFilePath, 'a') as csvfile:
                        csvfile.write(
                            str(userEmails[loopCount]) + ',' + str(
                                deleteResponse.status_code) + ',' + errorMessage + '\n')
                    errorCount += 1
                else:
                    deletedCount += 1
                    print('Deleted user #' + str(deletedCount) + ': ' + str(userEmails[loopCount]))
        loopCount += 1

    print('\n[ Delete complete for file:', csvFilePath,']')
    print('[ Deleted', str(deletedCount), 'users, with', str(errorCount), 'errors. ]')
    print('*****************************************************************************')
    totalDeletedCount += deletedCount
    totalErrorCount += errorCount
    if errorCount > 0:
        print('Please check the Errors.csv file for users that were unable to be deleted.')
        print('[ NOTE:- Delete the users mentioned under error manually from the Control Hub ]\n')

    # Perform the countdown if there are more CSV files to process
    if csvFilePath != csvFilePaths[-1]:
        print('Pausing for 30 seconds before processing the next file...')
        for remaining in range(30, 0, -1):
            sys.stdout.write(f'\rContinuing in {remaining} seconds... ')
            sys.stdout.flush()
            time.sleep(1)
        print('\rContinuing...\n')  # Print continuation message after countdown finishes

print('\n******************************************************')
print('All files executed successfully.')
print('Total Deleted Users:', str(totalDeletedCount))
print('Total Errors:', str(totalErrorCount))
print('******************************************************')
