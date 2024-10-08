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
from rest_framework.exceptions import ParseError
from io import BytesIO
from .main import parse_pdf
from django.conf import settings
from datetime import datetime
from auth_app.permissions import IsInGroupsOrSuperUser
pymupdf.TOOLS.mupdf_display_errors(False)
# print(fillpdfs.print_form_fields('template/pdf_fillable.pdf'))

# class IsPDFOrSuperUser(BasePermission):
   

#     def has_permission(self, request, view):
#         # Check if the user is authenticated
#         if not request.user or not request.user.is_authenticated:
#             return False
#         group = request.user.groups.first() 
#         if (group and group.name == "pdf") or request.user.is_superuser:
#             return True
#         else:
#             return False
        
# class IsSuperUser(BasePermission):
   

#     def has_permission(self, request, view):
#         # Check if the user is authenticated
#         if not request.user or not request.user.is_authenticated:
#             return False
#         group = request.user.groups.first() 
#         if request.user.is_superuser:
#             return True
#         else:
#             return False



    # output_folder = os.path.join(os.getcwd(), "outputs")
    # save_file_path = os.path.join(output_folder, output_file)

    # OutputFile = save_file_path
    # file_handle = fitz.open(file_name, filetype="pdf")
    # page = file_handle[0]
    # img_path = os.path.join(os.getcwd(), "sign.png")
    # page.insert_image(
    #     fitz.Rect(162, 760, 275, 805),
    #     filename=img_path,
    # )
    # file_handle.save(OutputFile, deflate=True)
    # if os.path.exists(img_path):
    #     os.remove(img_path)
    # if os.path.exists('out.pdf'):
    #     try:
    #         os.remove('out.pdf')
    #     except:
    #         pass


def delete_all_files_in_directory(directory_path):
    # Check if the directory exists
    dir_path = os.path.join(settings.MEDIA_ROOT, directory_path)
    if os.path.exists(dir_path):
        # Iterate over all files in the directory
        for file_name in os.listdir(dir_path):
            file_path = os.path.join(dir_path, file_name)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)  # Delete the file
            except Exception as e:
                print(f"Error while deleting file {file_path}: {e}")
    else:
        print(f"Directory {dir_path} does not exist.")


def make_zip_from_inputs(zip_file_name, inputs_dir, pdf_files_dir):
   
    # if not os.path.exists(inputs_dir):
    #     raise FileNotFoundError(f"Input directory '{inputs_dir}' does not exist.")
    
    pdf_dir = os.path.join(settings.MEDIA_ROOT, pdf_files_dir)
    in_dir = os.path.join(settings.MEDIA_ROOT, inputs_dir)
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    

    zip_file_path = os.path.join(pdf_dir, zip_file_name)
    
   
    with zipfile.ZipFile(zip_file_path, 'w') as zf:
      
        for dirname, _, files in os.walk(in_dir):
            for filename in files:
                file_path = os.path.join(dirname, filename)
                
                zf.write(file_path, os.path.relpath(file_path, in_dir))
    
    return zip_file_path

class PDFAPIView(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =['pdf'])]
    def get(self, request):
        dates = self.request.GET.getlist('dates[]')
        filter_conditions = { }
        if dates:
            start_date  = datetime.strptime(dates[0], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            end_date = datetime.strptime(dates[1], "%Y-%m-%dT%H:%M:%S.%fZ").date()
            filter_conditions = {
            'date_time__gt': start_date,
            'date_time__lt': end_date,
            }
        if self.request.user.is_superuser:
            user_id = request.query_params.get('user_id')
            if user_id:
                filter_conditions['user'] = user_id

        else:
            user_id = request.user
            filter_conditions['user'] = user_id
        data = PDFFiles.objects.filter(**filter_conditions).order_by('-date_time')

        serializer = PDFSerializer(data, many=True)
        
        # Return the serialized data in the response
        return Response({'rows': serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request, *args, **kwargs):
        serializer = PDFUploadSerializer(data=request.data)
        if serializer.is_valid():
            files = serializer.validated_data['files']
            input = os.path.join(settings.MEDIA_ROOT,'inputs')
            output = os.path.join(settings.MEDIA_ROOT,'outputs')
            temp = os.path.join(settings.MEDIA_ROOT,'temp')
            output_with_contacts = os.path.join(settings.MEDIA_ROOT,'outputs','with_contacts')
            output_without_contacts = os.path.join(settings.MEDIA_ROOT,'outputs','without_contacts')
            if not os.path.exists(input):
                os.makedirs(input)
            if not os.path.exists(output):
                os.makedirs(output)
            if not os.path.exists(output_with_contacts):
                os.makedirs(output)
            if not os.path.exists(output_without_contacts):
                os.makedirs(output)
            if not os.path.exists(temp):
                os.makedirs(temp)
            try:
            
                for f in files:
                    file_name = f.name
                    input_file = os.path.join(settings.MEDIA_ROOT,'inputs', file_name)

                    # Write the uploaded file to disk
                    try:
                        with open(input_file, 'wb+') as destination:
                            for chunk in f.chunks():
                                destination.write(chunk)
                    except IOError:
                        raise IOError("Error writing file to disk.")

                    # Process the PDF using parse_pdf
                    try:
                        output = parse_pdf(input_file)
                    except Exception as e:
                        raise ValueError(f"Error parsing PDF: {str(e)}")
                    

                input_name = ''.join(files[0].name.split('.')[:-1])+'_input.zip'
                output_without_contacts_name = ''.join(files[0].name.split('.')[:-1])+'_output.zip'
                output_with_contacts_name = ''.join(files[0].name.split('.')[:-1])+'_with_contacts_output.zip'
                make_zip_from_inputs(input_name, 'inputs', 'pdf_files')
                make_zip_from_inputs(output_without_contacts_name, 'outputs/without_contacts', 'pdf_files')
                make_zip_from_inputs(output_with_contacts_name, 'outputs/with_contacts', 'pdf_files')
                
                
                delete_all_files_in_directory('inputs')
                delete_all_files_in_directory('outputs/with_contacts')
                delete_all_files_in_directory('outputs/without_contacts')

                pdf = PDFFiles.objects.create(input=input_name,output = output_without_contacts_name,output_with_contacts = output_with_contacts_name,user=request.user)
                return Response({"rows": [{'id':pdf.pk,'input':pdf.input,'output':pdf.output,'output_with_contacts':pdf.output_with_contacts,'datetime':pdf.date_time.strftime('%d-%m-%Y %I:%M %p')}]}, status=status.HTTP_201_CREATED)

                # # Check if output was generated
                # if output and os.path.exists(output):
                #     try:
                #         with open(output, 'rb') as f:
                #             buff = BytesIO(f.read())
                #             response = FileResponse(buff, content_type='application/pdf')
                #             response['Content-Disposition'] = f'attachment; filename="{os.path.basename(output)}"'

                #             return response
                #     except IOError:
                #         raise IOError("Error reading the output file.")
                # else:
                #     return Response({"message": "Output not found or invalid."}, status=400)

            except ParseError as e:
                return Response({"error": str(e)}, status=400)
            except IOError as e:
                return Response({"error": str(e)}, status=500)
            except ValueError as e:
                return Response({"error": str(e)}, status=500)
            except Exception as e:
                return Response({"error": "An unexpected error occurred."}, status=500)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # serializer = PDFUploadSerializer(data=request.data)
        # if serializer.is_valid():
        #     files = serializer.validated_data['files']
            

        #     upload_dir = os.path.join(os.getcwd(), 'inputs')
        #     if not os.path.exists(upload_dir):
        #         os.makedirs(upload_dir)
        #     output_dir = os.path.join(os.getcwd(), 'outputs')
        #     if not os.path.exists(output_dir):
        #         os.makedirs(output_dir)


        #     for file in files:
        #          file_path = os.path.join(upload_dir, file.name)  
        #          with open(file_path, 'wb+') as destination:
        #             for chunk in file.chunks():
        #                 destination.write(chunk)

        #     for file in os.listdir(os.path.join(os.getcwd(), 'inputs')):
        #         folder = os.path.join(os.getcwd(), 'inputs')
        #         file_path = os.path.join(folder, file)
        #         read_pdf(file_path)
        #         save_signature(file_path)
        #         write_signature('new.pdf', file)


        #     input_name = ''.join(files[0].name.split('.')[:-1])+'_input.zip'
        #     output_name = ''.join(files[0].name.split('.')[:-1])+'_output.zip'
        #     make_zip_from_inputs(input_name, 'inputs', 'pdf_files')
        #     make_zip_from_inputs(output_name, 'outputs', 'pdf_files')
            
            
        #     delete_all_files_in_directory(upload_dir)
        #     delete_all_files_in_directory(output_dir)

        #     pdf = PDFFiles.objects.create(input=input_name,output = output_name,user=request.user)

        #     return Response({"rows": [{'id':pdf.pk,'input':pdf.input,'output':pdf.output,'datetime':pdf.date_time.strftime('%d-%m-%Y %I:%M %p')}]}, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class DownloadZipView(APIView):
    def get(self, request, *args, **kwargs):
        # Get the filename from query parameters
        filename = request.query_params.get('filename')
        
        if not filename:
            return Response({'error': 'Filename parameter is required.'}, status=400)
        
        # Construct the full file path
        file_path = os.path.join(settings.MEDIA_ROOT, 'pdf_files',filename)
        
        # Check if the file exists
        if not os.path.exists(file_path):
            raise Http404("File not found.")
        
        # Serve the file
        response = FileResponse(open(file_path, 'rb'), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response





class PDFUser(APIView):
    permission_classes = [IsAuthenticated,IsInGroupsOrSuperUser(allowed_groups =["VA"])]
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
        ).values("id", "web_username", "total_pdf","web_password",'first_name','last_name',"email")

        
        
        
        serializer = PDFUserDetailSerializer(users,many=True)
        

        return Response(serializer.data)

