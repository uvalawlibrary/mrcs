#### PACKAGES ####
import cv2
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt


### FUNCTIONS ###

def get_contours(img, dil_iter=24):
    """
    This function finds the contours in a binary image. 
    
    PARAMETERS: 
    cv2 img: The image on which to find contours
    dil_iter: The number of iterations for dilation. The default is 24. 
    
    RETURNS: 
    contours(list): A list of contours found in the image. Each contour is a list of points. 
    """
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) 
    # converts image to grayscale
    _,thresh = cv2.threshold(gray,140, 255,cv2.THRESH_BINARY_INV) 
    # apply a binary threshold. Pixals greater than 140 are set to 0 and pixals less than or equal to 140 are set to 255. 
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3)) 
    # create a structuring element of size 3x3 
    dilated = cv2.dilate(thresh,kernel,iterations = dil_iter) 
    # dialates the thresholded image. The dil_iter parameter specifies how many times the operation is applied. 
    contours, hierarchy = cv2.findContours(dilated,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE) 
    #finds contours using OpenCV's findCountours function

    return contours, hierarchy 
    #returns a list of contours and hierarchy of contours 



def contour_df(img, cl, hr, round=1):
   """
   This function creates a dataframe from the contour and hierarchy objects extracted from an image in 
   get_contour containing detailed information about each contour. 

   PARAMETERS:
   img (cv2 image): The image the contours were detected in 
   cl (list of ndarray): A list of contours found in the image represented as a numpy array of points 
   hr (ndarray): A hierarchy array with contour relationships within the image 
   round (int): The filtering round to apply, the default is 1. dditional filtering is 
                performed to exclude small particles, watermarks, edge artifacts, and shadows.

   RETURNS:
   c_df: A DataFrame where each row represents a contour
   
   """
   c_list = []
   img_height, img_width,_ = img.shape
   img_area = img_height * img_width
    
   for i, c in enumerate(cl):
        rect = cv2.minAreaRect(c)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cont_x,cont_y,cont_width,cont_height = cv2.boundingRect(box)
        cont_area = cv2.contourArea(c)
        cont_wh_ratio = cont_width/cont_height #ratio of width to height
       
        if round == 1:
            # remove small particles
            if ((cont_wh_ratio > 0.9) and (cont_wh_ratio < 1.5) and (cont_area < (img_area*0.1))):
                continue
            
            # removes watermark 
            elif (i == 0 or i == 1) and (cont_area < img_area * 0.1):
                continue
            
            # removes items too close to the edges
            elif (((cont_x < img_width * 0.01) or (cont_x > img_width *0.99)) and (cont_area < img_area*0.2)):
                continue 
            
            # remove shadows from scans
            elif ((cont_x > img_width *0.97) and (cont_wh_ratio < 0.75)):
                continue
            
            else:
                c_list.append([i, cont_width,cont_height,cont_x,cont_y, cont_area, cont_wh_ratio])
        else: # filtering for different round values 
            if ((cont_y > img_height*0.975) or (cont_y < img_height*0.025)) and (cont_area < img_area * 0.1):
                continue
            else:
                c_list.append([i, cont_width,cont_height,cont_x,cont_y, cont_area, cont_wh_ratio])

   #create the dataframe from collected contour data 
   c_df = pd.DataFrame(c_list, columns=["index","width", "height", "x", "y", "area", "wh_ratio"])
   c_df['is_child'] = c_df['index'].apply(lambda i: 0 if hr[0][i][3] == -1 else 1)
   c_df['parent_contour'] = c_df['index'].apply(lambda i: hr[0][i][3] if hr[0][i][3] != -1 else -1)

   return c_df



def main_bbox(image, c_df, x_buffer=20, y_buffer=5, round=1):
   """
   This function finds the main bounding box fom an image based on the contour data using the largest contours. 
   This function also applies optional padding buffers. 
   
   PARAMETERS:
   img (cv2 image): The image the contours were detected in 
   c_df (contour DataFrame): A DataFrame containing contour information
   x_buffer (int): x-axis buffer to add to the left and right sides of the bounding box with a default of 20 pixels
   y_buffer (int): y-axis buffer to add to the top and bottom of the bounding box with a default is 5 pixels
   round (int): The processing stage or filtering round to apply with a default of 1

   RETURNS:
   tuple: Four values representing the coordinates of the bounding box:
          min_x: Minimum x-coordinate with the x_buffer applied
          max_x: Maximum x-coordinate with the x_buffer applied
          min_y: Minimum y-coordinate
          max_y: Maximum y-coordinate
   """  
   #if there is only one contour, use its bounding box directly 
   
   if len(c_df) == 1:
        min_x = c_df['x'][0]
        max_x = c_df['x'][0] + c_df['width'][0]
        min_y = c_df['y'][0]
        max_y = c_df['y'][0] + c_df['height'][0]
    
   else:
       #for multiple contours, find the largest contour 
        largest_contour = c_df[c_df.area == max(c_df['area'])].head(1)# .head() is used to prevent having more than one result
        x_width = largest_contour.width  # creates x-value boundaries based on the dimension of largest contour
        min_x = int(largest_contour.x)
        max_x = int(min_x + x_width)
        
        #calculate the vertical bounding box 
        
        c_df["bottom"] = c_df.y+c_df.height
        y_vals = np.array(c_df['y'])
        highest_contour = c_df[c_df['y'] == min(y_vals)].head(1)
        lowest_contour = c_df[c_df['bottom'] == c_df.bottom.max()]
        min_y = int(highest_contour['y'].values)
        max_y = int(lowest_contour['y'].values + lowest_contour['height'].values)

   if round == 1:
        # adjust the bounding box to remove excess whitespace or marginalia 
        img_height,img_width,_ = image.shape
        #calculate the median pixal value in the middle strip of the image 
        mid_pixels = [np.mean(x) for x in np.array(image[min_y:max_y, int(min_x/2-5):int(max_x/2+5)])]
        mid_pixels.sort()
        mid_median = np.mean(mid_pixels)
        #adjust the right boundry of the bounding box 
        right_strip = np.array(image[min_y:max_y, max_x-5:max_x])
        right_pixels = [np.mean(x) for x in right_strip]
        right_pixels.sort()
        right_median = np.mean(right_pixels)
        
        while (right_median > mid_median):
            max_x = max_x - 5
            right_strip = np.array(image[min_y:max_y, max_x-5:max_x])
            right_pixels = [np.mean(x) for x in right_strip]
            right_pixels.sort()
            right_median = np.mean(right_pixels)
        #adjust the left boundry of the bounding box     
        left_pixels = [np.mean(x) for x in np.array(image[min_y:max_y, min_x:min_x+5])]
        left_pixels.sort()
        left_median = np.mean(left_pixels)
        
        while (left_median > mid_median):
            min_x = min_x + 5
            left_pixels = [np.mean(x) for x in np.array(image[min_y:max_y, min_x:min_x+5])]
            left_pixels.sort()
            left_median = np.mean(left_pixels)   

    # returns values with the buffer applied to the x values 
   return min_x-x_buffer, max_x+x_buffer, min_y, max_y

# checks cropped image if marginalia is still present
# usually only an issue with pages with left-hand marginalia 
# PARAMETERS: cropped cv2 image
# RETURNS: Boolean 
def check_for_marginalia(img):
    """
    This function checks if the marginalia is still present in a cropped image 
    
    PARAMETERS: 
    img (cv2 image) the cropped image in which to check for marginalia. This should be a numpy array. 
    
    RETURNS: 
    bool: returns true if marginalia is detected, otherwise returns false 
    """
    img_height, img_width, _ = img.shape #retrieves the dimensions of the image 
    try:
        left_strip = np.mean(np.array(img[:,0:int(img_width*0.05)])) #looks at the left strip
        right_strip = np.mean(np.array(img[:,img_width-int(img_width*0.05):img_width])) #looks at the right strip 
        mid_strip = np.mean(np.array(img[:,int(img_width/2)-int(img_width*0.025):int(img_width/2)+int(img_width*0.025)])) #looks at the middle of the image 
    except:
        print(f"there was an issue with {path}")
    if ((left_strip) > (right_strip)) and ((left_strip-right_strip) > (right_strip*0.03)):
        return True
    else:
        return False
   
  
def remove_child_marginalia(img, dil_iter=24):  
   """
   This function removes marginalia from child contours of the largest contour in a cropped image. It uses 
   image processing techniques to identify and remove smaller, irrelevant contours that may be considered marginalia.
   
   PARAMETERS:
   img (cv2 image): The cropped image to be cleaned
   dil_iter (int, optional): The number of dilation iterations to apply during image processing with a default of 24 

   RETURNS:
   int: The mean width of the child contours which is used to change x1 value in the main function 
   """
   gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY) # grayscale
   _,thresh = cv2.threshold(gray,140, 255,cv2.THRESH_BINARY_INV) # threshold
   kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3)) 
   dilated = cv2.dilate(thresh,kernel,iterations = dil_iter) # dilate
   contours, hierarchy = cv2.findContours(dilated,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
   c_df = contour_df(img, contours, hierarchy, round==2)
    
  # finds the largest contour 
   max_area = np.max(c_df['area'])
   largest_contour = c_df[c_df['area'] == max_area].reset_index()
    
    #finds the child contours of the largest contour 
   children_contours = c_df[c_df['x'] == largest_contour['x'][0]]
   children_contours = children_contours[children_contours['index'] != largest_contour['index'][0]]
    #returns the mean width of the child contours or 0 is none are found 
   if len(children_contours) == 0:
        return 0
   else:
        mean_width= np.mean(children_contours['width'])
        return int(mean_width)



def crop_round2(img, dil_iter=24):
    """
    This function performs a second round of croppong on the left hand side of the image to remove other watermarks and headers 
    This function slices 10% of the width from the left side of the image to analyze and remove unwanted elements and converts it to grayscale, 
    applies binary thresholding, and uses dilation to enhance features for contour detection. Then determines if the vertical boundaries of the 
    content are within this slice to fit the overall cropping parameters. The values returned will adjust the y1 and y2 variables in the main function. 

    PARAMETERS:
    img (cv2 image): The input image to be processed 
    dil_iter (int, optional): The number of dilation iterations to apply during image processing with a default of 24

    RETURNS:
    A tuple containing two values:
        top_diff (int): The adjustment to the top boundary (minimum y-value)
        bottom_diff (int): The adjustment to the bottom boundary (maximum y-value)
    """
    strip_width = int(img.shape[1]*0.1)
    strip = img[:,0:strip_width]
    
    gray = cv2.cvtColor(strip,cv2.COLOR_BGR2GRAY) # grayscale
    _,thresh = cv2.threshold(gray,140, 255,cv2.THRESH_BINARY_INV) # threshold
    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
    dilated = cv2.dilate(thresh,kernel,iterations = dil_iter) # dilate
    contours, hierarchy = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    c_df = contour_df(strip, contours, hierarchy, round==2)
    
    if len(c_df) == 1:
        min_y = c_df['y'][0]
        max_y = c_df['y'][0] + c_df['height'][0]
    
    else:
        c_df["bottom"] = c_df.y+c_df.height
        y_vals = np.array(c_df['y'])
        highest_contour = c_df[c_df['y'] == min(y_vals)].head(1)
        lowest_contour = c_df[c_df['bottom'] == c_df.bottom.max()]
        min_y = int(highest_contour['y'].values)
        max_y = int(lowest_contour['y'].values + lowest_contour['height'].values)

    top_diff = min_y
    bottom_diff = img.shape[0] - max_y
    return top_diff, bottom_diff 


def crop_report(path_list, dil_iter=30, x_buffer=20, y_buffer=5):
    """
    This function processes a list of image paths to extract and report the main bounding boxes of the content in each image. It 
    also reads images from the provided paths, detects contours, and calculates the main bounding box. It logs the bounding box coordinates 
    for each image, which can be used for further image processing or analysis.
    
    PARAMETERS:
    path_list (list of str): A list of paths to the images that need processing
    dil_iter (int): Number of dilation iterations used in contour detection to enhance image features with a default of 30
    x_buffer (int): Additional buffer to add to the x-coordinates of the bounding box for extra padding with a default of 20
    y_buffer (int): Additional buffer to add to the y-coordinates of the bounding box for extra padding with a default of 5
    
    RETURNS:
    results: A dictionary for bounding box data for each image 
    
    """

    imgs_dict = {}
    imgs_df = pd.DataFrame(columns=["path", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])
    path_list.sort()
    results = []
    for i, path in enumerate(path_list):
        img = cv2.imread(path)
        contours, hierarchy = get_contours(img, dil_iter)
        c_df = contour_df(img, contours, hierarchy)
        try:
            x1, x2, y1, y2 = main_bbox(img, c_df, x_buffer, y_buffer)
            results.append({
                'path': path,
                'bbox_x1': x1,
                'bbox_y1': y1,
                'bbox_x2': x2,
                'bbox_y2': y2,
            })       
        except:
            print(f"There was an issue finding the main bounding box with {path}")

    return results 



### MAIN FUNCTION ###

def crop2csv(path_list, dil_iter=30, x_buffer=20, y_buffer=5):
    """
    This main function is to process images and save their bounding box coordinates to a csv file 
    This function processes a list of image paths, finds the main bounding box for each image, 
    performs more cropping to remove watermarks, etc..., and saves the results to a csv file named 
    "cropped_images_bounding_boxes.csv". It also displays the original images and cropped images for extra verification. 
    
     PARAMETERS:
     path_list: a list of full paths to the images to be processed
     dil_iter: The number of dilation iterations to apply when finding contours with a default of 30
     x_buffer: Buffer to apply on the x-axis of the bounding box to fine-tune the cropping with a default of 20
     y_buffer: Buffer to apply on the y-axis of the bounding box to fine-tune the cropping with a default of 5
    
     RETURNS:
     None
     The function saves the bounding box data to a CSV file named cropped_images_bounding_boxes.csv and does not return any value.
    """
    imgs_dict = {}
    imgs_df = pd.DataFrame(columns=["path", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])
    path_list.sort()
    for i, path in enumerate(path_list):
        img = cv2.imread(path)
        filename = os.path.basename(path)
        print(filename)
        contours, hierarchy = get_contours(img, dil_iter)
        
        c_df = contour_df(img, contours, hierarchy)

        try:
            x1, x2, y1, y2 = main_bbox(img, c_df, x_buffer, y_buffer)
        except:
            print(f"There was an issue finding the main bounding box with {path}")
            print(f"{path} looks like this:")

        
        cropped = img[y1:y2, x1:x2]

        check = check_for_marginalia(cropped)
        
        if check == True:
            try:    
                diff = remove_child_marginalia(cropped, dil_iter)
                x1 = x1 + diff
            except:
                print(f"There was an issue removing child marginalia with {path}")

        
        cropped = img[y1:y2, x1:x2]

        try:
            top_diff, bottom_diff = crop_round2(cropped, dil_iter)
            y1 = y1+top_diff
            y2 = y2 - bottom_diff
        except:
            print(f"There was an issue in the second round of cropping with {path}")
 

        imgs_dict[i] = {
            'path': path,
            'filename': filename,
            'bbox_x1': x1,
            'bbox_y1': y1, 
            'bbox_x2': x2,
            'bbox_y2': y2,
                }
        print(imgs_dict[i])
        plt.close()
        f, ax = plt.subplots(1,2)
 
    imgs_df = pd.DataFrame(columns=["path", "filename", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])
    imgs_df = pd.DataFrame.from_dict(imgs_dict, orient="index")
    imgs_df.to_csv("./cropped_images_bounding_boxes.csv", index_label=False)

