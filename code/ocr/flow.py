from crop import *
from text_tools import *
from crop_functions import*

def single(volume):
    """
    This function processes a single volume/folder by cropping images within the volume.
    
    Parameters:
    volume (str): This is the identifier or path of the volume/folder to be processed.
    
    Returns:
    None
    """
    #gets the list of image files and the volume path
    list, volume = volList(volume)
    if len(list) > 0:
        #crops images with specified parameters 
        crop(volume, list, 18, 10, 30)
    else:
        print('no images files in root of volume directory')

def crop_all_volumes():
    """
    This function processes all volumes by cropping images within each volume.
    
    Parameters:
    None
    
    Returns:
    None
    """
    volumes.sort()
    for volume in volumes:
        if not os.path.exists(f"../../images/{volume}/cropped") and os.path.isdir(f"../../images/{volume}"):
            list, volume = volList(volume)
            crop(volume, list, 27, 20, 20)
            outliers = process_outliers(volume)
            print(volume + "done")

def ocr_all_croppped_volumes():
    """
    This function runs OCR on all cropped volumes
    
    Parameters:
    None
    
    Returns:
    None
    """

    volumes = os.listdir('../../images/')
    volumes.sort()
    for volume in volumes:
        if os.path.exists(f"../../images/{volume}/cropped") and os.path.isdir(f"../../images/{volume}"):
            ocr_cropped_volume(volume)


def process_laws(volume):
    """
    This function processes the laws from a given volume by running quality control, breaking down laws,
    and extracting their titles.
    
    Parameters:
    volume (str): The identifier or path of the volume to be processed.
    
    Returns:
    None
    """
    qc_process(volume)
    break_laws(volume)
    extract_titles(volume)

def build_corpus():
    """
    This function builds a corpus of laws by gathering and consolidating the laws from all processed volumes.
    
    Parameters:
    None
    
    Returns:
    None
    """
    gather_laws()


process_laws(1904)
