import os
import uuid
from multiprocessing.pool import ThreadPool

import uvicorn
from fastapi import FastAPI, File, HTTPException, status

import video_generation as video_generation

pool = ThreadPool(processes=2)
app = FastAPI()


@app.post("/video-attention")
def video_attention(video: bytes = File()):
    file_id = str(uuid.uuid4())
    pool.apply_async(lambda: start_processing(video, file_id))
    return {
        'file_id:': file_id
    }


@app.get('/video-status')
def check_video_status(file_id: str):
    if not os.path.exists('./output-{id}'.format(id=file_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'File not found',
        )
    else:
        if not os.path.exists('./output-{id}/video.mp4'.format(id=file_id)):
            return {
                'status': 'Processing'
            }
        else:
            return {
                'message': 'Done'
            }


def start_processing(video, file_uuid):
    print("Starting processing")
    temp_filename = file_uuid + '.mp4'
    with open(temp_filename, 'wb+') as temp:
        temp.write(video)
    temp.close()

    args_str = '--pretrained_weights dino_deitsmall8_pretrain.pth ' \
               '--input_path {file_path} --output_path output-{uuid}/'.format(
        file_path=temp.name, uuid=file_uuid)
    args = video_generation.parse_args(args_str)

    vg = video_generation.VideoGenerator(args)

    print('Running video generation')
    vg.run()

    with open(temp.name, 'rb') as f:
        result = f.read()
    os.remove(temp_filename)
    return result


if __name__ == '__main__':
    uvicorn.run(app)
