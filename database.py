import mysql.connector

class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        return mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )

    def run_query(self, query):    
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(query)
            res = cursor.fetchone()
            media_status_count = cursor.rowcount

            if media_status_count > 0:
                response = res[1]
            else: 
                response = None
            return response
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return None
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def getStatusMedia(self, emo_id):
        query = f"SELECT emotion_src, emotion_media, emotion_datetime FROM emotions WHERE emotion_src='{emo_id}'"
        return self.run_query(query)

    def insertDB(self, emo_src, emo_med, emo_data, emo_status, emo_datetime):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO emotions (emotion_src, emotion_media, emotion_data, emotion_status, emotion_datetime) VALUES (%s, %s, %s, %s, %s)",
                (emo_src, emo_med, emo_data, emo_status, emo_datetime)
            )
            connection.commit()
            return 1
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return 0
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def getStatusID(self, emo_id):
        query = f"SELECT emotion_src, emotion_status, emotion_datetime FROM emotions WHERE emotion_src='{emo_id}'"
        return self.run_query(query)

    def getStatusData(self, emo_id):
        query = f"SELECT emotion_src, emotion_data, emotion_datetime FROM emotions WHERE emotion_src='{emo_id}'"
        return self.run_query(query)

    def updateStatus(self, stat, emo_id):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = f"UPDATE emotions SET emotion_status='{str(stat)}' WHERE emotion_src='{str(emo_id)}'"
            cursor.execute(query)
            connection.commit()
            return 1
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return 0
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def updateData(self, data, emo_id):
        try:
            connection = self.connect()
            cursor = connection.cursor()
            query = f"UPDATE emotions SET emotion_data='{data}' WHERE emotion_src='{emo_id}'"
            cursor.execute(query)
            connection.commit()
            return 1
        except mysql.connector.Error as e:
            print(f"Error: {e}")
            return 0
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
