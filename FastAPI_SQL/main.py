from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
import sqlite3
import cv2
import numpy as np
import io


def load_database(database_name):
    global connection
    global cursor
    connection = sqlite3.connect(database_name, check_same_thread=False)
    cursor = connection.cursor()

load_database("school.db")

app = FastAPI()

@app.get('/')
def read_root():
    return "Welcome to FastAPI_SQL project"

@app.get("/read_students")
def read_students():
    student_db = cursor.execute("SELECT * FROM students")
    return f"Registered students are {student_db.fetchall()}"

@app.get('/read_student')
def read_student(ID: int = Form()):
    IDs = cursor.execute('''SELECT ID FROM students''').fetchall()
    IDs = [id[0] for id in IDs]
    if ID not in IDs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Student not found")
    
    student = cursor.execute(f'''SELECT * FROM students
                             WHERE ID = {ID}''')
    return f"Registered student is {student.fetchone()}"
    
@app.put('/update_student')
def update_student(ID: int = Form(), name: str = Form(None), degree: str = Form(None)): #, profile: bytes = Form(None))
    IDs = cursor.execute('SELECT ID FROM students').fetchall()
    IDs = [id[0] for id in IDs]
    if ID not in IDs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail="Student not found")
    if name is not None:
        cursor.execute(f'''UPDATE students
                       SET "name"= {name}
                       WHERE "ID" = {ID}''')
        connection.commit()
    if degree is not None:
        cursor.execute(f'''UPDATE students
                       SET degree = {degree}
                       WHERE ID = {ID}''')
        connection.commit()

    return "Updated"

@app.delete('/delete_student')
def delete_student(ID: int = Form()):
    IDs = cursor.execute('''SELECT ID FROM students''').fetchall()
    IDs = [id[0] for id in IDs]
    if ID not in IDs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student not found")
    else:
        cursor.execute(f'''DELETE FROM students WHERE ID = {ID}''')
        connection.commit()
        return "Removed"

@app.post("/create_student")
def create_student(ID: int = Form(), name: str = Form(None), degree: str = Form(None)):
    if (name is None or degree is None):
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail='''Please fill all forms''')
    else:
        cursor.execute(f'''INSERT INTO students(ID, name, degree) VALUES ({ID}, {name}, {degree})''')
        connection.commit()
        return "Created"


@app.post("/rgb2gray")
async def rgb2gray(inp_file: UploadFile = Form(None)):
    if inp_file is None:
        raise HTTPException(status_code=status.HTTP_417_EXPECTATION_FAILED, detail='''Please upload an image''')
    if not inp_file.content_type.startswith('image/'):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Please upload an image data type")
    else:
        contents = await inp_file.read()
        img_arr = np.frombuffer(contents, dtype=np.uint8)
        img_rgb = cv2.imdecode(img_arr, cv2.IMREAD_UNCHANGED)
        img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
        _, encoded_img = cv2.imencode('.jpg', img_gray)
        encoded_img = encoded_img.tobytes()
        return StreamingResponse(io.BytesIO(encoded_img), media_type='image/jpeg')