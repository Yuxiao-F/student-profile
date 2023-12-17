import pymysql


class LoginResource:

    def __int__(self):
        pass

    @staticmethod
    def get_connection():
        conn = pymysql.connect(
            # LOCAL
            host="localhost",
            port=3306,
            user="root",
            password="Fyx44243774",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True

            # AWS
            # host="customerdb.cvjaygaiwg1r.us-east-1.rds.amazonaws.com",
            # port=3306,
            # user="admin",
            # password="dbuserdbuser",
            # cursorclass=pymysql.cursors.DictCursor,
            # autocommit=True
        )

        return conn

    @staticmethod
    def get_user_by_uni(key):
        sql = "SELECT uni, password FROM student_profile.login_info WHERE uni=%s"
        conn = LoginResource.get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=key)
        result = cur.fetchone()

        return result

    @staticmethod
    def create_account(account):
        placeholder = ", ".join(["%s"] * len(account))
        sql = "INSERT INTO customerDB.account({columns}) VALUES ({values})".format(columns=",".join(account.keys()),
                                                                                   values=placeholder)
        conn = LoginResource.get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, list(account.values()))
        result = cur.fetchone()

        return result

