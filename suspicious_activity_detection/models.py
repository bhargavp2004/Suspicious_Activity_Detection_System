from django.db import models

class Video(models.Model):
    video_file = models.FileField(upload_to='uploaded_videos', null=True, verbose_name="")
    output_file = models.FileField(upload_to='output_videos', null=True, verbose_name="")

    def __str__(self):
        return f"Video: {self.video_file.name}, Output: {self.output_file.name}"  # Use valid attributes

    def get_output_file_url(self):
        if self.output_file:
            return self.output_file.url
        return None
