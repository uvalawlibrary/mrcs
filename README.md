# MRCS Project 

Project Overview

The [Modeling a Racial Caste System (MRCS)](http://uvalawlibrary8dev.prod.acquia-sites.com/mrcs/) is a [collections as data](https://collectionsasdata.github.io/part2whole/) project of the University of Virginia's Law Library which aims to compile a digital corpus of Virginia laws passed from 1865 to 1968, focusing on the Jim Crow era. This README provides a detailed guide to the steps taken to process legislative documents for Optical Character Recognition (OCR) and subsequent analysis.

[Learn more](http://uvalawlibrary8dev.prod.acquia-sites.com/mrcs/) 



# Installation Process 

Install Anaconda Python: Install Anaconda from [Anaconda website](https://www.anaconda.com/distribution/) and download the latest Python version (3.8 or later), then verify the installation by running: 

```
conda --version
```
Install Python Packages: This project requires several Python libraries to be installed. You can install all of the dependencies as shown below.

```
pip install <package-name>
```

Install Tesseract OCR (v4.0 or higher): Follow the [Tesseract installation guide](https://tesseract-ocr.github.io/tessdoc/Installation.html) for your operating system, then verify the installation by running:
```
tesseract --version
```
Tesseract should be added to your PATH to smoothly run scripts. 

# Running the Scripts 


| Script Name       | Function                                                                                           |
|-------------------|----------------------------------------------------------------------------------------------------|
| `flow.py`         | Orchestrates the processing of image volumes for cropping, OCR, and text extraction.               |
| `crop.py`         | Crops images to isolate the main text block, removing headers, footers, and marginalia.            |
| `crop_functions.py` | Utility functions for contour detection and bounding box calculations during image processing.     |
| `status.py`       | Generates reports on image processing status and progress.                                         |
| `splitter.py`     | Splits extracted text into sentences.                     |
| `text_tools.py`   | Additional text processing tools for manipulating and cleaning OCR text.                           |
| `ocr.py`          | Handles OCR application on cropped images to generate machine-readable text files.                 |


### 1. **flow.py**
   - **Command**: 
     ```bash
     python flow.py
     ```
### 2. **crop.py**
   - **Command**:
     ```bash
     python crop.py --input <path_to_images> --output <output_directory>
     ```
### 3. **crop_functions.py**
   - **Command**: 
     - This script is imported by `crop.py` so there is no command. 
   
### 4. **status.py**
   - **Command**:
     ```bash
     python status.py --input <path_to_image_folder>
     ```
### 5. **splitter.py**
   - **Command**:
     ```bash
     python splitter.py --input <text_file> --output <output_file>
     ```
### 6. **text_tools.py**
   - **Command**: 
     - This script is imported by other files so there is no command. 

### 7. **ocr.py**
   - **Command**: 
     ```bash
     python ocr.py --input <path_to_cropped_images> --output <output_directory>
     ```

