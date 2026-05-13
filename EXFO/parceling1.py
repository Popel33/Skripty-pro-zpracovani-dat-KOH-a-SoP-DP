import os
from bs4 import BeautifulSoup
import pandas as pd

def extract_tables_from_html(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    tables = soup.find_all("table")
    all_dataframes = []

    for idx, table in enumerate(tables):
        rows = []
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            rows.append([cell.get_text(strip=True) for cell in cells])
        if rows:
            df = pd.DataFrame(rows)
            all_dataframes.append(df)

    return all_dataframes

def save_tables_to_xlsx(tables, output_path):
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for i, table in enumerate(tables):
            table.to_excel(writer, index=False, header=False, sheet_name=f"Table_{i+1}")

def process_all_html_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    for filename in os.listdir(input_folder):
        if filename.endswith(".html"):
            file_path = os.path.join(input_folder, filename)
            tables = extract_tables_from_html(file_path)

            base_name = os.path.splitext(filename)[0]
            save_tables_to_xlsx(tables, os.path.join(output_folder, f"{base_name}.xlsx"))
            
input_dir = "vstupni_data"
output_dir = "vystupni_data"

process_all_html_files(input_dir, output_dir)
