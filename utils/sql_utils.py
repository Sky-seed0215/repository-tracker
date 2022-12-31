import os
import psycopg2
from psycopg2 import Error
from typing import Tuple

from local.key import user, pwd, host, port, db

class DuplicateKeyException(Exception):
    pass

class InputValueNotFound(Exception):
    pass

class DBConnection:
    def __getconnection():
        __DSN = 'postgresql://{user}:{password}@{host}:{port}/{dbname}'.format(
            user=user,
            password=pwd,
            host=host,
            port=port,
            dbname=db
        )

        connection =  psycopg2.connect(__DSN)

        return connection

    def __init__(self, autocommit: bool = True) -> None:
        self.conn = DBConnection.__getconnection()
        self.autocommit = autocommit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.autocommit:
            self.conn.commit()
        self.conn.close()

    def load_data_sql(self, sql: str, data):
        cursor = self.conn.cursor()
        cursor.execute(sql, data)
        result = cursor.fetchall()
        cursor.close()
        return result

    def table_update_sql(self, sql: str, data):
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, data)
        finally:
            cursor.close()

class User:
    def __init__(self, discord_id: int, prefix: str, owner: str, repo: str):
        self.discord_id = discord_id
        self.prefix = prefix
        self.owner = owner
        self.repo = repo

    def get_all_repos(*, discord_id: int):
        with DBConnection(autocommit=False) as db:
            data = db.load_data_sql(
                sql = """
                select prefix, owner, repo from "User".users where discord_id=%s
                """,
                data = (discord_id,)
            )
            return [User(discord_id, v[0], v[1], v[2]) for v in data]

    def get_repo(*, discord_id: int, prefix: str):
        with DBConnection(autocommit=False) as db:
            try:
                data = db.load_data_sql(
                        sql="""
                        select prefix, owner, repo from "User".users where discord_id=%s and prefix=%s
                        """,
                        data=(discord_id, prefix)
                    )
                result = User(discord_id, data[0][0], data[0][1], data[0][2])

                return result
            except IndexError:
                raise IndexError('Repository not found for prefix entered.')

    def insert_repo(*, discord_id: int, prefix: str, owner: str, repo: str):
        with DBConnection() as db:
            try:
                db.table_update_sql(
                    sql="""
                    insert into "User".users (discord_id, prefix, owner, repo) values (%s, %s, %s, %s)
                    """,
                    data=(discord_id, prefix, owner, repo)
                )
            except:
                raise DuplicateKeyException()

    def remove_repo(*, discord_id: int, prefix: str):
        with DBConnection() as db:
            db.table_update_sql(
                sql="""
                delete from "User".users where discord_id=%s and prefix=%s
                """,
                data=(discord_id, prefix)
            )

    def remove_all(*, discord_id: int):
        with DBConnection() as db:
            db.table_update_sql(
                sql="""
                delete from "User".users where discord_id=%s
                """,
                data=(discord_id,)
            )
