
# coding: utf-8

# In the piece of code, we run through a bunch of yelp business pages, and attempt to extract some important details of restaurants that are available on yelp. We have a FeatureExtraction Class, that is made up of several functions that extract the important features. The main() function, implemented outside the class, can be called to run the program, input more businesses, and then it outputs a list of relevant restaurant details. The following explains the features extracted: 
# 
# 1) Name: Simply the name of the business 
# 2) Address: The address. If all details are available, we divide it into street, city, state and zip code (4 feature points! (Entered as dictionary structure in python)
# 3) Telephone: Contact of location 
# 4) Website: Link to business' official page, if available 
# 5) Menu: Link to Menu, if available 
# 6) Price Range: How expensive the restaurant is, sometimes in dollar terms, sometimes in words like "Moderate" 
# 7) Hours: The operational hours of the restaurant, if available on Yelp (as dictionary structure)
# 8) Other Features: An extraction of other features from Yelp, like the column they usually have listed on the side indicating Delivery, Take-out, Parking, etc. Can range from 2-3 features to 15-20 features (as dictionary structure)
# 
# 
# 
# 

from bs4 import BeautifulSoup 
import lxml
import requests
import re
import urllib.request as req
import urllib

class FeatureExtraction:
        
    def extract(self,obj):  # function cleans up the portion of html code remaining 
        item = obj[0].string
        item.replace('n','')
        return item.strip()

    def name(self,obj): #extracts name of business
        location_name = obj.find_all('h1','biz-page-title')
        return self.extract(location_name)
    
    def address(self,obj): #extracts address of business 
        location_address = obj.find_all('address')
        add = self.extract(location_address)
        add = add.split(',') # we do this extra work to extract the specific street, city, state and zip 
        if len(add) != 3: 
            return ''.join(add)
        state = (add[2].strip()).split(' ')
        location = dict()
        location.update({'street': add[0]})
        location.update({'City': add[1]})
        location.update({'State':state[0]})
        location.update({'zip':state[1]})
        return location

    def telephone(self,obj): # get contact number, convert to an integer value before returning 
        location_contact = obj.find_all('span','biz-phone')
        contact = self.extract(location_contact)
        #we then find just the numbers to return it as a int variable 
        number = re.findall(r'\d+',contact)
        number = ''.join(number)
        if len(number) != 10: 
            return 'Invalid Number'
        return int(number)

    def website(self,obj): #get website link 
        location_website = obj.find_all('div','biz-website')
        if not location_website: 
            return 'link not provided'
        webpage = location_website[0].text
        webpage = webpage.replace('\n',' ')
        webpage = webpage.split()
        webpage.remove('website')
        webpage.remove('Business')
        weblink = str('http://www.'+''.join(webpage))
        return weblink

    def priceRange(self,obj): # find price range, some in words and some in dollar terms 
        price = obj.find_all('dd','nowrap price-description')
        return self.extract(price)

    def menu(self,base_url,obj): # access link to the menu 
        location_menu = obj.find_all('a',class_='menu-explore link-more')
        if not location_menu: 
            return "Maybe available on website"
        menu_link = location_menu[0].get('href')
        return str(base_url+menu_link)

    def hours(self,obj): # find the working hours of the business 
        schedule = dict()
        tables = obj.find_all('tr')
        if not tables: 
            return 'Hours not updated'
        for i in range(0,7): 
            day = tables[i].text
            day = day.split('\n')
            day = list(filter(None,day))   # removing all the empty strings in list 
            if len(day) < 2: 
                return 'Hours not updated'
            schedule.update({day[0]:day[1]})
        return schedule    

    
    def otherFeatures(self,obj): #extract other features like delivery, take-out, wi-fi, etc
        attributes = obj.find_all('div',class_='short-def-list')
        features = attributes[0]('dt')
        outputs = attributes[0]('dd')
        others = dict()
        for i in range(0,len(features)): 
            feature = ((features[i].string).replace('\n',' ')).strip()
            output = ((outputs[i].string).replace('\n',' ')).strip()
            others.update({feature:output})
        return others
         
    def __init__(self,obj,base_url):  # class constructor    
        self.name = self.name(obj)
        self.address = self.address(obj)
        self.telephone = self.telephone(obj)
        self.website = self.website(obj)
        self.price = self.priceRange(obj)
        self.menu = self.menu(base_url,obj)
        self.hours = self.hours(obj)
        self.otherFeatures = self.otherFeatures(obj)


def main(): 
    
    #base url is YELP, others links are as requested 
    base_url = 'http://www.yelp.com'
    links = ['http://www.yelp.com/biz/salt-and-straw-los-angeles',
            'http://www.yelp.com/biz/smittys-famous-fish-and-chicken-culver-city',
            'http://www.yelp.com/biz/zankou-chicken-los-angeles-7',
            'http://www.yelp.com/biz/chego-los-angeles-5',
            'http://www.yelp.com/biz/ambala-dhaba-homestyle-indian-los-angeles',
            'http://www.yelp.com/biz/colony-cafe-miami-beach']

    # this whole loops tests if the URL that the user input is a valid yelp business or not, 
    # and also checks if the user wants to input more links
    # I should have had this as a function of my previous class, my bad
    decision = input("Do you wish to enter more Yelp Businesses(Y/N)?:")
    while (decision == 'Y'):
        add_link = input("Please enter link:")
        
        #checks to see if input is in URL form
        if not re.match('http?://(?:www)(.?yelp)(.?com)/biz',add_link):
            print ("Please enter a Yelp Business URL")
            continue
            
        #checks to see if URL is valud 
        request = req.Request(add_link)
        try: 
            response = req.urlopen(request)
            links.append(add_link)
            decision = input("Do you wish to add more(Y/N):")
            if (decision == 'Y'):
                continue
            break
        except: 
            decision = input("Link is invalid. Do you wish to reenter (Y/N):")
            if (decision == 'Y'): 
                continue

    #iterations through all the links to extract the important features         
    for link in links: 
        r = requests.get(link)
        file = r.text
        soup = BeautifulSoup(file,"lxml")
        s = FeatureExtraction(soup,base_url)
        print('\n')
        print('Name:',s.name)
        print('Address:',s.address)
        print('Contact:',s.telephone)
        print('Website:',s.website)
        print('Pricing:',s.price)
        print('Menu:',s.menu)
        print('Hours:',s.hours)
        print('Other Details:',s.otherFeatures)


main()




