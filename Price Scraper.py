#Sebastian Bruce, 200561191
#04/08/2024 - 5pm
#Scrape web data for product prices based off of user saved links
#Write the data to google sheets

#import modules
import ezsheets, requests, re, os, time
from bs4 import BeautifulSoup
import pyinputplus as pyip

#Function to look at url and grab the website name from it
def extractWebsiteName(url):

    #Compile regex pattern to extract website name
    #Searches for any string between www. and the domain extension
    regexPattern = r"www\.(.*?)\.(com|ca|org|net|edu|gov|mil)"

    #Search for the pattern in the URL
    match = re.search(regexPattern, url)

    #Return extracted website name if match found, otherwise return full domain
    if match:
        return match.group(1)
    else:
        return url

#Scrape web data and return prices found
def scrapePrices(file):

    #Initiate variables to be changed later
    websiteList = []
    priceList = []
    hyperlinkList = []
    statusList = []
    count = 0

    #Reads first line of the txt file to find and store the MSRP
    msrp = file.readline()

    #Look through the txt file and store each URL to the list
    for line in file:

        #Skips the first line so that only URLs are stored
        if line != msrp:

            #Break the loop if an empty line is encountered (meaning all URLs have been read)
            if not line.strip():
                break

            #Remove any leading or trailing whitespace characters, grab and store URL
            url = line.strip()

            #Append the URL to the list
            websiteList.append(url)

    #Compile regex pattern to search for prices
    #This will pick up any number so it will be refined further later
    #We can't just compile a pattern to only look for ($XX.XX) because many websites have scraping protection and won't format the price that way
    regexObject = re.compile(r"\$?\d+(\.\d{2})?")

    #Go through each URL that was found from the txt file
    for website in websiteList:

        #Create a hyperlink formatted for google sheets
        hyperlink = f'=HYPERLINK("{website}", "{extractWebsiteName(website).title()}")'

        #Attempt to access the website and retrieve its content
        try:
            #Open and read URL
            response = requests.get(website)
            response.raise_for_status()

            #Scrape all html data and split into list with every line
            soup = BeautifulSoup(response.content, "html.parser")
            listOfLines = soup.prettify()
            listOfLines = listOfLines.splitlines()

            #Initiate toggle variable
            priceFound = False

            #Run through each line of html
            for line in listOfLines:

                #Increment count
                count += 1

                #Search the line for all matches of the regex pattern
                matches = re.finditer(regexObject, line)

                #Look through every match found
                for match in matches:

                    #Store match object
                    price = match.group(0)

                    #Convert the extracted number to a float for comparison
                    priceFloat = float(re.sub(r'[^\d.]', '', price))

                    #If the number is somewhat higher or significantly lower than the MSRP of the product we can assume its not the price and move on
                    if priceFloat > float(msrp) * 1.05 or priceFloat < float(msrp) * 0.8:
                        continue
                    
                    #Format the number to be in dollar form for storage
                    price = "${:.2f}".format(float(priceFloat))

                    #Check the line to see if it has a dollar sign so we can assume a price
                    if "$" in line:

                        #Append the price to the list
                        priceList.append(price)

                        #Append the status to the list
                        statusList.append("Found!")

                        print(f"Price {price} found on {website}")
                        
                        #Toggle the variable
                        priceFound = True

                        break

                    #If no dollar sign is found its still possibly the price just formatted differently
                    #So we check the html code to see if it contains the string "price"
                    #Usually the class of the price element will contain the word "price" in some way
                    elif "price" in line.lower():

                        #Append the price to the list
                        priceList.append(price)

                        #Append the status to the list
                        statusList.append("Found!")

                        print(f"Price {price} found on {website}")
                        
                        #Toggle the variable
                        priceFound = True

                        break

                #If the toggle has been flipped (meaning a possible price is found) we break the loop
                if priceFound:
                    break

            #If the toggle isn't flipped (meaning no possible price is found)
            if not priceFound:

                #Append an urgent message so the user knows no price is found
                priceList.append("CHECK MANUALLY!")
                statusList.append("No Price Found.")

                print(f"No price found on {website}")

        #If we can't access the website (site down, bot protection, 500 error, 403 error) we throw an error
        except Exception as e:

            #Append an urgent message so the user knows no price is found
            priceList.append("CHECK MANUALLY!")
            statusList.append("Error Accessing.")

            print(f"Error accessing {website}: {e}")
        
        #Append the hyperlink to the list
        hyperlinkList.append(hyperlink)

    #Return the relevant lists to the caller
    return hyperlinkList, priceList, statusList

#Write to the google sheet
def writeToSheet(hyperlinkList, priceList, statusList, sheetIndex):
    
    #Grab start time
    startTime = time.time()

    print("Updating spreadsheet (this may take a few seconds)")

    #grab the global variable
    global spreadsheet

    #Set active sheet to the index parameter passed
    sheet = spreadsheet.sheets[sheetIndex]

    #Clear the sheet in case amount of information has changed
    sheet.clear()

    #Update the sheet with the relevant information
    sheet.updateRow(1, hyperlinkList)
    sheet.updateRow(2, priceList)
    sheet.updateRow(3, statusList)

    #Grab end time
    endTime = time.time()

    #Calculate elapsed time
    elapsedTime = endTime - startTime

    #Display amount of time takes
    print(f"Updated (took {elapsedTime:.2f} seconds).")

#Pick the file to be used
def pickFile(choice):

    #Initialize variables
    count = 1
    fileIndexList = []

    #Print each file in the folder, use count to display input options
    print("Files in folder:")
    for fileName in files:
        print(f"{count}. {fileName}")

        #Append the file index to the list
        fileIndexList.append(files.index(fileName))

        #Increment count
        count += 1

    #If choice parameter is 1 (meaning the user wants to run a report)
    #Print an additional option and run a slightly different input statement
    if choice == 1:
        print(f"{count}. UPDATE ALL")

        #User input is taken and validated to make sure they enter a valid option
        index = pyip.inputInt(prompt = "Which file would you like to pick?: ", min = 1, max = count)

    #If choice parameter isn't 1 (meaning the user wants to edit)
    else:
        
        #User input is taken and validated to make sure they enter a valid option
        index = pyip.inputInt(prompt = "Which file would you like to pick?: ", min = 1, max = count - 1)

    #If choice parameter is 1 (meaning the user wants to run a report)
    if choice == 1:

        #If the user enters the number corresponding to the update all option
        if index == count:
            print("Updating All.")

            #Call the report all function and pass the index list
            reportAll(fileIndexList)

    #Return the relevant metrics to the caller
    return index - 1, count - 1

#Edit the selected file
def editFile(index):

    #Initialize variables to be updated
    url = ""
    choice = ""

    #Grab the global variable
    global directory

    #Using the index passed find the corresponding file
    fileName = files[index]

    #Create the full path using the directory and file name
    fullPath = os.path.join(directory, fileName)

    #Open the txt file in append mode
    file = open(fullPath, 'a')


    print(f"Now editing {fullPath}")
    print("1. Add URL\n2. Delete URL")

    #Prompt the user to pick an option or quit and validate the input
    #pyinputplus cant be used here for inputInt since it will reject "q" which is needed to quit
    #We prompt the first time outside of the loop so it doesn't before run every time
    choice = input("Enter your choice (1/2 or 'q' to quit and save): ")

    #Repeat this loop until the user enters "q" to quit
    #Modify the input to lowercase incase they entered a capital "q"
    while choice.lower() != "q":

        #If the user enters 1, run add mode
        if int(choice) == 1:

            #Repeat this loop until the user enters "q" to quit
            while url.lower() != "q":
                
                #Prompt the user to enter a URL
                #pyip.inputURL cant be used since it will reject q
                url = input("Enter a URL to store (or 'q' to quit and save): ")

                #Manually validate the URL as any URL should have at least on of these
                #Run until they enter a valid URL
                while "http" not in url and ".com" not in url and ".ca" not in url:

                    #If user wants to quit, break the loop
                    if url.lower() == "q":
                        break

                    #Reprompt the user to enter a URL
                    url = input("Invalid URL, try again (or 'q' to quit and save): ")

                #If user wants to quit, break outer loop as well
                if url.lower() == "q":
                    break

                #Once they enter a valid URL write it to the txt file and move to the next line
                file.write(url + '\n')

                print(f"URL {url} written to {fileName} successfully.")

        #If the user enters a 2, run delete mode   
        elif int(choice) == 2:
            
            #Repeat this loop until the user enters "q" to quit
            while str(choice).lower() != "q":

                #Open the selected file in read mode
                file = open(fullPath, "r")

                #Store each line (after each new line character) to a list
                lines = file.readlines()

                #Initiate count variable to be incremented
                count = 1

                #Print each URL from the list, use count to display input options
                for line in lines:
                    print(f"{count}. {line}")

                    #Increment count variable
                    count += 1

                #Prompt the user to pick a URL to delete
                #"1-{count - 1}" ensures that it always displays the right number
                choice = input(f"Enter your choice (1-{count - 1} or 'q' to quit and save): ")

                #Validate user input
                #Reprompt the user to enter a valid number
                while int(choice) > count - 1 or int(choice) < 1 or type(count) == str:

                    #If user wants to quit, break the loop
                    if choice == "q":
                        break

                    choice = input(f"Invalid input, try again (or 'q' to quit and save): ")
                
                #If user wants to quit, break outer loop as well
                    if choice == "q":
                        break
                
                #If a valid number is entered, delete that URL from the txt file and save
                del lines[int(choice) - 1]
                file = open(fullPath, 'w')
                file.writelines(lines)
                file.close()

        #If user wants to quit, continue which will stop the while loop since the condition is met
        elif choice == "q":
            continue

        #If the user enters anything other than 1, 2 or "q" then reprompt them and continue the loop
        else:
            choice = input("Invalid input, try again: ")
            continue

        #If none of the past breaks/continues are ran, then reprompt the user and the loop continues
        print("1. Add URL\n2. Delete URL")
        choice = input("Enter your choice (1/2 or 'q' to quit and save): ")
    
    #Save and close the file
    file.close()
    print("File closed and saved.")

    #Ask user if they want to run a report
    response = input("Would you run a report now? (y/n) ")

    #If the user enters y (yes) then run the report
    if response.lower() == "y":
        runReport(index)

    #If the user enters anything else just end
    else:
        print("Operation Ended.")

#Add a txt file
def addFile():
    
    #Prompt user for file name, strip leading or trailing whitespace, and add the .txt file extension
    fileName = input("Enter file name: ").strip() + ".txt"

    #Create the full path by joining the directory with the name they entered, and Make It Title Case
    fullPath = os.path.join(directory, fileName.title())

    #If that path already exists (meaning a file corresponds exactly to the name they entered), direct them to the file
    if os.path.exists(fullPath):
        print("File already exists, opening file.")

    #If the file doesn't already exist
    else:

        #Create and open the file in write mode
        file = open(fullPath, "w")

        #(One time upon creation) prompt the user to enter the MSRP of the product as a float and validate it
        msrp = pyip.inputFloat("Enter the product MSRP (XX.XX): ")

        #Once a valid float is entered write the MSRP to the file and go to the next line
        file.write(f"{msrp}\n")

        #Save and close the file
        file.close()

        #Append the file name to the built in os file list
        files.append(fileName)

    #Call the edit file function and pass the index of the file just created
    editFile(files.index(fileName))
    
    print("File created, you can now edit file.")

#Create a new sheet in the existing google spreadsheet
def newSheet(fileName):

    #Grab global variables
    global sheetIndex, spreadsheet

    #Take the passed file name parameter and remove the .txt extension
    fileName = fileName[:-4]
    
    #If theres no existing sheet with the same name
    if fileName not in spreadsheet.sheetTitles:

        #Create a new sheet with that name
        newSheet = spreadsheet.createSheet(fileName)

        #Grab all of the sheet titles and store them in a list
        sheetTitles = spreadsheet.sheetTitles

        #Find the index of the new sheet based on its place in the sheet title list
        sheetIndex = sheetTitles.index(fileName)

#Run a report (update spreadsheet information based on the index passed)
def runReport(txtIndex):

    #Grab global variables
    global directory, sheetIndex, spreadsheet

    #Grab the file name based on its index in the folder
    fileName = files[txtIndex]

    ##Create the full path by joining the directory with the file name
    fullPath = os.path.join(directory, fileName)

    #Open the txt file in read mode
    file = open(fullPath, 'r')

    #Call the new sheet function to create a new sheet based on the file name
    #If a sheet with that name already exists no new sheet will be created (handled in the function itself)
    newSheet(fileName)

    print(f"Now running report for {fullPath}")

    #Call the scrape prices function and store the lists it returns
    hyperlinkList, priceList, statusList = scrapePrices(file)

    #Grab all of the sheet titles and store them in a list
    sheetTitles = spreadsheet.sheetTitles
    
    #Take the passed file name parameter and remove the .txt extension
    fileName = fileName[:-4]

    #Find the index of the new sheet based on its place in the sheet title list
    sheetIndex = sheetTitles.index(fileName)

    #Call the write to sheet function with the appropriate arguments
    writeToSheet(hyperlinkList, priceList, statusList, sheetIndex)

#Will run a report for every product and update its spreadsheet
def reportAll(fileIndexList):

    #For every index number in the passed list, a report is ran
    for index in fileIndexList:
        runReport(index)

#Store the directory that stores the txt files
directory = "C:\\Python Final\\txt files"

#If the directory doesn't exist, make it
if not os.path.exists(directory):
    os.makedirs(directory)

#Store every file name from the directory in a list
files = os.listdir(directory)

#Open spreadsheet
spreadsheet = ezsheets.Spreadsheet("1wA7K-DtS3jGK0vEkEV3Z9L1II0C_3SN_YpK_c_4qImk")

#Initialize a global variable that needs to be used between functions
sheetIndex = 0

#If the txt files folder is empty (meaning this is likely the users first execution)
if len(files) == 0:
    
    print("Welcome to your first use, to start we must add a file to store the product links.")

    #Set choice to 3 (Add a File)
    choice = int(3)

#If the txt files folder isn't empty (meaning the user has ran the program before
else:

    #Prompt the user to pick an option and validate it
    print("1. Run Report\n2. Edit File\n3. Add a File")
    choice = pyip.inputInt(prompt="Enter your choice (1/2/3): ", min=1, max=3)


#If user enters 1 (Run Report)
if choice == 1:

    #Call the pick file function and store the variables it returns
    index, count = pickFile(choice)

    #If index doesn't equal count (meaning the user didn't choose to update all)
    if index != count:

        #Run the report based on the index passed from pick file function
        runReport(index)

#If user enters 2 (Edit File)
elif choice == 2:

    #Call the pick file function and store the variables it returns
    index, count = pickFile(choice)

    #Edit the file based on the index from the pick file function
    editFile(index)

#If user enters 3 (Add a File)
elif choice == 3:

    #Call the add file function to create a new txt file
    addFile()
