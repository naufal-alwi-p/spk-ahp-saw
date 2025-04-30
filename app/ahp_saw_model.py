import numpy as np
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from database import engine
from model.database_model import Kriteria, Perbandingan_Kriteria, Karyawan, Skor_Karyawan

class DecisionSupportSystem:
    def __init__(self):
        self.matrix = None
        self.n = None
        self.normalized_matrix = None
        self.priority_vector = None
        self.lambda_max = None
        self.ci = None
        self.ri = None
        self.cr = None

        self.decision_matrix = None
        self.text_decision_matrix = None
        self.saw_normalized_matrix = None

        self.names = None

        self.get_comparison_matrix()
        self.get_decision_matrix()

        self.calculate_consistency_ratio()
    
    # AHP
    def get_comparison_matrix(self, kriteria: list[Kriteria] = None, perbandingan_kriteria: list[Perbandingan_Kriteria] = None):
        if kriteria == None or perbandingan_kriteria == None:
            with Session(engine) as session:
                kriteria = session.exec(select(Kriteria)).all()
                perbandingan_kriteria = session.exec(select(Perbandingan_Kriteria)).all()
        
        self.matrix = np.zeros((len(kriteria), len(kriteria)), dtype=float)
        self.n = self.matrix.shape[0]

        np.fill_diagonal(self.matrix, 1)

        index = 0

        for i in range(0, len(kriteria) - 1):
            for j in range(1 + i, len(kriteria)):
                self.matrix[i][j] = perbandingan_kriteria[index].nilai_kriteria1 / perbandingan_kriteria[index].nilai_kriteria2
                self.matrix[j][i] = perbandingan_kriteria[index].nilai_kriteria2 / perbandingan_kriteria[index].nilai_kriteria1

                index += 1
                
        return self.matrix

    def ahp_normalize_matrix(self):
        col_sums = self.matrix.sum(axis=0)
        self.normalized_matrix = self.matrix / col_sums
        return self.normalized_matrix

    def calculate_priority_vector(self):
        self.ahp_normalize_matrix()
        self.priority_vector = self.normalized_matrix.mean(axis=1)
        return self.priority_vector

    def calculate_consistency_ratio(self):
        self.calculate_priority_vector()
        weighted_sum = self.matrix @ self.priority_vector
        self.lambda_max = np.mean(weighted_sum / self.priority_vector)
        self.ci = (self.lambda_max - self.n) / (self.n - 1)
        ri_values = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
        self.ri = ri_values.get(self.n, 1.49)
        self.cr = self.ci / self.ri
        return self.cr
    
    # SAW
    def get_decision_matrix(self, kriteria: list[Kriteria] = None, karyawan: list[Karyawan] = None, skor_karyawan: list[Skor_Karyawan] = None):
        if kriteria == None or karyawan == None or skor_karyawan == None:
            with Session(engine) as session:
                kriteria = session.exec(select(Kriteria)).all()
                karyawan = session.exec(select(Karyawan)).all()
                skor_karyawan = session.exec(select(Skor_Karyawan).options(selectinload(Skor_Karyawan.opsi_kriteria))).all()
        
        skor_karyawan = sorted(skor_karyawan, key=lambda nilai_karyawan: (nilai_karyawan.id_karyawan, nilai_karyawan.id_kriteria))
        
        self.decision_matrix = np.zeros((len(karyawan), len(kriteria)), dtype=float)
        self.text_decision_matrix = [["" for _ in range(len(kriteria))] for _ in range(len(karyawan))]

        index = 0

        self.names = [data_karyawan.nama for data_karyawan in karyawan]

        for i in range(len(karyawan)):
            for j in range(len(kriteria)):
                self.decision_matrix[i][j] = skor_karyawan[index].opsi_kriteria.bobot
                self.text_decision_matrix[i][j] = skor_karyawan[index].opsi_kriteria.opsi

                index += 1

        cols_all_zero = np.all(self.decision_matrix == 0, axis=0)

        for i, is_zero in enumerate(cols_all_zero):
            if is_zero:
                self.decision_matrix[:, i] = 0.001

    def saw_normalize_matrix(self):
        max_values = self.decision_matrix.max(axis=0)
        self.saw_normalized_matrix = self.decision_matrix / max_values
        return self.saw_normalized_matrix

    def rank_alternatives(self):
        self.saw_normalize_matrix()
        scores = self.saw_normalized_matrix @ np.array(self.priority_vector)
        return scores
    
    def evaluate(self):
        self.cr = self.calculate_consistency_ratio()
        if self.cr >= 0.1:
            raise ValueError("Consistency Ratio (CR) too high. Reassess the pairwise comparison.")
        scores = np.round(self.rank_alternatives(), 2)
        ranked = sorted(zip(self.names, scores), key=lambda x: x[1], reverse=True)
        return ranked
