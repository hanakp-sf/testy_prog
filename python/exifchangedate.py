#!/usr/bin/env python3
"""
Change EXIF date/time of images by a given delta, developed to fix Zuzana's 50th birthday photos.
delta is added to DateTimeOriginal and DateTimeDigitized fields.
delta =  23 years, 7 months, 8 days, 8 hours, 30 minutes

Usage:
  python exifchangedate.py

Requires:  Pillow  piexif
"""

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS, IFD
import datetime
import piexif
import os

# Set the date time in different EXIF fields
# 36867 = DateTimeOriginal
# 36868 = DateTimeDigitized
# 306 = DateTime
# exif_dict['Exif'][36867] = datetime_str.encode('utf-8')
# exif_dict['Exif'][36868] = datetime_str.encode('utf-8')
# exif_dict['0th'][306] = datetime_str.encode('utf-8')
def set_image_datetime(image_path, image_file, delta):
    try:
        fname = image_path + image_file
        print(f"Processing {fname}", end = ' ')
        data = None
        # Load existing EXIF data
        exif_dict = piexif.load(fname)
        #print(exif_dict)  # Debugging line to see the entire EXIF data structure
        dateOriginal = exif_dict['Exif'].get(36867, b'--').decode('utf-8', errors='ignore')
        dateDigitized = exif_dict['Exif'].get(36868, b'--').decode('utf-8', errors='ignore')    
        if dateOriginal != '--':
            #DateTimeOriginal
            new_timestamp = datetime.datetime.strptime(dateOriginal, "%Y:%m:%d %H:%M:%S") + delta
            exif_dict['Exif'][36867] = new_timestamp.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
        if dateDigitized != '--':
            #DateTimeDigitized
            new_timestamp = datetime.datetime.strptime(dateDigitized, "%Y:%m:%d %H:%M:%S") + delta
            exif_dict['Exif'][36868] = new_timestamp.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')

        if dateOriginal != '--' or dateDigitized != '--':
            # Open and save image with new EXIF data
            im = Image.open(fname)
            exif_bytes = piexif.dump(exif_dict)
            new_file = new_timestamp.strftime("%Y%m%d-%H%M%S")          
            i = 0
            while (os.path.isfile(image_path  + new_file + ('' if i == 0 else '_' + str(i)) + '.JPG')):
                i += 1
            im.save(image_path  + new_file + ('' if i == 0 else '_' + str(i)) +'.JPG', exif=exif_bytes, quality='keep')
            print(f"updated {dateOriginal if dateOriginal != '--' else dateDigitized }->{new_timestamp.strftime("%Y:%m:%d %H:%M:%S")}")
        else:
            print(" No Timestamp found in EXIF data")
        
    except Exception as e:
        print(f"Error setting datetime: {str(e)}")

def print_allexif(fname: str):
    img = Image.open(fname)
    exif = img.getexif()

    print('>>>>>>>>>>>>>>>>>>', 'Base tags', '<<<<<<<<<<<<<<<<<<<<')
    for k, v in exif.items():
        tag = TAGS.get(k, k)
        print(tag, v)

    for ifd_id in IFD:
        print('>>>>>>>>>', ifd_id.name, '<<<<<<<<<<')
        try:
            ifd = exif.get_ifd(ifd_id)

            if ifd_id == IFD.GPSInfo:
                resolve = GPSTAGS
            else:
                resolve = TAGS

            for k, v in ifd.items():
                tag = resolve.get(k, k)
                print(tag, v)
        except KeyError:
            pass

def print_DateOriginal(imagepath: str):
    try:
        # Load existing EXIF data
        exif_dict = piexif.load(imagepath)
        # 36867 = DateTimeOriginal
        dateOriginal = exif_dict['Exif'].get(36867, b'--').decode('utf-8', errors='ignore')
        print(f"{imagepath}: {dateOriginal}")
    except Exception as e:
        print(f"Error setting datetime: {str(e)}")

# Example usage
if __name__ == "__main__":
    # image path with pictures
    # Zuzka 50ka -> posun datetime.timedelta(days=23*365 + 7*31 + 8, hours=8, minutes=30)
    # Tomi birmovka -> datetime.timedelta(days=3*365 + 10*31 + 2, hours=22, minutes=21)
    image_path = "C:\\home\\rodina\\fotografie\\nove\\zuzka50\\"
   
    for image_file in os.listdir(image_path):
        if os.path.isfile(image_path + '\\' + image_file) and image_file.split('.')[-1] == 'JPG':
            # print_DateOriginal(image_path + '\\' + image_file)
            set_image_datetime(image_path, image_file, datetime.timedelta(days=23*365 + 7*31 + 8, hours=8, minutes=30))
