import csv
import os
import nltk
import pandas as pd



def get_text():
    """
    This function identifies laws from a CSV file and returns them as a list of dictionaries.
    
    Returns:
    keyed_arrays: A list where each dictionary represents a row in the identified laws CSV file, 
    with keys as column headers and values as corresponding cell values.
    """
    lawlist = f"{os.getcwd()}/data/identified_laws.csv"
    index_array = []
    with open(lawlist, encoding='utf-8-sig', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        keyed_arrays = []

        for row in reader:
            keyed_array = {}
            for header, value in row.items():
                keyed_array[header] = value
            keyed_arrays.append(keyed_array)

    return keyed_arrays

def last8(x):
    """
    This function extracts the law number from a filename.
    
    Parameter:
        x (str): The filename containing the law number.
    
    Returns:
        int: The extracted law number as an integer.
    """
    start = x.index("law") + len("law")
    end = x.index(".", start)
    return int(x[start:end])


def tokenize_corpus():
    """    
    This function scans directories of law text files, tokenizes their content into sentences using NLTK's
    PunktSentenceTokenizer, and compiles the results into a pandas DataFrame which is then saved as a CSV file.
    """
    #get path to directory containing law volumes
    volumes = f"{os.getcwd()}/images/"
    volumes = [file for file in os.listdir(volumes) if os.path.isdir(os.path.join(volumes, file))]
    #volumes  = ['1875-76', '1962', '1965es']
    sid = 0
    corpus_sentences = []
    for volume in sorted(volumes):
        laws_dir = f"{os.getcwd()}/images/{volume}/laws"
        files = os.listdir(laws_dir)
        filtered = [item for item in files if not item.startswith('preceedingmaterials')]
        for filename in sorted(filtered, key=last8):
            if not filename.startswith("preceeding"):
                start = filename.index("law") + len("law")
                end = filename.index(".", start)
                lawnumber = int(filename[start:end])
                file_url = f"{laws_dir}/{filename}"

                if os.path.exists(file_url):
                    with open(file_url, 'r') as file:
                        text = file.read()
                        text = text.replace('\n', ' ')
                        tokenizer = nltk.tokenize.PunktSentenceTokenizer()
                        sentences = tokenizer.sentences_from_text(text)
                        for sentence in sentences:
                            sid += 1
                            data = [filename, volume, lawnumber, sid, sentence]
                            corpus_sentences.append(data)
    laws_data = pd.DataFrame(corpus_sentences, columns=['Filename', 'Volume', 'Law Number', 'SID', 'Sentence'])
    laws_data.to_csv(f"{os.getcwd()}/data/corpus_sentences.csv")



def iterator():
    """
    This function reads the identified laws and checks if their corresponding text files exist. It splits the text
    of each law into sentences, saving the results into individual CSV files.
    """

    data = get_text()
    for row in data:

        file_path = f"{os.getcwd()}/images/{row['Volume']}/laws/VAactsofassembly_{row['Volume']}_law{row['Chapter']}.txt"
        output_path = f"{os.getcwd()}/data/exploded/VAactsofassembly_{row['Volume']}_law{row['Chapter']}_exploded.csv"

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                text = file.read()
                text = text.replace('\n', '')
                sentences = text.split('. ')

                with open(output_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['phrase'])
                    for sentence in sentences:
                        writer.writerow([sentence])

        else:
            print(f"The file {os.path.basename(file_path)} does not exist.")

def split_text(volume):
    """
    This function reads text files of laws, extracts titles based on certain patterns, and compiles the data into
    a CSV file listing law numbers and their titles.  
    
    Parameters:
    volume (str): The volume identifier (e.g., a year or range of years) corresponding to a set of law files.
    
    Returns: 
    None 
    
    """
    laws_dir = f"{os.getcwd()}/images/{volume}/laws"
    volume_dir = f"{os.getcwd()}/images/{volume}"
    files = os.listdir(laws_dir)

    laws = []
    for file in files:
        print(file)
        para = []
        data = []
        path = f"{laws_dir}/{file}"
        if pathlib.Path(file).suffix == '.txt':
            with open(path) as infile:
                for line in infile:
                    cleaned = line.rstrip('\n')
                    if cleaned != '':
                        para.append(cleaned)
                    if cleaned == '':
                        break
        para = ' '.join(para)
        pattern = re.compile(r"Chap\. \d+(\,|\.)", re.IGNORECASE)

        lawmatch = pattern.search(para)
        if lawmatch:
            numberpattern = re.compile(r'\d+')
            numbermatch = numberpattern.search(lawmatch.group())
            lawnumber = numbermatch.group()
            posend = numbermatch.end()
        if posend:
            title = para[posend+2:]
        else:
            title = para
        data = [lawnumber, title]
        laws.append(data)


    laws_data = pd.DataFrame(laws, columns=['Law Number', 'Law Title'])
    laws_data.sort_values(by='Law Number')
    laws_data.to_csv(f"{volume_dir}/{volume}_lawtitles.csv")

tokenize_corpus()
