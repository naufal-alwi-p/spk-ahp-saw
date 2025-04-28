import os

from sqlalchemy.engine.url import URL
from sqlmodel import create_engine, SQLModel, Session

import model.database_model

database_url = URL.create(
    drivername='mysql+pymysql',
    host="127.0.0.1",
    port=3306,
    username="root",
    password=None,
    database="sistem_spk"
)

engine = create_engine(database_url, echo=True if __name__ == "__main__" else False)

def migration():
    SQLModel.metadata.create_all(engine)

def init_data():
    with Session(engine) as session:
        golongan = model.database_model.Kriteria(nama="Golongan")
        eselon_terakhir = model.database_model.Kriteria(nama="Eselon Terakhir")
        jabatan_terakhir = model.database_model.Kriteria(nama="Jabatan Terakhir")
        pendidikan_terakhir = model.database_model.Kriteria(nama="Pendidikan Terakhir")

        opsi_golongan = [
            "Tidak Punya Golongan",
            "I/a - I/d",
            "II/a - II/d",
            "III/a - III/d",
            "IV/a - IV/e"
        ]

        opsi_eselon = [
            "Tidak Punya Eselon",
            "Eselon IV",
            "Eselon III",
            "Eselon II",
            "Eselon I"
        ]

        opsi_jabatan = [
            "Tidak Punya Jabatan",
            "Staff",
            "Ka. Seksi",
            "Ka. Bidang",
            "Ka. Subbag",
            "Sekretaris"
        ]

        opsi_pendidikan = [
            "SMA",
            "D3 - Sederajat",
            "S1 - Sederajat",
            "S2"
        ]

        session.add(golongan)
        session.add(eselon_terakhir)
        session.add(jabatan_terakhir)
        session.add(pendidikan_terakhir)

        session.add(model.database_model.Perbandingan_Kriteria(kriteria_1=golongan, nilai_kriteria1=1, kriteria_2=eselon_terakhir, nilai_kriteria2=2))
        session.add(model.database_model.Perbandingan_Kriteria(kriteria_1=golongan, nilai_kriteria1=1, kriteria_2=jabatan_terakhir, nilai_kriteria2=5))
        session.add(model.database_model.Perbandingan_Kriteria(kriteria_1=golongan, nilai_kriteria1=1, kriteria_2=pendidikan_terakhir, nilai_kriteria2=4))
        session.add(model.database_model.Perbandingan_Kriteria(kriteria_1=eselon_terakhir, nilai_kriteria1=1, kriteria_2=jabatan_terakhir, nilai_kriteria2=2))
        session.add(model.database_model.Perbandingan_Kriteria(kriteria_1=eselon_terakhir, nilai_kriteria1=1, kriteria_2=pendidikan_terakhir, nilai_kriteria2=4))
        session.add(model.database_model.Perbandingan_Kriteria(kriteria_1=jabatan_terakhir, nilai_kriteria1=1, kriteria_2=pendidikan_terakhir, nilai_kriteria2=2))

        list_length = len(opsi_golongan)
        for i in range(list_length):
            session.add(model.database_model.Opsi_Kriteria(kriteria=golongan, opsi=opsi_golongan[i], bobot=round(i/(list_length - 1), 2)))
        
        list_length = len(opsi_eselon)
        for i in range(list_length):
            session.add(model.database_model.Opsi_Kriteria(kriteria=eselon_terakhir, opsi=opsi_eselon[i], bobot=round(i/(list_length - 1), 2)))

        list_length = len(opsi_jabatan)
        for i in range(list_length):
            session.add(model.database_model.Opsi_Kriteria(kriteria=jabatan_terakhir, opsi=opsi_jabatan[i], bobot=round(i/(list_length - 1), 2)))
        
        list_length = len(opsi_pendidikan)
        for i in range(list_length):
            session.add(model.database_model.Opsi_Kriteria(kriteria=pendidikan_terakhir, opsi=opsi_pendidikan[i], bobot=round(i/(list_length - 1), 2)))
        
        session.commit()

def get_session():
    with Session(engine) as session:
        yield session

if __name__ == "__main__":
    migration()
    init_data()
