from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi import HTTPException

from fastapi import status
import numpy as np
import cv2
import io


def generate_img(width, height, red, green, blue):
    img = np.zeros((height, width, 3), dtype="uint8")
    img[:,:] = [red, green, blue]
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    _, encoded_img = cv2.imencode('.png', img)
    return encoded_img

app = FastAPI()

@app.get('/ImgGeneration/{width}/{height}/{red}/{green}/{blue}/{scale_status}')
def ImgGeneration(width: int, height: int, red: int, green: int, blue: int, scale_status):
    if (scale_status == 'scaled'):
        if (0 <= red <= 1) and (0 <= green <= 1) and (0 <= blue <= 1):
            [red, green, blue] = np.array([red, green, blue] , 255)
            encoded_img = generate_img(width, height, red, green, blue)
            return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type='image/png') 
        else:
            raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                                detail="Range of valid values is between [0, 1]")
    elif (scale_status == 'unscaled'):
        if (0 <= red <= 255) and (0 <= green <= 255) and (0 <= blue <= 255):
            encoded_img = generate_img(width, height, red, green, blue)
            return StreamingResponse(io.BytesIO(encoded_img.tobytes()), media_type='image/png') 
        else:
            raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
                                detail="Range of valid values is between [0, 255]")
    else:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="There is one error with your request. Try again")
