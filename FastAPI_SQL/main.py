from fastapi import FastAPI, HTTPException, status, File, Form, UploadFile
from fastapi.responses import StreamingResponse
import numpy as np
import io
import cv2

app = FastAPI()
students = dict()
students = {1: {'name': 'reza', 'degree': 'Msc'}, 2: {'name': 'sajjad', 'degree': 'Msc'}}

@app.get('/')
def get_root():
    return "Welcome to FastAPI project"


@app.get('/get_students')
def get_students():
    return f"Registered students are {students}"

@app.get('/get_student')
def get_student(id: int=Form()):
    if id in students.keys():
        return students[id]
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student has not found")

@app.post('/create_student')
def create_student(id: int=Form(), name: str=Form(), degree: str=Form()):
    students[id] = {"name": name, "degree": degree}
    return f"added student is: id={id}, name={name}, degree={degree}"

@app.put('/update_student')
def update_student(id: int=Form(), name: str=Form(None), degree: str=Form(None)):
    if id not in students.keys():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail="there is not student with this ID")
    if name is not None:
        students[id]['name'] = name
    if degree is not None:
        students[id]['degree'] = degree
    
    return f"updated student is: id={id}, name={name}"

@app.delete('/remove_student')
def remove_student(id: int=Form()):
    if id in students:
        deleted_student = f" id={id} and {students[id]}"
        del students[id]
        return "removed student is" + deleted_student
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="There isnt student with this id")

@app.post('/rgb2gray')
async def rgb2gray(inp_file: UploadFile=File(None)):
    if not inp_file.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail='Upload an image')
    contents = await inp_file.read()
    img_array = np.frombuffer(contents, dtype=np.uint8)
    decoded_img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
    img_gray = cv2.cvtColor(decoded_img, cv2.COLOR_RGB2GRAY)
    _, encoded_img = cv2.imencode('.jpg', img_gray)
    return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type='image/jpeg')
