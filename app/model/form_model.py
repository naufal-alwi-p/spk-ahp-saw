from pydantic import BaseModel
from typing import Literal

class FormPerbandinganKriteria(BaseModel):
    id: list[int]
    id_kriteria1: list[int]
    nilai_kriteria1: list[int]
    id_kriteria2: list[int]
    nilai_kriteria2: list[int]

class FormKaryawan(BaseModel):
    nama: str
    kriteria1: int
    opsi_kriteria1: Literal["Tidak Punya Golongan", "I/a - I/d", "II/a - II/d", "III/a - III/d", "IV/a - IV/e"]
    kriteria2: int
    opsi_kriteria2: Literal["Tidak Punya Eselon", "Eselon IV", "Eselon III", "Eselon II", "Eselon I"]
    kriteria3: int
    opsi_kriteria3: Literal["Tidak Punya Jabatan", "Staff", "Ka. Seksi", "Ka. Bidang", "Ka. Subbag", "Sekretaris"]
    kriteria4: int
    opsi_kriteria4: Literal["SMA", "D3 - Sederajat", "S1 - Sederajat", "S2"]
