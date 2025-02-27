import pandas as pd
import os
import pdfplumber
import re


def multiRead(directory) -> pd.DataFrame:

    all_dataFrames = []

    for file_name in os.listdir(directory):
        if file_name.endswith(".pdf"):  # Only process PDFs
            pdf_path = os.path.join(directory, file_name)
            one_month_df = singleRead(pdf_path)
            print(f'Finished Processing {file_name}')
            
            if one_month_df is not None:
                all_dataFrames.append(one_month_df)

    all_times_processed_df = pd.concat(all_dataFrames, ignore_index=True).sort_values(by="Date")
    return all_times_processed_df


def singleRead(pdf_path) -> pd.DataFrame:

    # Used to match name format in Firebase
    month_map = {
        'January': '01',
        'February': '02',
        'March': '03',
        'April': '04',
        'May': '05',
        'June': '06',
        'July': '07',
        'August': '08',
        'September': '09',
        'October': '10',
        'November': '11',
        'December': '12'
    }

    # Extract data from pdf
    with pdfplumber.open(pdf_path) as pdf:
        tables = []
        all_text = ''

        for page in pdf.pages:

            all_text += page.extract_text()

            table = page.extract_table()
            if table:
                tables.extend(table)

        match = re.search(r"\b(20\d{2})\b", all_text)  # Search the text for the year
        if match: year = match.group(1)  # Extract the matched year
        else: year = '2025'

    name_of_month = table[0][0]  # Get the name of the current month from the table as it is the name of the column in the df
    name_of_hijri_month = table[0][1]

    # Pandas DataFrame Operations
    df = pd.DataFrame(table[1:], columns=table[0])  # Convert to a DataFrame for better readability
    df.replace("", None, inplace=True)
    df.dropna(inplace=True)  # Get rid of bad rows
    df[name_of_month] = df[name_of_month].apply(lambda day: f'{year}-{month_map[name_of_month]}-{day}')  # Reconfigure column to match Firebase naming convention
    df.drop(columns=[name_of_hijri_month,'Day'],axis=1,inplace=True)  # Get rid of rows i dont need
    df.rename(columns={name_of_month : 'Date'}, inplace=True)  # To make it easier to concat multiple months
    return df

