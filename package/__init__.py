import os
import sys
from urllib.parse import quote
from urllib.request import urlopen
from PIL import Image, ImageOps

from manage_examination.models import QuestionType, Question, Choice


def handle_upload_file(file, request):
    with open('upload/temp.txt', 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    with open('upload/temp.txt', "rb") as file:
        for line in file:

            question_string = line.decode().split()

            obj = Question.objects.create(question_type_id=request.POST["question_type"],
                                          question_subject_id=request.POST['subject'],
                                          question_title=question_string[0][:8],
                                          question_text=question_string[0],
                                          )
            type = QuestionType.objects.get(id=request.POST["question_type"]).question_type_text
            if type == "选择题":
                if len(question_string) > 5:
                    answer_text = question_string[-1]
                    obj.answer_text = answer_text
                    obj.save()
                for choice in question_string[1:5]:
                    Choice.objects.create(choice_text=choice, question_id=obj.id)



def img2webp(path):
    """
    Takes a path of an image and converts it to webp
    """
    file, ext = os.path.splitext(path)
    image = Image.open(path).convert("RGBA")
    image = ImageOps.expand(image, 75)
    image.save(file + ".webp", "WEBP")
    os.remove(path)


def latex2img(expression, filename):
    """
    Convert expression to an image called filename.extension
    """
    webp = False

    extension = "png"

    # Preparing text strings
    server = "http://latex.codecogs.com/" + extension + ".download?"
    fullname = filename + "." + extension
    size = "%5Cdpi%7B100%7D%20"

    # Quote expression引用表达式
    expression = quote(expression)
    url = server + size + expression

    # Download file from url and save to output_file:
    with urlopen(url) as response, open(fullname, 'wb') as output_file:
        data = response.read()  # Un objeto "bytes"
        output_file.write(data)  # Se escribe en disco

    if webp:
        img2webp(fullname)
        extension = "webp"

    return filename + "." + extension
