import os
import os.path
from io import BytesIO

import fitz  # PyMuPDF for PDF handling
import pdfrw
import usaddress
from PyPDF2.generic import NameObject, IndirectObject, BooleanObject
from django.conf import settings
from django.http import FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fillpdf import fillpdfs
from pymupdf import pymupdf
from rest_framework.decorators import api_view
from rest_framework.exceptions import ParseError

pymupdf.TOOLS.mupdf_display_errors(False)




def set_need_appearances_writer(writer):
    try:
        catalog = writer._root_object
        # get the AcroForm tree and add "/NeedAppearances attribute
        if "/AcroForm" not in catalog:
            writer._root_object.update({
                NameObject("/AcroForm"): IndirectObject(len(writer._objects), 0, writer)})

        need_appearances = NameObject("/NeedAppearances")
        writer._root_object["/AcroForm"][need_appearances] = BooleanObject(True)


    except Exception as e:
        print('set_need_appearances_writer() catch : ', repr(e))

    return writer


def encode_pdf_string(value):
    if value:
        return pdfrw.objects.pdfstring.PdfString.encode(value)
    else:
        return pdfrw.objects.pdfstring.PdfString.encode('')


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
            elif 'EIN' in line:
                data['text_id'] = line.replace('EIN', '').strip()
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

        data['open_loan'] = 'NA'
        data['state_inc'] = data['state']
        template_form = os.path.join(settings.MEDIA_ROOT, 'templates','NEW PDF.pdf')
        
        # output = str(os.path.join(os.path.dirname(filename), f'temp/{os.path.basename(filename)}'))
        
        output = str(os.path.join(settings.MEDIA_ROOT,'temp' ,os.path.basename(filename)))
        template = pdfrw.PdfReader(template_form)
        for page in template.pages:
            annotations = page['/Annots']
            if annotations is None:
                continue

            for annotation in annotations:
                if annotation['/Subtype'] == '/Widget':
                    if annotation['/Parent']:
                        key = str(annotation['/Parent']['/T']).replace('(', '')
                        key = key.replace(')', '')
                        if key in data:
                            annotation.update(
                                pdfrw.PdfDict(V=encode_pdf_string(data[key]))
                            )
                        annotation.update(pdfrw.PdfDict(Ff=1))

        template.Root.AcroForm.update(pdfrw.PdfDict(NeedAppearances=pdfrw.PdfObject('true')))
        pdfrw.PdfWriter().write(output, template)

        save_signature(filename)
        # final_file = os.path.join(os.path.dirname(filename), f'outputs/{os.path.basename(filename)}')
        final_file = os.path.join(settings.MEDIA_ROOT,'outputs', os.path.basename(filename))
        write_signature(output, final_file)
        if os.path.exists(output):
            try:
                os.remove(output)
            except:
                pass
        return final_file


def save_signature(file_name):
    doc = fitz.open(file_name)
    page = doc.load_page(len(doc) - 1)
    image_list = page.get_images()
    file_base_name = os.path.basename(file_name).split('.')[0]
    
    if image_list:
        for img in image_list:
            if img[7].startswith('X'):
                fitz.Pixmap(doc, 5)
                base_image = fitz.Pixmap(doc, img[0])
                mask = fitz.Pixmap(doc, img[1])
                pix = fitz.Pixmap(base_image, mask)
                img_name = os.path.join(settings.MEDIA_ROOT,'temp', f"{file_base_name}.png")
                
                pix.save(img_name)
                break


def write_signature(file_name, output_file):
    file_base_name = os.path.basename(file_name).split('.')[0]
    file_handle = fitz.open(file_name, filetype="pdf")
    page = file_handle[0]
    img_path = os.path.join(os.path.dirname(file_name), f"{file_base_name}.png")
    page.insert_image(
        fitz.Rect(162, 760, 275, 805),
        filename=img_path,
    )
    file_handle.save(output_file)
    if os.path.exists(img_path):
        os.remove(img_path)


def parse_pdf(OldPdfName, email_sh=1, django=0):
    return read_pdf(OldPdfName)


@csrf_exempt
@api_view(['GET', 'POST'])
def send_file(request):
    try:
        # Check if the file is in the request
        if 'file' not in request.FILES:
            raise ParseError("File not provided in the request.")

        f = request.FILES['file']
        file_name = f.name
        input_file = os.path.join(settings.MEDIA_ROOT, file_name)

        # Write the uploaded file to disk
        try:
            with open(input_file, 'wb+') as destination:
                for chunk in f.chunks():
                    destination.write(chunk)
        except IOError:
            raise IOError("Error writing file to disk.")

        # Process the PDF using parse_pdf
        try:
            output = parse_pdf(input_file, email_sh=int(1))
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")

        # Check if output was generated
        if output and os.path.exists(output):
            try:
                with open(output, 'rb') as f:
                    buff = BytesIO(f.read())
                    response = FileResponse(buff, content_type='application/pdf')
                    response['Content-Disposition'] = f'attachment; filename="{os.path.basename(output)}"'

                    return response
            except IOError:
                raise IOError("Error reading the output file.")
        else:
            return JsonResponse({"message": "Output not found or invalid."}, status=400)

    except ParseError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except IOError as e:
        return JsonResponse({"error": str(e)}, status=500)
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=500)
    except Exception as e:
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)