from django.db import models

class BannerImage(models.Model):
    image = models.ImageField(upload_to='banners/', help_text='Upload a new banner image')

    def save(self, *args, **kwargs):
        # Delete existing BannerImage objects
        BannerImage.objects.all().delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return  "Banner Image"

class RushFormLink(models.Model):
    link = models.URLField(max_length=200, help_text='URL for the Rush Interest Form')

    def save(self, *args, **kwargs):
        RushFormLink.objects.all().delete()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.link

class RushSlide(models.Model):
    image = models.ImageField(upload_to='rush_slides/', help_text='Upload a slide image')
    caption = models.CharField(max_length=200, help_text='Caption for the slide')
    order = models.IntegerField(default=0, db_index=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.caption