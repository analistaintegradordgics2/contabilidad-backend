from io import BytesIO
import os
from django.http import HttpResponse
from rest_framework.response import Response
from django.template.loader import get_template,render_to_string
from rest_framework.response import Response
from django.http import HttpResponse, Http404
from celery import shared_task
from django.http import HttpResponse, Http404
import xlsxwriter, datetime, pdb, pdfkit
from zipfile import ZipFile
import zipfile
from django.conf import settings
from os import listdir, rmdir, remove
class Render:

    @staticmethod
    @shared_task
    def export_excel(registros, name, dejar_guion_bajo = False, no_informacion = False, no_encabezado = False, por_hojas = False):
        output = BytesIO()

        workbook = xlsxwriter.Workbook(output)

        # LeidyB 14/01/2025 - Se realiza cuando se necesite generar informacion en Excel por hojas.
        if por_hojas:
            for sheet_name, data in registros.items():
                worksheet = workbook.add_worksheet(sheet_name[:31])  # Los nombres de hoja tienen un límite de 31 caracteres
                Render.procesar_hoja(data, worksheet, workbook, dejar_guion_bajo, no_informacion, no_encabezado)
        else:
            worksheet = workbook.add_worksheet()
            if no_informacion == False :
                row = 3
                col = 1
                total_columnas = 1
            else :
                row = 0 if no_encabezado == False else -1
                col = 0
                total_columnas = 0

            row, col = Render.recorrer_excel(registros,worksheet,workbook,row,col,True, dejar_guion_bajo, no_informacion)

            if no_informacion == False :
                fecha_actual = datetime.datetime.now().strftime('%d/%m/%Y %I:%M %p')
                cell_format = workbook.add_format()
                cell_format.set_font_size(20)
                worksheet.write(0, 1, name, cell_format)
                row+= 3  
                cell_format = workbook.add_format()
                cell_format.set_font_size(10)
                worksheet.write(row, 1, f'Elaborado por DGI S.A.S - {fecha_actual}', cell_format)

        workbook.close()
        output.seek(0) 

        filename = '{}.xlsx'.format(name)
        # pdb.set_trace()
        response = HttpResponse(output,content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' )
        response['Content-Disposition'] = 'attachment; filename=%s' % filename
        return response

    def recorrer_excel(registros,worksheet,workbook,row,col,estado, dejar_guion_bajo = False, no_informacion = False):
        idtitulo = row
        totalReg = len(registros)
        countReg = 0

        for registro in registros:
            countReg += 1
            if row == (3 if no_informacion == False else 0) :
                col = (1 if no_informacion == False else 0)
                for columna  in registro:
                    total_columnas = len(registro)
                    
                    cell_format = workbook.add_format()
                    cell_format.set_bold()      # Turns bold on.
                    cell_format.set_bold(True) 
                    cell_format.set_align('center')
                    if dejar_guion_bajo == False :
                        titulo = columna.replace('_',' ')
                    else :
                        titulo = columna
                    worksheet.write(row, col, titulo,cell_format)   
                    col += 1 
                row += 1

            if row==idtitulo and estado:
                col = 1
                
                for columna  in registro:
                    total_columnas = len(registro)
                    cell_format = workbook.add_format()
                    cell_format.set_bold()      # Turns bold on.
                    cell_format.set_bg_color('#BFBFBF')
                    cell_format.set_border(1)
                    cell_format.set_bold(True) 
                    cell_format.set_align('center')
                    titulo = columna.replace('_',' ')
                    worksheet.set_column(row, col, len(titulo.strip()) * 2)
                    worksheet.write(row, col, titulo,cell_format)   
                    col += 1 

                row += 1            
            col = (1 if no_informacion == False else 0)

            for columna  in registro.values():
                # pdb.set_trace()
                if isinstance(columna, list):                 
                    row, col = Render.recorrer_excel(columna,worksheet,workbook,row+1,col,True)
                else:
                    if columna == None: 
                        columna = ''
                    
                    if  isinstance(columna, str) or isinstance(columna, datetime.datetime) or isinstance(columna, datetime.date): 
                    
                        valor = '{}'.format(columna)
                        worksheet.write(row, col, valor)   


                        #.##0
                    elif isinstance(columna, int):
                        valor = '{}'.format(columna)
                        currency_format = workbook.add_format({'num_format': '0'})                    
                        worksheet.write(row, col, columna, currency_format )   
                    else:    
                        try:
                            currency_format = workbook.add_format({'num_format': '$#,##0.00'})

                            #para colorear la columna de totales
                            # if totalReg == countReg:
                            #     currency_format.set_bg_color('#BFBFBF')
                            #     currency_format.set_border(2)

                            worksheet.write(row,col, columna, currency_format)
                        except:
                            error = ''
                            # pdb.set_trace()
                            # row, col = Render.recorrer_excel(columna,worksheet,workbook,row+1,col,True)

 
                col += 1 
            
            row += 1
        return row,col

    def procesar_hoja(registros, worksheet, workbook, dejar_guion_bajo, no_informacion, no_encabezado):
        """
        Procesa los datos de una hoja específica.
        """
        # Configurar inicio de filas y columnas
        row = 3 if not no_informacion else 0 if not no_encabezado else -1
        col = 1 if not no_informacion else 0

        # Escribir datos en la hoja
        row, col = Render.recorrer_excel(registros, worksheet, workbook, row, col, True, dejar_guion_bajo, no_informacion)

        # Encabezado y pie de página
        if not no_informacion:
            Render.agregar_encabezado(worksheet, workbook)
            Render.agregar_pie(worksheet, workbook, row)
    
    @staticmethod
    def agregar_encabezado(worksheet, workbook):
        """
        Agrega el encabezado con el nombre del documento.
        """
        cell_format = workbook.add_format({'font_size': 20})
        worksheet.write(0, 1, 'Reporte', cell_format)

    @staticmethod
    def agregar_pie(worksheet, workbook, row):
        """
        Agrega un pie de página con información adicional.
        """
        cell_format = workbook.add_format({'font_size': 10})
        worksheet.write(row + 3, 1, 'Elaborado por DGI S.A.S', cell_format)

    
    @staticmethod
    @shared_task
    def downloadZip(folder, files=[], nameZip="zip.zip", archivoAcomprimir='.pdf'):
        path = folder + nameZip 
        fantasy_zip = zipfile.ZipFile(path, 'w')
        for file in files:
            if file.endswith(archivoAcomprimir):
                fantasy_zip.write(
                    os.path.join(folder, file), os.path.relpath(os.path.join(folder, file), folder),
                    compress_type=zipfile.ZIP_DEFLATED
                )
        fantasy_zip.close()
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type='application/force-download')
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
                return response
        raise Http404
    
    @staticmethod
    @shared_task
    def render_pdfkit(path: str, params: dict, name=None, options={}) :
        """
            options = {
                'page-size': 'A4',
                'encoding': 'UTF-8',
                'print-media-type': ''
                'orientation' : 'Landscape'
            }
        """
        template = get_template(path)
        html = template.render(params)
        css = str(os.path.join(settings.DIR_CSS, "main.css"))

        try:
            pdf = pdfkit.from_string(html, False, options=options, css=[css])
            response = HttpResponse(pdf, content_type='application/pdf')
            if name != None : 
                response['Content-Disposition'] = 'attachment; filename="{}.pdf"'.format(name)
            return response
        except Exception as e:
            return HttpResponse("Error al generar el PDF: {}".format(str(e)), status=400)