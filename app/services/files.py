from typing import Tuple, Optional
from fastapi import UploadFile, HTTPException
from app.utils.storage import storage_manager, FileValidator

class FileService:
    
    @staticmethod
    async def upload_photo(
        file: UploadFile,
    ) -> Tuple[bool, str, Optional[str]]:
        
        try:
            file_content = await file.read()
            is_valid, error_message = FileValidator.validate_image(file_content, file.content_type)
            
            if not is_valid:
                return False, error_message, None
            
            success, url_or_error = storage_manager.upload_file(
                file_content, 
                file.filename, 
                file.content_type
            )
            
            if not success:
                return False, url_or_error, None
            
            return True, "Archivo subido exitosamente", url_or_error
            
        except Exception as e:
            return False, f"Error subiendo archivo: {str(e)}", None

    
    @staticmethod
    async def upload_brand_images(
        photo: Optional[UploadFile] = None,
    ) -> Tuple[bool, str, dict]:
        
        try:
            urls = {}
            
            success, message, url = await FileService.upload_photo(
                photo
            )
            if success:
                urls["brand_photo_url"] = url
            else:
                return False, f"Error subiendo archivo: {message}", {}
            
            if not urls:
                return False, "No se subieron archivos", {}
            
            return True, "Archivos subidos exitosamente", urls
            
        except Exception as e:
            return False, f"Error subiendo documentos: {str(e)}", {} 
    

    @staticmethod
    async def upload_vehicle_images(
        files: Optional[list] = None,
    ) -> Tuple[bool, str, list]:

        try:
            urls = []
            for idx, photo in enumerate(files):
                success, message, url = await FileService.upload_photo(
                    photo,
                )
                if success:
                    urls.append(url)
                else:
                    return False, f"Error subiendo archivo: {message}", {}

            return True, "Archivos subidos exitosamente", urls

        except Exception as e:
            return False, f"Error subiendo documentos: {str(e)}", {} 


    @staticmethod
    def validate_file_upload(file: UploadFile) -> Tuple[bool, str]:

        try:
            if not file.filename:
                return False, "Nombre de archivo requerido"

            if file.size and file.size > 5 * 1024 * 1024:
                return False, "Archivo demasiado grande (máximo 5MB)"

            allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
            file_extension = file.filename.lower().split('.')[-1]

            if f'.{file_extension}' not in allowed_extensions:
                return False, f"Tipo de archivo no permitido. Extensiones permitidas: {', '.join(allowed_extensions)}"

            return True, "Archivo válido"
            
        except Exception as e:
            return False, f"Error validando archivo: {str(e)}"
