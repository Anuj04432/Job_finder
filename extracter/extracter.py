from pypdf import PdfReader
import re

# file = PdfReader("example.pdf")
# text1 = ""
# for i in file.pages:
#     text1 += i.extract_text()+"\n"
def name(text):
    name = None
    if name is None:
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        if lines:
            name = lines[0] 
    return name



def email(text):
    email = re.search(r'[A-Za-z0-9]+@[A-Za-z0-9]+\.[A-Za-z]{2,}',text)

    if not email:
        return "Email not provided in the resume"
    
    else:
        return email.group()




def number(text):
    number = re.search(r'[\+91]?\s?\d{5}[\s+]?\d{5}', text)
    if number:
        return number.group()
    else:
        return None


# print(number(text1))




