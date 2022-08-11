import pymysql
import get_images

class Database:
    def __enter__(self):
        self.__connection = pymysql.connect(
            **CONFIG["mysql"]
        )
        return self

    def __exit__(self, type, value, traceback):
        self.__connection.commit()
        self.__connection.close()

    def append_black