import pathlib
import shutil
import cv2
import os, sys, csv
import traceback
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats
from PIL import Image, ImageChops, ImageStat, ImageOps, ImageFilter
import pytesseract
import importlib
import crop_functions
from crop_functions import get_contours
from crop_functions import contour_df
from crop_functions import *
importlib.reload(crop_functions)

def volList(volume):
    """
    This function generates a sorted list of image file paths for a specified volume.
    
    Parameters:
    volume (str): The volume number used to locate images.
        
    Returns:
    tuple: A tuple containing a list of file paths and the volume number.
    """
    images_dir = f"images/{volume}"
    volume_path = os.path.join(os.getcwd(), images_dir)
    print(f"Checking directory: {volume_path}")  
    if not os.path.exists(volume_path):
        print(f"Directory does not exist: {volume_path}")
        return [], volume
    
    file_list = []

    filepaths = [f.path for f in os.scandir(volume_path) if f.is_file()]
    for filename in filepaths:
        if pathlib.Path(filename).suffix == '.jpg':
            file_list.append(filename)
    file_list.sort()
    return file_list, volume

def crop(volume, path_list, dil_iter=30, x_buffer=20, y_buffer=5):
    """
    This function crops images based on bounding boxes determined from contours and save the cropped images.

    Parameters:
    volume (str): The volume number used to locate images and save output.
    path_list (list): List of image file paths to process.
    dil_iter (int, optional): Number of dilation iterations for contour detection. Default is 30.
    x_buffer (int, optional): Horizontal buffer for bounding box. Default is 20.
    y_buffer (int, optional): Vertical buffer for bounding box. Default is 5.
    
    Returns: 
    """
    imgs_dict = {}
    imgs_df = pd.DataFrame(columns=["id", "path", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])
    path_list.sort()
    y1 = 0
    y2 = 0
    x1 = 0
    x2 = 0
    for i, path in enumerate(path_list):
        img = cv2.imread(path)

        filename = os.path.basename(path)
        contours, hierarchy = get_contours(img, dil_iter)

        c_df = contour_df(img, contours, hierarchy)

        error = False
        try:
            x1, x2, y1, y2 = main_bbox(img, c_df, x_buffer, y_buffer)
        except:
            print(f"There was an issue finding the main bounding box with {path}")
            print(f"{path} looks like this:")
            error = True
        #crop the image 
        cropped = img[y1:y2, x1:x2]

        check = check_for_marginalia(cropped)
        #check for marginalia 
        if check == True:
            try:
                diff = remove_child_marginalia(cropped, dil_iter)
                x1 = x1 + diff
            except:
                print(f"There was an issue removing child marginalia with {path}")
                error = True

        cropped = img[y1:y2, x1:x2]
        #more cropping based on contour
        try:
            top_diff, bottom_diff = crop_round2(cropped, dil_iter)
            y1 = y1+top_diff
            y2 = y2 - bottom_diff
        except:
            print(f"There was an issue in the second round of cropping with {path}")
            error = True
        #update dict with image data 
        imgs_dict[i] = {
            'path': path,
            'filename': filename,
            'bbox_x1': x1,
            'bbox_y1': y1,
            'bbox_x2': x2,
            'bbox_y2': y2,
                }
        cwd = os.getcwd()

        if error is True:
            dir = f"{cwd}/images/{volume}/issues/" #save cropped images 
            if not os.path.exists(dir):
                os.makedirs(dir, exist_ok=False)
            plt.imsave(dir + filename, img)
            print('image with issues saved to issues folder')
        else:
            dir = f"{cwd}/images/{volume}/cropped/"
            if not os.path.exists(dir):
                os.makedirs(dir, exist_ok=False)
            name = filename.replace('.jpg', '')
            plt.imsave(dir + name + '_crop.jpg', img[y1:y2, x1:x2])
        dir = f"{cwd}/images/{volume}/originals/"
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=False)
        try:
            shutil.move(filename, f"{dir}{filename}")
        except OSError:
            pass
        plt.close()



    imgs_df = pd.DataFrame(columns=["id", "path", "filename", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])

    imgs_df = pd.DataFrame.from_dict(imgs_dict, orient="index")
    csv_path = f"{cwd}/images/{volume}/{volume}_contourreport.csv"
    print(f"Saving CSV to: {csv_path}")
    imgs_df.to_csv(csv_path, index_label="ID")

def get_stats(volume):
    """
    This function analysis statistical properties of bounding box coordinates and identify outliers.
    Parameters:
    volume (str): The volume number used to locate the CSV file with bounding box data.
    
    Returns:
    list: A list of filenames with bounding box coordinate outliers.
    """
    coords = ["x1", "y1", "x2", "y2"]

    dirpath = sys.path.append(os.path.abspath("./"))
    os.chdir('../images/'+str(volume))
    df = pd.read_csv(f"./{volume}_contourreport.csv")
    files = []
    for coord in coords:
        #print(np.std(df[f"bbox_{coord}"]))
        column = f"bbox_{coord}"
        z = np.abs(stats.zscore(df[column]))
        outliers = np.where(z > 2.5)
        for outlier in outliers:
            for index in outlier:
                file = df['filename'].values[index]
                print(file)
                files.append(file)
                shutil.copy("./originals/" + file, "./issues/" + file)
        df[f"bbox_{coord}_z"] = z
    df.to_csv(f"{volume}_z-scores.csv", index=False)
    return files

def process_outliers(volume):
    """
    This function processes files identified as outliers by removing their cropped images and copying originals to the issues folder.
    
    Parameters:
    volume (str): The volume number used to locate the CSV file with bounding box data and manage files.
    
    Returns:
    list: A sorted list of filenames with bounding box coordinate outliers.
    """
    coords = ["x1", "x2"]
    df = pd.read_csv(f"./{volume}_contourreport.csv")
    files = []
    for coord in coords:
        #print(np.std(df[f"bbox_{coord}"]))
        column = f"bbox_{coord}"
        z = np.abs(stats.zscore(df[column]))
        outliers = np.where(z > 2.5)
        for outlier in outliers:
            for index in outlier:
                file = df['filename'].values[index]
                files.append(file)
                try:
                    shutil.copy("./originals/" + file, "./issues/" + file)
                except:
                    pass
                filename = file.replace('.jpg', '')
                target = f"./cropped/{filename}_crop.jpg"
                if os.path.exists(target):
                    os.remove(target)
                else:
                    pass

        df[f"bbox_{coord}_z"] = z
    df.to_csv(f"{volume}_z-scores.csv", index=False)
    files.sort()
    return files



def reprocess_issues(volume):
    """
    This function reprocesses images flagged as issues. This function currently just lists the issue files.
    
    Parameters:
    volume (str): The volume number used to locate the issues directory.
    
    Returns:
    None
    """
    dirpath = sys.path.append(os.path.abspath("./"))
    #os.chdir('../../images/'+str(volume)+'/issues')
    os.chdir('../../issues/')
    issues_list = os.listdir(dirpath)
    issues_list.sort()
    print(issues_list)




