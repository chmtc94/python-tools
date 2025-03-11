from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
from xlsxwriter.workbook import Workbook
import os
import pandas as pd

def ask_csv_filenames():
    """ Choose csv files to import in EXCEL """ 
    filenames = fd.askopenfilenames(
        title='Selectionner les fichiers csv à importer',
        initialdir=os.path.dirname(__file__),
        filetypes=(('csv files', '*.csv'),('All files', '*.*')) 
        )
    return filenames

def ask_workbook_path():
    """Ask for path of workbook to create"""
    _workbook_path = fd.asksaveasfilename(
        title='Saisir un nom pour le classseur',
        initialdir=os.path.dirname(__file__),
        filetypes=(('Excel .xlsx files', '*.xlsx'),('All files', '*.*')) 
        )
    return _workbook_path

def import_csv_files_to_excel (workbook_path, csv_filenames ):
    """ 
    Import all csv files into one workook created at workbook_path
    The workbook contains one sheet per each csv file
    The sheet names are the csv file basename without extension
    """
    with Workbook(workbook_path) as workbook:
        
        for filename in csv_filenames:
            try:
                # Read csvfile into dataframe df
                df = pd.read_csv(filename, encoding="utf-8", na_filter=False)

                # extract sheetname from filename
                sheetname, ext = os.path.splitext(os.path.basename(filename))

                # Add new sheet to workbook
                worksheet = workbook.add_worksheet(str.upper(sheetname))

                # Get the dimensions of the dataframe.
                (max_row, max_col) = df.shape
                
                # Create a list of column headers, to use in add_table().
                column_settings = [{'header': column} for column in df.columns]
                
                # Define options for EXCEL table creation
                options = {
                    "data": df.values,
                    "columns": column_settings,
                    }
                
                # Add the Excel table structure
                worksheet.add_table(0,0,max_row,max_col-1, options)

                # Make the columns wider for clarity.
                worksheet.autofit()
              
                # Freeze headers
                worksheet.freeze_panes(1,0)
                
                # Set zoom to 150%
                worksheet.set_zoom(150)

                print (f"OK file '{filename}' imported ")
            
            except Exception as err:
            
                print (f"ERROR! file '{filename}' NOT IMPORTED")
                print(f"Unexpected {err=}, {type(err)=}")

        # Closing the workbook with workbook.close statement is not needed
        # Closing is automatic with statement block, even in case of error

if __name__ == '__main__':
    csv_filenames = ask_csv_filenames()
    if len(csv_filenames) > 0:
        workbook_path = ask_workbook_path()
        if len(workbook_path)>0:
            print(f"Importing csv files into workbook {workbook_path}")
            import_csv_files_to_excel(workbook_path,csv_filenames)

