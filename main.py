import os
import hashlib

def listAffectingFiles():
    print("Listing csv file(s) in 'to_mask' folder that will be processed...")
    basepath = 'to_mask/'
    count = 1
    files = []
    for entry in os.listdir(basepath):
        if (entry.endswith('.csv')):
            if os.path.isfile(os.path.join(basepath, entry)):
                print(f"{count}. {entry}")
                files.append(entry)
                count += 1
    return files

def validateMultiCols(input):
    if not input.isdigit():
        inputArr = input.split(',')
        error = 0
        for col in inputArr:
            if not col.isdigit():  
                error = 1
                print ("Not a valid number. Please try again.")
                return 0
        if error == 0:
            return 1
    else:
        return 1
    
def mask(row,selCols,file,type='others'):
    for col in selCols:
        index = int(col) - 1 #change to index convention
        try:
            val = str(row[index])
            val = val.strip()
            if len(val) == 0: #for str type only
                val = ""
            
            if (type == 'mobile'):
                if len(val) < 8:
                    val = "1234567"
                else:
                    val = val[:-4] + '1234'
            else:
                valLen = len(val)
                val = hashlib.sha256(val.encode('UTF-8'))
                val = val.hexdigest() + "_" + str(valLen)
            row[index] = val
        except IndexError:
            continue 
        except Exception as e:
            print(f"[{file}] {e}")
            continue
    return row


def main():
    files = listAffectingFiles()
    if len(files) == 0:
        print("No csv files found in 'to_mask' folder. Please try again.\nProgram exited.")
        return
    delimiterObj = {
        "1" : ",",
        "2" : "|",
        "3" : "\\t"
    }
    print("""
Note for masking data:
- MOBILE masking will replace last 4 digits to '1234'. 
- OTHERS (e.g for Name, NRIC, sensitive data, etc.) masking will encrypt entire content using SHA-256 with added original content length.

Selecting column(s) to mask:
- Enter a number to select DELIMITER (e.g 1 - ',' or comma, 2 - '|' or pipe, 3 - '\\t' or tab).
- Enter comma-seperated numbers to select multiple columns for MOBILE and OTHERS (e.g 1 or 1,4)
- Enter 0 to skip column selection.
- Same selections will be applied for all the above listed files.
- Enter 'q' to exit.
    """)
    while 1:
        delimiterKey = input("Select a number for DELIMITER: ")
        if delimiterKey == 'q':
            print('Program exited.')
            return
        if delimiterKey not in ['1','2','3']:
            print ("Invalid, only accepts 1, 2 or 3. Please try again.")
            continue
        else:
            break

    res = 0
    skipMobile = 0
    while res != 1:
        mnoCols = input("Select column(s) to mask for MOBILE: ")
        if mnoCols == 'q':
            print('Program exited.')
            return
        elif mnoCols == '0':
            print('Skip masking for MOBILE.')
            skipMobile = 1
            break
        mnoCols = mnoCols.replace(" ","")
        res = validateMultiCols(mnoCols)
        
    res = 0
    skipOthers = 0
    while res != 1:
        otherCols = input("Select column(s) to mask for OTHERS: ")
        if otherCols == 'q':
            print('Program exited.')
            return
        elif mnoCols == '0':
            print('Skip masking for OTHERS.')
            skipOthers = 1
            break
        otherCols = otherCols.replace(" ","")
        res = validateMultiCols(otherCols)

    delimiter = delimiterObj[delimiterKey]
    mnoCols = mnoCols.split(',')
    otherCols = otherCols.split(',')

    maskedDir = 'masked'
    if not os.path.exists(maskedDir):
        os.makedirs(maskedDir)
        print("Created new 'masked' folder...")
    for file in files:
        f = open('to_mask/'+file, 'r')
        lines = f.readlines()
        count = 0
        print(f"processing {file}...")

        for line in lines:
            count += 1
            row = line.split(delimiter)
            fileName = file.split('.')[0]

            if (skipMobile != 1):
                row = mask(row,mnoCols,file,'mobile')
            if (skipOthers != 1):
                row = mask(row,otherCols,file)
            row = delimiter.join(row)

            maskedFile = open(maskedDir+'/'+fileName+'_masked.csv','a')
            maskedFile.writelines(row.strip())
            maskedFile.writelines("\n")
            maskedFile.close()

        print(f"done processing")
        f.close()   
main()








