import io
import os
from fastapi import APIRouter, Form, Query, Request, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from fastapi import File, UploadFile

from saw import SAW

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def view_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "name": " & Welcome Back To Electre !"})

@router.get("/upload", response_class=HTMLResponse)
async def view_upload(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})

UPLOAD_DIR = "upload"
@router.post("/post-upload")
async def upload_data(file: UploadFile = File(...)):
        try:
            if file.content_type != "text/csv":
                raise HTTPException(status_code=400, detail="File type not supported")
            if not os.path.exists(UPLOAD_DIR):
                os.makedirs(UPLOAD_DIR)

            # Menyimpan file ke direktori yang ditentukan
            with open(os.path.join(UPLOAD_DIR, file.filename), "wb") as buffer:
                contents = await file.read()  # baca file
                buffer.write(contents)

            files = []
            if os.path.exists(UPLOAD_DIR):
                files = os.listdir(UPLOAD_DIR)
            
            return {
                "error": "",
                "status": True,
                "data": files
            }
    
        except HTTPException as e:
            return {
                "error": e.detail,
                "status": False,
                "data": []
            }

@router.get("/calculate", response_class=HTMLResponse)
async def view_home(request: Request):
    files = None
    if os.path.exists(UPLOAD_DIR):
        files = os.listdir(UPLOAD_DIR)
    return templates.TemplateResponse("calculate.html", {"request": request, "files":files, "error":""})

@router.post("/post-calculate", response_class=HTMLResponse)
async def train_result(
    request: Request,
    selectedFile: str = Form(...),
    weights: str = Form(...),
    benefit: str = Form(...),
):
    filename = f'./upload/{selectedFile}'
    df = pd.read_csv(filename)
    # selected_columns = ['K1', 'K2', 'K3', 'K4', 'K5']
    kolom_tidak_berguna = 'ID'

    # Menghapus kolom yang tidak berguna
    df_filtered = df.drop(columns=[kolom_tidak_berguna])
    # df_filtered = df[selected_columns]

    # Mengonversi DataFrame menjadi matriks
    data_matrix = df_filtered.values.tolist()
    weight_matrix = [float(item.strip()) for item in weights.split(',')]
    benefit_matrix = [bool(int(item.strip())) for item in benefit.split(',')]
    weight_size = len(weight_matrix)
    benefit_size = len(benefit_matrix)
    colomn_size = len(data_matrix[0])
    if(weight_size == colomn_size == benefit_size):
        s = SAW()
        normalized_matrix, weighted_normalized_matrix, scores = s.start(data_matrix, weight_matrix, benefit_matrix)
        # Menggabungkan skor dengan DataFrame asli
        normalized_df = pd.DataFrame(normalized_matrix, columns=df_filtered.columns)
        normalized_df.insert(0, 'ID', df[kolom_tidak_berguna])
        normalized_df_string = normalized_df.to_csv(index=False)
        df['Score'] = scores
        df_sorted = df.sort_values(by='Score', ascending=False)
        df_sorted['Rank'] = range(1, len(df_sorted) + 1)

        # Menyimpan ke CSV baru
        output_filename = 'hasil_saw.csv'
        csv_string = df_sorted.to_csv(index=False)
        df_sorted.to_csv(f'./static/result/{output_filename}', index=False)
        return templates.TemplateResponse(
            "results.html", {"request": request, "csv_data": csv_string, "normalize":normalized_df_string, "path":f'/static/result/{output_filename}', "router": router}
        )
    else:
        files = None
        if os.path.exists(UPLOAD_DIR):
            files = os.listdir(UPLOAD_DIR)
        return templates.TemplateResponse("calculate.html", {"request": request, "files":files, "error":"Jumlah kriteria & bobot tidak sama !"})
    

@router.get("/download-csv")
async def download_csv(
     request: Request,
     output_filename: str = Query(..., alias="output_filename")
):
    file_path = f'.{output_filename}'
    name = "result"
    # Membaca file CSV sebagai bytes
    with open(file_path, "rb") as file:
        csv_bytes = file.read()

    # Menanggapi unduhan dengan menggunakan StreamingResponse
    return StreamingResponse(io.BytesIO(csv_bytes), media_type="text/csv", headers={"Content-Disposition": f'attachment; filename="{output_filename}"'})


