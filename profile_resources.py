import pymysql


class ProfileResource:

    def __int__(self):
        pass

    @staticmethod
    def get_connection():
        conn = pymysql.connect(
            # LOCAL
            host="localhost",
            port=3306,
            user="root",
            password="dbuserdbuser",
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
    def get_profile_by_uni(key):
        sql = "SELECT uni, name, interest, schedule, email FROM student_profile.student_info WHERE uni=%s"
        conn = ProfileResource.get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=key)
        result = cur.fetchone()

        return result

    @staticmethod
    def delete_profile_by_uni(key):
        sql = "DELETE FROM student_profile.student_info WHERE uni=%s"
        conn = ProfileResource.get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, args=key)
        result = cur.fetchone()

        return result

    @staticmethod
    def create_account(new_account):
        # placeholder = ", ".join(["%s"] * len(new_account))
        # sql = "INSERT INTO student_profile.student_info({columns}) VALUES ({values})".format(columns=",".join(new_account.keys()),
        #                                                                            values=placeholder)
        sql = "INSERT INTO student_profile.student_info(uni, name, interest, schedule, email) VALUES (%s, %s, %s, %s, %s)"
        conn = ProfileResource.get_connection()
        cur = conn.cursor()
        # res = cur.execute(sql, list(new_account.values()))
        res = cur.execute(sql, (new_account[0], new_account[1], new_account[2], new_account[3], new_account[4]))
        result = cur.fetchone()

        return result
    #
    @staticmethod
    def update_account(new_content):
        sql = "UPDATE student_profile.student_info SET interest=%s, schedule=%s where uni=%s"
        conn = ProfileResource.get_connection()
        cur = conn.cursor()
        res = cur.execute(sql, (new_content[1], new_content[2], new_content[0]))
        result = cur.fetchone()
        return result
