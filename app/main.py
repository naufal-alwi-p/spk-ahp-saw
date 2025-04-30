from fastapi import FastAPI, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import get_session
from model.database_model import Kriteria, Perbandingan_Kriteria, Opsi_Kriteria, Karyawan, Skor_Karyawan
from model.form_model import FormPerbandinganKriteria, FormKaryawan
from typing import Annotated
from ahp_saw_model import DecisionSupportSystem

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.mount("/static", StaticFiles(directory="app/interface/static"), "assets")

templates = Jinja2Templates(directory="app/interface/templates")

spk_model = DecisionSupportSystem()

SessionDatabase = Annotated[Session, Depends(get_session)]

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
    )

@app.get("/perbandingan-kriteria", response_class=HTMLResponse)
def perbandingan_kriteria_page(request: Request, session: SessionDatabase):
    try:
        perbandingan_kriteria = session.exec(select(Perbandingan_Kriteria)).all()
    except:
        raise HTTPException(500, detail="Internal Server Error")

    return templates.TemplateResponse(
        request=request,
        name="perbandingan_kriteria.html",
        context={"perbandingan_kriteria": perbandingan_kriteria}
    )

@app.post("/perbandingan-kriteria")
def perbandingan_kriteria_handler(request: Request, session: SessionDatabase, formData: Annotated[FormPerbandinganKriteria, Form()]):
    try:
        perbandingan_kriteria = session.exec(select(Perbandingan_Kriteria)).all()
    except:
        raise HTTPException(500, detail="Internal Server Error")
    
    if len(formData.id) != len(perbandingan_kriteria):
        raise HTTPException(500, detail="Internal Server Error")

    is_commit = False

    for i in range(len(perbandingan_kriteria)):
        is_add = False
        if (perbandingan_kriteria[i].nilai_kriteria1 != formData.nilai_kriteria1[i]):
            perbandingan_kriteria[i].nilai_kriteria1 = formData.nilai_kriteria1[i]
            is_add = True
        
        if (perbandingan_kriteria[i].nilai_kriteria2 != formData.nilai_kriteria2[i]):
            perbandingan_kriteria[i].nilai_kriteria2 = formData.nilai_kriteria2[i]
            is_add = True
        
        if is_add:
            session.add(perbandingan_kriteria[i])
            is_commit = True
    
    if is_commit:
        session.commit()
    
    spk_model.get_comparison_matrix()
    spk_model.calculate_consistency_ratio()
    
    return RedirectResponse(
        url=str(request.base_url) + "perbandingan-kriteria",
        status_code=303
    )

@app.get("/karyawan", response_class=HTMLResponse)
def karyawan_page(request: Request, session: SessionDatabase):
    if (spk_model.cr >= 0.1):
        return RedirectResponse(
            url=str(request.base_url) + "perbandingan-kriteria",
            status_code=302
        )
    
    try:
        all_karyawan = session.exec(select(Karyawan)).all()
        all_kriteria = session.exec(select(Kriteria)).all()
    except:
        raise HTTPException(500, detail="Internal Server Error")

    return templates.TemplateResponse(
        request=request,
        name="karyawan.html",
        context={
            "all_karyawan": enumerate(all_karyawan),
            "all_kriteria": all_kriteria
        }
    )

@app.get("/tambah-karyawan")
def tambah_karyawan_page(request: Request, session: SessionDatabase):
    if (spk_model.cr >= 0.1):
        return RedirectResponse(
            url=str(request.base_url) + "perbandingan-kriteria",
            status_code=302
        )
    
    try:
        all_kriteria = session.exec(select(Kriteria)).all()
    except:
        raise HTTPException(500, detail="Internal Server Error")
    return templates.TemplateResponse(
        request=request,
        name="tambah_karyawan.html",
        context={
            "all_kriteria": enumerate(all_kriteria)
        }
    )

@app.post("/tambah-karyawan")
def tambah_karyawan_handler(request: Request ,session: SessionDatabase, formData: Annotated[FormKaryawan, Form()]):
    if (spk_model.cr >= 0.1):
        return RedirectResponse(
            url=str(request.base_url) + "perbandingan-kriteria",
            status_code=302
        )
    
    try:
        golongan = session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria1).where(Opsi_Kriteria.opsi == formData.opsi_kriteria1)).one()
        eselon = session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria2).where(Opsi_Kriteria.opsi == formData.opsi_kriteria2)).one()
        jabatan = session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria3).where(Opsi_Kriteria.opsi == formData.opsi_kriteria3)).one()
        pendidikan = session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria4).where(Opsi_Kriteria.opsi == formData.opsi_kriteria4)).one()

        data_karyawan = Karyawan(nama=formData.nama)

        session.add(data_karyawan)
        session.commit()
        session.refresh(data_karyawan)

        session.add(Skor_Karyawan(karyawan=data_karyawan, opsi_kriteria=golongan, id_kriteria=golongan.id_kriteria))
        session.add(Skor_Karyawan(karyawan=data_karyawan, opsi_kriteria=eselon, id_kriteria=eselon.id_kriteria))
        session.add(Skor_Karyawan(karyawan=data_karyawan, opsi_kriteria=jabatan, id_kriteria=jabatan.id_kriteria))
        session.add(Skor_Karyawan(karyawan=data_karyawan, opsi_kriteria=pendidikan, id_kriteria=pendidikan.id_kriteria))

        session.commit()
    except:
        raise HTTPException(422, detail="Unprocessable Content")
    
    spk_model.get_decision_matrix()
    
    return RedirectResponse(
        url=str(request.base_url) + "karyawan",
        status_code=303
    )

@app.get("/edit-karyawan/{id}")
def update_karyawan_page(request: Request, id: int, session: SessionDatabase):
    if (spk_model.cr >= 0.1):
        return RedirectResponse(
            url=str(request.base_url) + "perbandingan-kriteria",
            status_code=302
        )
    
    try:
        karyawan = session.exec(select(Karyawan).where(Karyawan.id == id)).one()
        all_kriteria = session.exec(select(Kriteria)).all()
    except:
        raise HTTPException(404, detail="Not Found")
    
    return templates.TemplateResponse(
        request=request,
        name="edit_karyawan.html",
        context={
            "karyawan": karyawan,
            "all_kriteria": enumerate(all_kriteria)
        }
    )

@app.post("/edit-karyawan/{id}")
def update_karyawan_handler(request: Request, id: int, session: SessionDatabase, formData: Annotated[FormKaryawan, Form()]):
    if (spk_model.cr >= 0.1):
        return RedirectResponse(
            url=str(request.base_url) + "perbandingan-kriteria",
            status_code=302
        )
    
    try:
        opsi_kriteria = [
            session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria1).where(Opsi_Kriteria.opsi == formData.opsi_kriteria1)).one(),
            session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria2).where(Opsi_Kriteria.opsi == formData.opsi_kriteria2)).one(),
            session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria3).where(Opsi_Kriteria.opsi == formData.opsi_kriteria3)).one(),
            session.exec(select(Opsi_Kriteria).where(Opsi_Kriteria.id_kriteria == formData.kriteria4).where(Opsi_Kriteria.opsi == formData.opsi_kriteria4)).one(),
        ]
    except:
        raise HTTPException(422, detail="Unprocessable Content")
    
    try:
        data_karyawan = session.exec(select(Karyawan).where(Karyawan.id == id)).one()

        if data_karyawan.nama != formData.nama:
            data_karyawan.nama = formData.nama
            session.add(data_karyawan)
            session.commit()
            session.refresh(data_karyawan)
    except:
        raise HTTPException(404, detail="Not Found")
    
    try:
        skor_karyawan = data_karyawan.skor_karyawan
        dict_fromData = formData.model_dump()
        is_change = False

        for i in range(len(skor_karyawan)):
            if (skor_karyawan[i].id_kriteria == dict_fromData['kriteria' + str(i + 1)]):
                if (skor_karyawan[i].id_opsi != opsi_kriteria[i].id):
                    skor_karyawan[i].id_opsi = opsi_kriteria[i].id
                    session.add(skor_karyawan[i])
                    is_change = True
            else:
                raise HTTPException(422, detail="Unprocessable Content")
        
        if is_change:
            session.commit()
    except:
        raise HTTPException(422, detail="Unprocessable Content")
    
    spk_model.get_decision_matrix()
    
    return RedirectResponse(
        url=str(request.base_url) + "karyawan",
        status_code=303
    )

@app.post("/hapus-karyawan/{id}")
def hapus_karyawan(request: Request, id: int, session: SessionDatabase):
    if (spk_model.cr >= 0.1):
        return RedirectResponse(
            url=str(request.base_url) + "perbandingan-kriteria",
            status_code=302
        )
    
    try:
        data_karyawan = session.exec(select(Karyawan).where(Karyawan.id == id)).one()

        session.delete(data_karyawan)
        session.commit()
    except:
        raise HTTPException(404, detail="Not Found")
    
    spk_model.get_decision_matrix()
    
    return RedirectResponse(
        url=str(request.base_url) + "karyawan",
        status_code=303
    )

@app.get("/hasil")
def hasil_page(request: Request):
    if (spk_model.cr >= 0.1):
        return RedirectResponse(
            url=str(request.base_url) + "perbandingan-kriteria",
            status_code=302
        )

    if (len(spk_model.names) < 1):
        return RedirectResponse(
            url=str(request.base_url) + "karyawan"
        )

    return templates.TemplateResponse(
        request=request,
        name="hasil.html",
        context={
            "score": spk_model.evaluate()
        }
    )
