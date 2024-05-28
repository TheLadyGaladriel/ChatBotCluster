import sqlite3
import numpy as np
from sklearn.neighbors import NearestNeighbors


class TrainerClusterer:
    def __init__(self, db_file):
        self.db_file = db_file
        self.neigh = None
        self.trainer_responses = []
        self.trainer_ids = []

    def load_trainer_responses(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT trainer_id, a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11, a12, a13, a14, a15 FROM trainer_responses"
        )
        rows = cursor.fetchall()
        conn.close()
        self.trainer_ids = [row[0] for row in rows]
        self.trainer_responses = [row[1:] for row in rows]

    def train_model(self):
        self.load_trainer_responses()
        self.neigh = NearestNeighbors(n_neighbors=1).fit(self.trainer_responses)

    def predict_trainer(self, user_responses):
        if self.neigh is None:
            raise Exception("Модель не обучена. Пожалуйста, сначала обучите модель.")
        distances, indices = self.neigh.kneighbors([user_responses])
        closest_trainer_index = indices[0][0]
        return self.trainer_ids[closest_trainer_index]

    def get_trainer_name(self, trainer_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM trainer_responses WHERE trainer_id=?", (trainer_id,)
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]
        else:
            return None
