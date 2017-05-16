# watson_stt_example
An example for watson Speech-To-Text service using python.
This code is based on: https://www.ibm.com/blogs/watson/2016/07/getting-robots-listen-using-watsons-speech-text-service/

# Dependencies
* bluemix account and speech-to-text service enabled
* watson-developer-cloud (sudo pip install --upgrade watson-developer-cloud)
* ws4py (sudo pip install --upgrade ws4py)


# Usage
* put username and password in account.conf
  ```
  [bluemix]
  username = your username
  password = your password
  ```
* run it 
  ```
  python main.py
  ```
