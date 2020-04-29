# -*- coding: utf-8 -*-
"""
Created on Sun Jul 15 00:01:50 2018

@author: Administrator
"""
import pandas as pd
import pymysql

config =  {'user': 'root',
          'password': '123456',
          'port':3300,
          'host': '127.0.0.1',
          'db': 'Book',
          'charset':'utf8'}


class BookSqlTools:
    #链接MYSQL数据库
    #读取出来转化成pandas的dataframe格式

    def LinkMysql(self, sql):
        try:
            connection = pymysql.connect(user=config['user'],
                                          password=config['password'],
                                          port=config['port'],
                                          host=config['host'],
                                          db=config['db'],
                                          charset=config['charset'])
            cur = connection.cursor()
            
        except Exception as e:
            print("Mysql link fail：%s" % e)
        try:
            cur.execute(sql)
            
        except Exception as e:
            print("dont do execute sql")
        try:
            result1 = cur.fetchall()
            title1 = [i[0] for i in cur.description]
            Main = pd.DataFrame(result1)
            Main.columns = title1
            
        except Exception as e:
            print(" select Mysql error：{}".format(e))
        return Main
    

    #数据库中的表插入数据
    def UpdateMysqlTable(self, data, sql_qingli, sql_insert):
        try:
            connection = pymysql.connect(user=config['user'],
                                          password=config['password'],
                                          port=config['port'],
                                          host=config['host'],
                                          db=config['db'],
                                          charset=config['charset'])
            cursor = connection.cursor()
            
        except Exception as e:
            print("Mysql link fail：%s" % e)
        try:
            cursor.execute(sql_qingli)
        except:
            print("dont do created table sql")
        try:
            datas = data.to_dict(orient='records')
            for data in datas:
                x = list(data.values())
                sql = sql_insert.format(tuple(x)).encode(encoding='utf-8')
                print(sql)
                try:
                    cursor.execute(sql)
                except Exception as e:
                    print("Mysql insert fail%s" % e)
        except Exception as e:
            connection.rollback()
            print("Mysql insert fail%s" % e)
        connection.commit()
        cursor.close()
        connection.close()




connection = pymysql.connect(user=config['user'],
                          password=config['password'],
                          port=config['port'],
                          host=config['host'],
                          charset=config['charset'])

cur = connection.cursor()
cur.execute('DROP DATABASE if exists Book')
cur.execute('CREATE DATABASE if not exists Book')
connection.commit()
cur.close()
# 创建购物车表

connection = pymysql.connect(user=config['user'],
                          password=config['password'],
                          port=config['port'],
                          host=config['host'],
                          db=config['db'],
                          charset=config['charset'])

cur = connection.cursor()
createCartSql = '''CREATE TABLE Cart         
               (UserID                 VARCHAR(100)   ,
                BookID                VARCHAR(100) )'''
cur.execute(createCartSql)
connection.commit()
cur.close()
connection.close()


BookInfoInsert = BookSqlTools()
#--------------------------------------------------------------------------
#读取本地的BX-Users.csv文件  在数据库中建一个User表   将User.csv内容插入到数据库中
#--------------------------------------------------------------------------
path = './data/BX-Users.csv'
User = pd.read_csv(path, sep=None, error_bad_lines=False)

createUserSql = '''CREATE TABLE User         
               (UserID                 VARCHAR(100)   ,
               Location                VARCHAR(100)  , 
                 Age                    VARCHAR(100) );'''

UserSql_insert='insert into User (UserID,Location,Age) values {}'

BookInfoInsert.UpdateMysqlTable(User,createUserSql,UserSql_insert)
del User
#--------------------------------------------------------------------------
#读取本地的BX-Books.csv文件  在数据库中建一个Books表   将book.csv内容插入到数据库中
#--------------------------------------------------------------------------

path = './data/BX-Books.csv'
Book = pd.read_csv(path, sep=None, error_bad_lines=False)

createBooksSql =''' CREATE TABLE Books         
               (BookID                   VARCHAR(999) ,
                BookTitle                VARCHAR(999) ,
                BookAuthor               VARCHAR(999) ,
                PubilcationYear          VARCHAR(999) ,
                Publisher                VARCHAR(999) ,
                ImageS                   VARCHAR(999) ,
                ImageM                   VARCHAR(999) ,
                ImageL                   VARCHAR(999));'''

BooksSql_insert='insert into Books (BookID,BookTitle,BookAuthor,PubilcationYear,Publisher,ImageS,ImageM,ImageL) values {}'

BookInfoInsert.UpdateMysqlTable(Book,createBooksSql,BooksSql_insert)
del Book

#--------------------------------------------------------------------------
#读取本地的BX-Book-Ratings文件  在数据库中建一个Bookrating表   将bookrating.csv内容插入到数据库中
#--------------------------------------------------------------------------

path = './data/BX-Book-Ratings.csv'
Rating = pd.read_csv(path, sep=None, error_bad_lines=False)

createBookratingSql = '''CREATE TABLE Bookrating        
               (UserID                VARCHAR(999) ,
                BookID                VARCHAR(999) ,
                Rating                VARCHAR(999));'''          

BookratingSql_insert='insert into Bookrating (UserID,BookID,Rating) values {}'

BookInfoInsert.UpdateMysqlTable(Rating,createBookratingSql,BookratingSql_insert)
del Rating
#--------------------------------------------------------------------------
#读取本地的Booktuijian.csv文件  在数据库中建一个Booktuijian表   将Booktuijian.csv内容插入到数据库中
#--------------------------------------------------------------------------

Booktuijian = pd.read_csv('data/booktuijian.csv')
Booktuijian['score'] = Booktuijian['score'].apply(lambda x: round(x,2))
Booktuijian['score'] = 10*(Booktuijian['score'])/(max(Booktuijian['score']))

Booktuijian=Booktuijian[['BookID','UserID','score']]

createBookrecomql = '''CREATE TABLE Booktuijian        
               (UserID                    VARCHAR(999) ,
                BookID                    VARCHAR(999) ,
                score                     FLOAT(5,3)  );'''  

BooktuijianSql_insert='insert into Booktuijian (BookID,UserID,score) values {}'

BookInfoInsert.UpdateMysqlTable(Booktuijian,createBookrecomql ,BooktuijianSql_insert)


