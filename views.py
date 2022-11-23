import os
import tempfile
import uuid

import uvicorn
from fastapi import FastAPI, Body, File

app = FastAPI()


@app.post("/video-attention")
def video_attention(video: bytes = File()):
    temp_filename = str(uuid.uuid4()) + '.mp4'
    with open(temp_filename, 'wb+') as temp:
        temp.write(video)
    temp.close()
    command = os.system(
        'python video_generation.py  --pretrained_weights dino_deitsmall8_pretrain.pth --input_path {path} --output_path output/'.format(
            path=temp.name))
    with open('output/' + temp.name, 'rb') as f:
        result = f.read()
    os.remove(temp_filename)
    return result


if __name__ == '__main__':
    uvicorn.run(app)
