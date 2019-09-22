### FIRST READ EACH BLOCK IN AN ARRAY

from bs4 import BeautifulSoup
import subprocess
import redis
import re
import json

def get_bound_box(uuid, file):
    print(file)
    response = open(file)
    html_doc = response.read()
    response.close()
    html_file = BeautifulSoup(html_doc, 'html.parser')

    all_elements = []
    blocks = html_file.findAll('block')
    for block in blocks:
        list_elements = []
        words = block.findAll('word')
        for word in words:
            word_list = []
            word_list.append(word["xmin"])
            word_list.append(word["ymin"])
            word_list.append(word["xmax"])
            word_list.append(word["ymax"])
            word_list.append(word.string)
            list_elements.append(word_list)
        all_elements.append(list_elements)


    #### NEXT SORT ELEMENTS IN EACH BLOCK BY THEIR X AND Y COORDINATES
    #### FIRST TRYING XMIN und YMAX
    ###FIRST CHECKING IF THE ELEMENTS ARE VERTICAL, IF YES THEN NO SORTING
    new_all_elements = []

    for element in all_elements:
        later_bigger = (float(element[-1][0])-(float(element[0][0]))) #check if xmin from first element is bigger than xmin from last element
        abstand_x = abs(float(element[-1][0])-(float(element[0][2])))
        abstand_y = abs(float(element[-1][3])-float(element[0][1]))
        if later_bigger >= -5:
            #print(abstand_x-abstand_y)
            new_all_elements.append(element)
        else:
            new_element = sorted(element, key=lambda k: [float(k[0])])
            new_all_elements.append(new_element)


    """for element in new_all_elements:
        for blub in element:
            #print(blub[4])

        #print("\n")"""


    db = redis.Redis("localhost")
    db.set(uuid, "test")
    return new_all_elements, uuid

def pdf_to_html(uuid,filepath):
    subprocess.call(['pdftotext', '-bbox-layout',
                     filepath, str(uuid)+'out.html'])

def extract_isos(result):
    reg = r"(ISO\s\d\d\d\d*\W?\d?\W?\d?)|(EN\s\d*)"
    details_ = []
    for element in result:
        new_arr = ""
        #print(element)
        for x in element:
            new_arr += x[4] + " "
        print(new_arr)
        if re.search(reg,new_arr):
            #print(new_arr)
            found = re.findall(reg, new_arr)
            for f in found:
                if len(f[0]) != 0:
                    details_.append(f[0].replace(")",""))
                if len(f[1]) != 0:
                    details_.append(f[1])
    return details_

def main(uuid, result):
    pdf_to_html(uuid, result)
    res, uuid = get_bound_box(uuid, str(uuid)+"out.html")
    isos = extract_isos(res)
    isos_j = json.dumps(isos)
    db = redis.Redis("localhost")
    print(isos)
    db.set(uuid, str(isos_j))

"""file = "/home/bscheibel/PycharmProjects/dxf_reader/drawings/5129275_Rev01-GV12.html"
res, uuid = get_bound_box("uuu", file)
isos = extract_isos(res)
print(isos)
#pdf_to_html("/home/bscheibel/PycharmProjects/dxf_reader/drawings/5129275_Rev01-GV12.pdf")
"""

#main("uud","/home/bscheibel/PycharmProjects/dxf_reader/drawings/5129275_Rev01-GV12.pdf")