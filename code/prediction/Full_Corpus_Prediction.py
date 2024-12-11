import os
import transformers
from datasets import Dataset
import pandas as pd
from transformers import pipeline
import cuda 

"""
    We used this script to predict on the entire corpus. The corpus contained 445,824 sentences after cleaning,
    validation, and without the training set data. This will require significant computation time. 
    Consequently, we used UVA's research computing and submitted a SLURM request. 
    We used a script instead of notebook for SLURM for ease. The training took 2 hours instead of
    over 30 hours because we batched the training and used arrays in the SLURM request. 
    The SLURM script is available in the repository.

    The model predicted 30,814 Jim Crow sentences within the corpus.
    
"""

# This code initializes the indexing options in the SLURM script and the options txt files. 
#The frist option is 0 and the second is 14000. The options continue by 14,000 till the end of the corpus.

index1 = int(sys.argv[2])
index2 = int(sys.argv[3])

# # Load the corpus CSV file into a DataFrame
df = pd.read_csv('newfullcorpus_2024.csv')
df.drop(columns = 'Unnamed: 0', inplace=True)
df = df.iloc[index1:index2 + 1] # This specifies the indexed sentences in the corpus. 
#The +1 is a very important addition as it guarantees the last sentence in the index is included in the indexing.

# Initialize the UVA finetuned model and tokenizer inference pipeline for text classification
nlp = pipeline("sentiment-analysis", model="UVAJC_Final_bertmodel", tokenizer="UVAJC_Final_bertmodel_tokenizer", truncation=True)

# Define the name of the text column in your CSV
text_column = 'Sentence'  

# Perform inference and add the inferred labels to a new column. The Model Jim_Crow column creates a parallel column with 0 and 1 

df['Inferred_Label'] = df[text_column].apply(lambda x: nlp(x)[0]['label'])
df['Model Jim_Crow'] = df['Inferred_Label'].apply(lambda x: 1 if x == 'jim_crow' else 0)


# Save the updated DataFrame to a new CSV file
"""
    The code below saved each batch of 14000 into a new csv file. We ended up with 32 csv files which we recompiled. 
    
"""
filename = "fullpred_batchnew_{}.csv".format(sys.argv[1])

df.to_csv(filename, index=True)

print("Inference results saved to" + filename)


