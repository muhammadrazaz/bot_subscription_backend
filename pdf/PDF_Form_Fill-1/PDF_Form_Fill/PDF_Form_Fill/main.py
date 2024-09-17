import os
import fitz  # PyMuPDF for PDF handling
import usaddress
from fillpdf import fillpdfs
from pymupdf import pymupdf

pymupdf.TOOLS.mupdf_display_errors(False)
# print(fillpdfs.print_form_fields('template/pdf_fillable.pdf'))


def read_pdf(filename):
    import pdfplumber
    with pdfplumber.open(filename) as pdf:
        first_page = pdf.pages[0]
        lines = first_page.extract_text().split("\n")
        data = {}
        days_list = [
            "Monday",
            "Sunday",
            "Saturday",
            "Friday",
            "Thursday",
            "Wednesday",
            "Tuesday"
        ]

        for line in lines:
            if 'Business Legal Name' in line:
                result = line.replace('Business Legal Name', '').strip()
                data['legal_business'] = result
            elif 'Business DBA Name' in line:
                result = line.replace('Business DBA Name', '').strip()
                data['dba'] = result
            elif any(day in line for day in days_list):
                result = line
                data['date'] = result
            elif 'Avg. Monthly Revenue' in line:
                result = line.replace('Avg. Monthly Revenue', '').strip()
                data['monthly_revenue'] = result

            elif 'Legal Entity' in line:
                data['textarea_30knmr'] = lines[lines.index(line) + 1]
            elif 'Business Start Date' in line:
                result = line.replace('Business Start Date', '').strip()
                data['business_start'] = result
            elif 'Business start date' in line and 'business_start' not in data:
                data['business_start'] = line.replace('Business start date', '').strip()
            elif 'Industry Type' in line:
                result = line.replace('Industry Type', '').strip()
                data['business_type'] = result
            # elif 'More than 1 Owner?' in line:
            #     data['more_owner'] = lines[lines.index(line)+1]
            elif 'Business Address' in line:
                result = line.replace('Business Address', '').strip()
                data['business_address'] = result
                for address in usaddress.parse(result + ' ' + lines[lines.index(line) + 1]):
                    if address[1] == 'PlaceName':
                        data['city'] = address[0].strip(',')
                    elif address[1] == 'StateName':
                        data['state'] = address[0].strip(',')
                    elif address[1] == 'ZipCode':
                        data['zip'] = address[0].strip(',')
            elif 'Business street address' in line and 'business_address' not in data:
                data['business_address'] = line.replace('Business street address', '').strip()
            elif 'Business City' in line and 'city' not in data:
                data['city'] = line.replace('Business City', '').strip()

            elif 'Business State' in line and 'state' not in data:
                data['state'] = line.replace('Business State', '').strip()

            elif 'Business zip code' in line and 'zip' not in data:
                data['zip'] = line.replace('Business zip code', '').strip()
            elif 'First Name' in line and 'first_name' not in data:
                result = line.replace('First Name', '').strip()
                data['first_name'] = result
            elif 'FULL NAME' in line and 'first_name' not in data:
                result = line.replace('FULL NAME', '').strip()
                data['first_name'] = result.split(' ')[0]
                data['last_name'] = result.split(' ')[1]
            elif 'Last Name' in line and 'last_name' not in data:
                result = line.replace('Last Name', '').strip()
                data['last_name'] = result
            elif 'SSN' in line and 'social_security' not in data:
                result = line.replace('SSN', '').strip()
                data['social_security'] = result
            elif 'Ownership Percentage' in line and 'percent_ownership' not in data:
                result = line.replace('Ownership Percentage', '').strip()
                data['percent_ownership'] = result
            elif 'Date of Birth' in line and 'dob' not in data:
                result = line.replace('Date of Birth', '').strip()
                data['dob'] = result
            elif 'DOB' in line and 'dob' not in data:
                result = line.replace('DOB', '').strip()
                data['dob'] = result
            elif 'Home Address' in line and 'home_address' not in data:
                result = line.replace('Home Address', '').strip()
                data['home_address'] = result
                for address in usaddress.parse(result + ' ' + lines[lines.index(line) + 1]):
                    if address[1] == 'PlaceName':
                        data['home_city'] = address[0].strip(',')
                    elif address[1] == 'StateName':
                        data['home_state'] = address[0].strip(',')
                    elif address[1] == 'ZipCode':
                        data['home_zip'] = address[0].strip(',')
            elif 'Home city' in line and 'home_city' not in data:
                data['home_city'] = line.replace('Home city', '').strip()

            elif 'Homes State' in line and 'home_state' not in data:
                data['home_state'] = line.replace('Homes State', '').strip()

            elif 'Home Zip Code' in line and 'home_zip' not in data:
                data['home_zip'] = line.replace('Home Zip Code', '').strip()

        template_form = os.path.join(os.getcwd(), 'template/pdf_fillable.pdf')
        output = os.path.join(os.getcwd(), 'new.pdf')
        fillpdfs.write_fillable_pdf(template_form, output, data_dict=data, flatten=True)
        fillpdfs.flatten_pdf(output, output)


def save_signature(file_name):
    doc = fitz.open(file_name)
    page = doc.load_page(len(doc) - 1)
    image_list = page.get_images()
    if image_list:
        for img in image_list:
            if img[7].startswith('X'):
                fitz.Pixmap(doc, 5)
                base_image = fitz.Pixmap(doc, img[0])
                mask = fitz.Pixmap(doc, img[1])
                pix = fitz.Pixmap(base_image, mask)
                img_name = f"sign.png"
                pix.save(img_name)
                break

def write_signature(file_name, output_file):
    output_folder = os.path.join(os.getcwd(), "outputs")
    save_file_path = os.path.join(output_folder, output_file)

    OutputFile = save_file_path
    file_handle = fitz.open(file_name, filetype="pdf")
    page = file_handle[0]
    img_path = os.path.join(os.getcwd(), "sign.png")
    page.insert_image(
        fitz.Rect(162, 760, 275, 805),
        filename=img_path,
    )
    file_handle.save(OutputFile, deflate=True)
    if os.path.exists(img_path):
        os.remove(img_path)
    if os.path.exists('out.pdf'):
        try:
            os.remove('out.pdf')
        except:
            pass


if __name__ == '__main__':
    for file in os.listdir(os.path.join(os.getcwd(), 'inputs')):
        folder = os.path.join(os.getcwd(), 'inputs')
        file_path = os.path.join(folder, file)
        read_pdf(file_path)
        save_signature(file_path)
        write_signature('new.pdf', file)
    print('Done')
