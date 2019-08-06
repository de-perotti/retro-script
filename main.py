import sys
import glob
import pdf_parser
from datetime import datetime

TODAY = datetime.isoformat(datetime.now())
CSV_NAME = f'results/{TODAY}-result.csv'

if __name__ == '__main__':
    file_names = glob.glob('pdfs/*.pdf')

    with open(CSV_NAME, 'w') as csv_file:
        for f in file_names:
            with open(f, 'rb') as pdf:
                print(f)
                csv_file.write(pdf_parser.toCSVContent(pdf))
