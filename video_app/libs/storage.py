import os
from django.conf import settings
from django.core.files.storage import FileSystemStorage

class Storage(FileSystemStorage):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.location = self.get_location()
    
    @property
    def base_url(self) -> str:
        """This property appends slug to base_url for FileSystemStorages"""
        if not settings.USE_S3:
            return f'{super().base_url}{self.destination}/'
        return super().base_url

    def get_location(self):
        """This function changes the location based on usecase """
        if not settings.USE_S3:
            return os.path.join(settings.MEDIA_ROOT, self.destination)
        return self.destination

class CourseStorage(Storage):
    destination = 'course'
    file_overwrite = False
