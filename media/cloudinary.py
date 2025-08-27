import cloudinary.uploader
from cloudinary.exceptions import Error

class CloudinaryUploader:
    @staticmethod
    def upload_file(file, folder=None, tags=None, resource_type='auto'):
        try:
            upload_options = {
                'resource_type': resource_type,
                'folder': folder,
                'tags': tags or []
            }
            result = cloudinary.uploader.upload(file, **upload_options)
            return {
                'url': result.get('secure_url'),
                'public_id': result.get('public_id'),
                'resource_type': result.get('resource_type'),
            }
        except Error as e:
            return {'error': str(e)}
