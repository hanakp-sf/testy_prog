#pip install Pillow
#pip install piexif
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS, IFD
import datetime
import piexif

        # Set the date time in different EXIF fields
        # 36867 = DateTimeOriginal
        # 36868 = DateTimeDigitized
        # 306 = DateTime
        # exif_dict['Exif'][36867] = datetime_str.encode('utf-8')
        # exif_dict['Exif'][36868] = datetime_str.encode('utf-8')
        # exif_dict['0th'][306] = datetime_str.encode('utf-8')
def set_image_datetime(image_path, delta):
    try:
        print(f"Processing {image_path}")
        data = None
        # Load existing EXIF data
        exif_dict = piexif.load(image_path)
        #print(exif_dict)  # Debugging line to see the entire EXIF data structure
        dateOriginal = exif_dict['Exif'].get(36867, b'--').decode('utf-8', errors='ignore')
        dateDigitized = exif_dict['Exif'].get(36868, b'--').decode('utf-8', errors='ignore')    
        if dateOriginal != '--':
            #DateTimeOriginal
            new_timestamp = datetime.datetime.strptime(dateOriginal, "%Y:%m:%d %H:%M:%S") + delta
            exif_dict['Exif'][36867] = new_timestamp.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
        if dateDigitized != '--':
            #DateTimeOriginal
            new_timestamp = datetime.datetime.strptime(dateDigitized, "%Y:%m:%d %H:%M:%S") + delta
            exif_dict['Exif'][36868] = new_timestamp.strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')

        if dateOriginal != '--' or dateDigitized != '--':
            # Open and save image with new EXIF data
            im = Image.open(image_path)
            exif_bytes = piexif.dump(exif_dict)
    
            im.save(image_path, exif=exif_bytes, quality='keep')
            print(f"Successfully updated {dateOriginal if dateOriginal != '--' else dateDigitized }->{new_timestamp.strftime("%Y:%m:%d %H:%M:%S")}")
        else:
            print(" No Timestamp found in EXIF data")
        
    except Exception as e:
        print(f"Error setting datetime: {str(e)}")

def print_exif(fname: str):
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


# Example usage
if __name__ == "__main__":
    # Replace with your image path
    image_path = "C:\\Users\\A410442\\Downloads\\DSC_0191.jpg" #20100403-151405.jpg DSC_0191.jpg 20250920_123657.jpg"
    #set_image_datetime(image_path, datetime.timedelta(days=23*365 + 7*31 + 8, hours=8, minutes=30))
    print_exif(image_path)
