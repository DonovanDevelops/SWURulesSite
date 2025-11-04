# Need to `pip install os` for this
import os

def images_to_array(folders):
    outputlocation = 'pdf_images.js'

    folderstring = "window.projectNamespace = window.projectNamespace || {};\n"
    for folder in folders:
        files = os.listdir('rules_documents/' + folder)
        folderstring += 'projectNamespace.' + folder.lower() + ' = window.projectNamespace.' + folder.lower() + ' || ["' + '", "'.join(files) + '"];\n'

    # Write the extracted text to a text file
    with open(outputlocation, 'w', encoding='utf-8') as txt_file:
        txt_file.write(folderstring)   

if __name__ == "__main__":
    doc_folders = ['CR', 'MED', 'TR']

    images_to_array(doc_folders)

    print("PDF images ready for HTML!")