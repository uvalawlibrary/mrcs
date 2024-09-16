import sys, os
import pandas as pd




def volume_data(volume):
    """
    This function finds data about the volume's images, such as the number of pages, 
    percentage of cropped images, and the number of issues.

    Parameters:
    volume (str): The name of the volume/folder directory

    Returns:
    tuple: A tuple containing:
        pages (int or str): The number of pages in the volume or "n/a" if no pages are found.
        progress (str): The percentage of cropped images formatted as a string percentage or "n/a".
        issues (int or str): The number of issues found or "None" if the issues directory doesn't exist.
    """
    cwd = os.getcwd()

    pages = [x for x in os.listdir(f"{cwd}/images/{volume}/originals") if '.jpg' in x]
    cropped = [x for x in os.listdir(f"{cwd}/images/{volume}/cropped") if '.jpg' in x]
    issues_dir = f"{cwd}/images/{volume}/issues"
    if os.path.exists(issues_dir):
        issues = len([x for x in os.listdir(issues_dir) if '.jpg' in x])
    else:
        issues = "None"
    if(len(pages) > 0):
        percent = len(cropped) / len(pages)
        progress = f"{percent:.1%}"
        pages = len(pages)
    else:
        pages = "n/a"
        progress = "n/a"

    return pages, progress, issues


def prepare_report():
    """
    This function prints a report of the volume processing status, including
    the number of pages, percentage of cropped images, and the number of issues for each volume.
    
    The report is presented as a DataFrame and printed to the console.
    """
    cwd = os.getcwd()
    dir = f"{cwd}/images"
    volumes = os.listdir(dir)
    volumes.sort()
    report = pd.DataFrame(columns=["volume", "pages", "percent_cropped", "issues"])
    stats_dict = {}
    for i, volume in enumerate(volumes):
        dir = f"{cwd}/images/{volume}"
        if os.path.exists(f"{cwd}/images/{volume}/cropped") and os.path.isdir(f"{cwd}/images/{volume}"):

            pages, progress, issues = volume_data(volume)
            stats_dict[i] = {
                'volume': volume,
                'pages': pages,
                'percent_cropped': progress,
                'issues': issues,
                }
        else:
            if os.path.isdir(f"{cwd}/{volume}"):
                stats_dict[i] = {
                    'volume': volume,
                    'pages': "unprocessed",
                    'percent_cropped': "unprocessed",
                    'issues': "unprocessed",
                    }
    report = pd.DataFrame.from_dict(stats_dict, orient="index")
    print(report.to_string())




#calls prepare_report() to generate and display the report 
prepare_report()
