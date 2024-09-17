from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import PDFUploadSerializer,PDFSerializer,PDFUserDetailSerializer
from  .models import PDFFiles
from rest_framework import status
from django.db.models import Count,Subquery,OuterRef,F,Value
from django.db.models.functions import Coalesce
from django.contrib.auth.models import User

import os
import fitz  # PyMuPDF for PDF handling
import usaddress
from fillpdf import fillpdfs
from pymupdf import pymupdf
import zipfile
from django.http import HttpResponse
import io
from django.http import FileResponse,Http404
from rest_framework.permissions import BasePermission
from  rest_framework.permissions import IsAuthenticated

pymupdf.TOOLS.mupdf_display_errors(False)
# print(fillpdfs.print_form_fields('template/pdf_fillable.pdf'))

class IsPDFOrSuperUser(BasePermission):
   

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        group = request.user.groups.first() 
        if (group and group.name == "pdf") or request.user.is_superuser:
            return True
        else:
            return False
        
class IsSuperUser(BasePermission):
   

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False
        group = request.user.groups.first() 
        if request.user.is_superuser:
            return True
        else:
            return False


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


def delete_all_files_in_directory(directory_path):
    # Check if the directory exists
    if os.path.exists(directory_path):
        # Iterate over all files in the directory
        for file_name in os.listdir(directory_path):
            file_path = os.path.join(directory_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete the file
            except Exception as e:
                print(f"Error while deleting file {file_path}: {e}")
    else:
        print(f"Directory {directory_path} does not exist.")


def make_zip_from_inputs(zip_file_name, inputs_dir, pdf_files_dir):
   
    if not os.path.exists(inputs_dir):
        raise FileNotFoundError(f"Input directory '{inputs_dir}' does not exist.")
    
  
    if not os.path.exists(pdf_files_dir):
        os.makedirs(pdf_files_dir)
    

    zip_file_path = os.path.join(pdf_files_dir, zip_file_name)
    
   
    with zipfile.ZipFile(zip_file_path, 'w') as zf:
      
        for dirname, _, files in os.walk(inputs_dir):
            for filename in files:
                file_path = os.path.join(dirname, filename)
                
                zf.write(file_path, os.path.relpath(file_path, inputs_dir))
    
    return zip_file_path

class PDFAPIView(APIView):
    permission_classes = [IsAuthenticated,IsPDFOrSuperUser]
    def get(self, request):
        filter_condition = {
            
        }
        if self.request.user.is_superuser:
            user_id = request.query_params.get('user_id')
            if user_id:
                filter_condition['user'] = user_id

        else:
            user_id = request.user
            filter_condition['user'] = user_id
        data = PDFFiles.objects.filter(**filter_condition)

        serializer = PDFSerializer(data, many=True)
        
        # Return the serialized data in the response
        return Response({'rows': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = PDFUploadSerializer(data=request.data)
        if serializer.is_valid():
            files = serializer.validated_data['files']
            

            upload_dir = os.path.join(os.getcwd(), 'inputs')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            output_dir = os.path.join(os.getcwd(), 'outputs')
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)


            for file in files:
                 file_path = os.path.join(upload_dir, file.name)  
                 with open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)

            for file in os.listdir(os.path.join(os.getcwd(), 'inputs')):
                folder = os.path.join(os.getcwd(), 'inputs')
                file_path = os.path.join(folder, file)
                read_pdf(file_path)
                save_signature(file_path)
                write_signature('new.pdf', file)


            input_name = ''.join(files[0].name.split('.')[:-1])+'_input.zip'
            output_name = ''.join(files[0].name.split('.')[:-1])+'_output.zip'
            make_zip_from_inputs(input_name, 'inputs', 'pdf_files')
            make_zip_from_inputs(output_name, 'outputs', 'pdf_files')
            
            
            delete_all_files_in_directory(upload_dir)
            delete_all_files_in_directory(output_dir)

            pdf = PDFFiles.objects.create(input=input_name,output = output_name,user=request.user)

            return Response({"rows": [{'id':pdf.pk,'input':pdf.input,'output':pdf.output,'datetime':pdf.date_time.strftime('%d-%m-%Y %I:%M %p')}]}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DownloadZipView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the filename from query parameters
        filename = request.query_params.get('filename')
        
        if not filename:
            return Response({'error': 'Filename parameter is required.'}, status=400)
        
        # Construct the full file path
        file_path = os.path.join('pdf_files', filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise Http404("File not found.")
        
        # Serve the file
        response = FileResponse(open(file_path, 'rb'), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response





class PDFUser(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    def get(self, request):
        
        users = User.objects.filter(groups__name = 'pdf').annotate(
    
    total_pdf=Coalesce(Subquery(
        PDFFiles.objects.filter(user=OuterRef('id')).values('user_id').annotate(
            total_sum=Count('user_id')
        ).values('total_sum')[:1]
        ),Value(0)),
        ).annotate(
        user_id=F('id'),
        web_username=F('username'),
        web_password = F('password')
        ).values("id", "web_username", "total_pdf","web_password")

        
        
        
        serializer = PDFUserDetailSerializer(users,many=True)
        

        return Response(serializer.data)

