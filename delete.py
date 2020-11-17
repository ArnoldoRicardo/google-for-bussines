from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user']

def main():
    """Shows basic usage of the Admin SDK Directory API.
    Prints the emails and names of the first 10 users in the domain.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # delete unused users
    service = build('admin', 'directory_v1', credentials=creds)

    page_token = None
    params = {'customer': 'my_customer'}

    page = 0
    users_total = 0
    while True:
        try:
            if page_token:
                params['pageToken'] = page_token
            current_page = service.users().list(**params).execute()

            users = current_page.get('users', [])
            if not users:
                print('No users in the domain.')
                break
            else:
                users_total = users_total + len(users)
                print('Users page: ', page)
                for user in users:
                    last_login_time = datetime.strptime(user['lastLoginTime'], '%Y-%m-%dT%H:%M:%S.%fz')
                    # here go the date
                    if last_login_time < datetime(2016, 1, 1):
                        print('delete mail')
                        print(user['primaryEmail'])
                        service.users().delete(userKey=user['id']).execute()

            page_token = current_page.get('nextPageToken')
            page = page + 1

            if not page_token:
                break

        except:
            print('errors')
            break

    print(users_total)


if __name__ == '__main__':
    main()