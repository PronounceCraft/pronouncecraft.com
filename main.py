# ++++++++++++TESTING app.py WITH Symbols++++++++++++++++++++

import re
from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

# Load the Excel file
def load_excel(file_path):
    df = pd.read_excel(file_path)
    return df

# Function to get word and IPA for a list of words, modified to handle symbols
def get_words_and_ipa(df, line_words):
    word_to_ipa = dict(zip(df['Words'].str.strip().str.lower().str.replace('\xa0', ''), df['British IPA']))
    words_list = []
    ipa_list = []

    for word in line_words:
        # Use regex to find symbols before and after the word
        match = re.match(r'([^\w]*)(\w+)([^\w]*)', word)
        if match:
            prefix, core_word, suffix = match.groups()
            lower_word = core_word.lower()

            if lower_word in word_to_ipa:
                # If a match is found, append the original word with non-breaking space
                original_word = df.loc[df['Words'].str.strip().str.lower().str.replace('\xa0', '') == lower_word, 'Words'].values[0]
                words_list.append(prefix + original_word + suffix)  # Add symbols back to the word
                ipa_list.append(prefix + word_to_ipa[lower_word] + suffix)  # Add symbols back to the IPA
            else:
                words_list.append(prefix + core_word + suffix)  # Add symbols back to the word
                ipa_list.append(prefix + core_word + suffix)  # Keep the original word with symbols
        else:
            words_list.append(word)
            ipa_list.append(word)

    return words_list, ipa_list

# Function to pad words and IPA lists to the same length
def pad_words_and_ipa(words_list, ipa_list):
    padded_words = []
    padded_ipa = []

    for word, ipa_word in zip(words_list, ipa_list):
        max_length = max(len(word), len(ipa_word))
        
        # Pad the word and IPA transcription based on their lengths
        if len(word) < len(ipa_word):
            padded_words.append(word.ljust(max_length))
            padded_ipa.append(ipa_word)
        elif len(ipa_word) < len(word):
            padded_ipa.append(ipa_word.ljust(max_length))
            padded_words.append(word)
        else:  # len(word) == len(ipa_word)
            padded_words.append(word)
            padded_ipa.append(ipa_word)

    return padded_words, padded_ipa

# Function to format the output for display
def format_output(words_list, ipa_list, max_words_per_line=20):
    words_output = []
    ipa_output = []
    current_line_words = []
    current_line_ipa = []
    current_length = 0

    for word, ipa in zip(words_list, ipa_list):
        if word.strip() == "":
            if current_line_words:
                words_output.append(" ".join(current_line_words))
                ipa_output.append(" ".join(current_line_ipa))
                current_line_words = []
                current_line_ipa = []
                current_length = 0
                
        else:
            current_line_words.append(word)
            current_line_ipa.append(ipa)
            current_length += 1
            if current_length >= max_words_per_line:
                words_output.append(" ".join(current_line_words))
                ipa_output.append(" ".join(current_line_ipa))
                current_line_words = []
                current_line_ipa = []
                current_length = 0
    
    if current_line_words:
        words_output.append(" ".join(current_line_words))
        ipa_output.append(" ".join(current_line_ipa))

    combined_output = []
    for word_line, ipa_line in zip(words_output, ipa_output):
        if word_line.strip() != "":
            combined_output.append(word_line)
            combined_output.append(ipa_line)
            combined_output.append("")
        else:
            combined_output.append("")

    return "\n".join(combined_output)

# Load the Excel file once when the app starts
df = load_excel(r'C:\Users\Windows\Documents\IPA_TESTING_nonbreakingspace.xlsx')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_input():
    input_data = request.json.get('input')
    input_words = input_data.split("\n")
    words_list = []
    ipa_list = []
    
    for line in input_words:
        line_words = line.split()
        line_words_list, line_ipa_list = get_words_and_ipa(df, line_words)
        words_list.extend(line_words_list)
        ipa_list.extend(line_ipa_list)
        words_list.append("")  # Add a blank line to mark the end of the paragraph
        ipa_list.append("")  # Add a blank line to mark the end of the paragraph

    padded_words, padded_ipa = pad_words_and_ipa(words_list, ipa_list)
    combined_output = format_output(padded_words, padded_ipa, max_words_per_line=20)  # Adjust max_words_per_line as needed

    return jsonify({'output': combined_output})

if __name__ == '__main__':
    app.run(debug=True)
