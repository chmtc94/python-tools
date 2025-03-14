from tkinter import filedialog as fd

def select_python_file():
    # Choose python file 
    filename = fd.askopenfilename(
        title='Selectionner un fichier python',
        filetypes=(('Python files', '*.py'),('All files', '*.*')), 
        )
    return filename

def execute_python_file(filename:str):
    try:
        with open(filename, mode="r") as python_file:
            file = python_file.read()
            exec(file)
    except Exception as err:           
        print(f"Erreur exécution script python: {filename} \nErrType: {type(err)}\n{str(err)}")

if __name__ == '__main__':
    filename = select_python_file()
    if len(filename) > 0: execute_python_file(filename)
