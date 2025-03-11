import os
import json
from tkinter import filedialog as fd

'''
io documentation
https://docs.python.org/fr/3.13/library/io.html#io.open

f = open("myfile.txt", "r", encoding="utf-8")

def read_text(path, encoding=None):
    encoding = io.text_encoding(encoding)  # stacklevel=2
    with open(path, encoding) as f:
        return f.read()
'''

# Keys to hide in json strings (for example in http responses)
# Comment unwanted lines od add new secret keys in below secrets keys list
SECRET_JSON_KEYS = {
    "Authorization",
    "access_token",
    "basic_token",
    "refresh_token",
    "client_id",
    "client_secret",
    "customer_id",
    "vehicle_id",
    "vin",
    "coordinates",
}

# Keys to hide everywhere in file (for example in http request)
# NB : Keys need to appear at least once in a json string (for example in a http response)
# Comment unwanted lines od add new secret keys in below secrets keys list
SECRET_EVERYWHERE_KEYS = { 
    "client_id",
    "vehicle_id",
    "vin",
}

def ask_filenames( file_types = ('log files', '*.log') ):
    ''' Choose files to process '''

    filenames = fd.askopenfilenames (
        title = 'Select files to process',
        initialdir = os.path.dirname(__file__),
        filetypes = (file_types,('All files', '*.*'))
    )
    return filenames

def anonymized_string(string : str, anonym_char = "*"):
    anonym_string = ""
    for c in string:
        if c in ('{','}','[',']',',','-',' '):
            anonym_string += c
        else:
            anonym_string += anonym_char
    return anonym_string

def hide_secrets(json_object:object, key = ""):
    
    try:

        if isinstance(json_object, dict):
            d = dict(json_object)
            for key in d:
                json_value = json_object[key]
                json_object[key] = hide_secrets(json_value, key)
        
        elif isinstance(json_object, list):
            l = list(json_object)
            for i in range(len(l)):
                json_value = json_object[i]
                json_object[i] = hide_secrets(json_value, key)
        
        else:
            s = str(json_object)
            if key in SECRET_JSON_KEYS:
                json_object = anonymized_string(s)
                if key in SECRET_EVERYWHERE_KEYS:
                    Anonymized_values[s]=json_object # memorisation for http requests back processing
            else:
                json_object = s
        
        return json_object
                    
    except Exception as e:
        print (f"ERROR hiding secrets with json_object : '{str(json_object)}' , key : '{key}' \n", str(e))
        return ("<ERROR>")
    
def remove_secrets(filename:str):
    """ Remove secrets from text file """
    with open(filename, 'r', encoding="utf-8") as input_file:
        root, ext = os.path.splitext(filename)
        output_filename = root + "_anonymized" + ext
        with open(output_filename, 'w', encoding="utf-8") as output_file:
            
            line_number=0
            for line in input_file:
                line_number += 1
                print(f"\rProcessing line {line_number}", end="")
                start_index = line.find("{")
                if (start_index == -1): # No json data in line
                    output_file.write(line)
                else: # json data detected 
                    end_index = line.rindex("}")  # end index in line
                    json_string = line[start_index : end_index+1] # extract json string from line
                    if json_string.find("UUID('") > -1 :  
                        output_file.write(line) # do not process lines with UUIDs that make json.loads() fail (TO_DO_LATER)
                    else:
                        # replace /' True et False to prevent json.loads() failing
                        json_string = json_string.replace("'","\"").replace("True","true").replace("False","false") 
                        json_object = json.loads(json_string) # decode json string into object
                        json_object = hide_secrets(json_object) # hide secrets infos in json object
                        json_string = json.dumps(json_object) # json object with hiden secrets back to json string 
                        anonymized_line = line[0:start_index] + json_string + line[end_index+1:] # line with secrets hidden
                        output_file.write(anonymized_line) # write line to output file

    # Back process entire output file to hide remaining secrets values not in json strings (ex: http requests or VIN jpg file)
    with open(output_filename, 'r', encoding="utf-8") as output_file:            
        content = output_file.read()
        for keyvalue in Anonymized_values:
            content = content.replace(keyvalue, Anonymized_values[keyvalue])
    
    with open(output_filename, 'w', encoding="utf-8") as output_file:
            output_file.write(content) 
    print("\n", end="\n")

if __name__ =='__main__':
    filenames = ask_filenames()
    if len(filenames) > 0:
        Anonymized_values=dict()
        for filename in filenames:
            try:
                print("Removing secrets from file", filename)
                remove_secrets(filename)

            except Exception as e:
                print ("Error processing file ", filename, end="\n")

        print("All files processed")