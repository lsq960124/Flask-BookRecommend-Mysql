# coding: utf-8 -*-
import math
import pandas as pd

class UserCf:
    # 这个类的主要功能是提供一个基于用户的协调过滤算法接口
    
    def __init__(self):
        self.file_path = './data/BX-Book-Ratings.csv'
        self._init_frame()

    def _init_frame(self):
        self.frame = pd.read_csv(self.file_path,sep=None, error_bad_lines=False)
        self.frame.columns=['UserID','BookID','Rating'] 

    @staticmethod
    def _cosine_sim(target_books, books):
        '''
        simple method for calculate cosine distance.
        e.g: x = [1 0 1 1 0], y = [0 1 1 0 1](x1^2+x2^2+...)+sqrt(y1^2+y2^2+...)]
             cosine = (x1*y1+x2*y2+...) / [sqrt
             that means union_len(movies1, movies2) / sqrt(len(movies1)*len(movies2))
             上面是算法的公式，return的值cosine就是相似度。用到的知识是线性代数求cos角度数。举个列子 空间上面有 2个点A,B。与
             坐标原点（0,0）组成AOB三角形，角AOB的度数越小，那么表示两个坐标点越相近。代入这个书籍推荐上面
             我们这样理解：
             用户A=[‘书1’，‘书2’，‘书3’]=['1','2','3'] ID代表书籍的编号
             用户B=[‘书4’，‘书2’，‘书6’]=['4','2','6'] ID代表书籍的编号
             用户C=[‘书7’，‘书8’，‘书9’]=['21','2','6'] ID代表书籍的编号
             如果用户A登录网址 思考一个问题 我们推荐用户B的书籍，还是用户C的给A？
             求cosAOB = x  cosAOC = y
             很明显 X< Y 那么 证明用户B距离用户A更近，即B的阅读兴趣与A跟相似，于是
             我们可以把B阅读的书籍推荐给A
             我们用这个方法可以得到最相似的用户，但是还得不到最适合推荐的书籍。这个可以在
             get_topn_items这个方法中解决。
        '''
        union_len = len(set(target_books) & set(books))
        if union_len == 0: return 0.0
        product = len(target_books) * len(books)
        cosine = union_len / math.sqrt(product)
        return cosine

    def _get_top_n_users(self, target_user_id, top_n):
        '''
        calculate similarity between all users and return Top N similar users.
        '''
        target_books = self.frame[self.frame['UserID'] == target_user_id]['BookID']
        other_users_id = [i for i in set(self.frame['UserID']) if i != target_user_id]
        other_books = [self.frame[self.frame['UserID'] == i]['BookID'] for i in other_users_id]

        sim_list = [self._cosine_sim(target_books, books) for books in other_books]
        sim_list = sorted(zip(other_users_id, sim_list), key=lambda x: x[1], reverse=True)
        return sim_list[:top_n]

    def _get_candidates_items(self, target_user_id):
        """
        Find all books in source data and target_user did not meet before.
        """
        target_user_books = set(self.frame[self.frame['UserID'] == target_user_id]['BookID'])
        other_user_books = set(self.frame[self.frame['UserID'] != target_user_id]['BookID'])
        candidates_books = list(target_user_books ^ other_user_books)
        return candidates_books

    def _get_top_n_items(self, top_n_users, candidates_books, top_n):
        """
            calculate interest of candidates movies and return top n movies.
            e.g. interest = sum(sim * normalize_rating)
    
            上面2个方法，依靠上面的注释的内容，我们得到了最相似的用户，那么用户中我们需要怎么推荐书籍？
            原理其实很容易理解：
            
            首先我们有全部用户对于不同书籍的评分，那么我们可以计算出每个书籍的平均得分。这个作为一个权重
            再去乘以之前用户的相似度。那么这个值以上面的例子来说
            用户A=[‘书1’，‘书2’，‘书3’]=['1','2','3'] ID代表书籍的编号
            用户B=[‘书4’，‘书2’，‘书6’]=['4','2','6'] ID代表书籍的编号
            用户C=[‘书7’，‘书8’，‘书9’]=['21','2','6'] ID代表书籍的编号
            
            用户A登录, 他阅读了‘书1’，‘书2’，‘书3’，假设数据库只有用户A，用户B，用户C
            发现B,C都与A有共同兴趣，即看过书2，那么我们需要推送4,6,21，我们需要计算4,6,21的
            推荐度，并排序返回给A。
            
            那么怎么计算呢？
            
            首先，我们前面求出了A与B,C的相似度。这个值乘以每本书在书籍评分数据的平均值。这样4，21的是可以直接
            得到的，而关于6，我们需要将B的匹配度加上C匹配度。
            
            最后我们得到的一个表格为
            【 书本ID，匹配度 】
            【  xxxxx    1.223】
            【  xxxxx    1.223】
            【  xxxxx    0.423】
            【  xxxxx    1.323】
            【  xxxxx    0.023】
            【  xxxxx    0.000】
    
            我们再对这个表格排序 将前TOPN推荐给用户A。
        """
        top_n_user_data = [self.frame[self.frame['UserID'] == k] for k, _ in top_n_users]
        interest_list = []
        for book_id in candidates_books:
            tmp = []
            for user_data in top_n_user_data:
                if book_id in user_data['BookID'].values:
                    readdf = user_data[user_data['BookID'] == book_id]
                    tmp.append(round(readdf['Rating'].mean(),2))
                else:
                    tmp.append(0)
            interest = sum([top_n_users[i][1] * tmp[i] for i in range(len(top_n_users))])
            interest_list.append((book_id, interest))
        interest_list = sorted(interest_list, key=lambda x: x[1], reverse=True)
        return interest_list[:top_n]



    def calculate(self, target_user_id, top_n):
        """
        user-cf for books recommendation.
        """
        # most similar top n users
        top_n_users = self._get_top_n_users(target_user_id, top_n)
        # candidates books for recommendation
        candidates_books = self._get_candidates_items(target_user_id)
        # most interest top n books
        top_n_books = self._get_top_n_items(top_n_users, candidates_books, top_n)
        
        print(top_n_books)
        name = []
        values = []
        for x in top_n_books:
            name.append(x[0])
            values.append(x[1])
        df = pd.DataFrame({'UserID':target_user_id,'BookID':name,'score':values})
        return df


def run(i):
    global res
    target_user_id = users[i]
    DF = usercf.calculate(target_user_id, top_n)
    res = res.append(DF)
    

path = './data/BX-Book-Ratings.csv'
Data = pd.read_csv(path, sep=None, error_bad_lines=False)
Data.columns = ['UserID','BookID','Rating']
res = pd.DataFrame(columns=['UserID','BookID','score'])
usercf = UserCf()
#---------------------------------------------------------------------------------------------------------------
#   这个程序的功能是 从100W的评分数据中，挑选20个用户。users中20表示20个用户,可以更改这个值来获得更多基于用户的推荐信息。
#   top_n 表示 对于登录的用户，我们推荐的书籍为计算出来推荐度的序列中的前10本书。如果存在推荐度的推荐书籍小于10.会随机拿书籍补全  
#   如果是给定ID  那么 users = ['给定ID']     
#----------------------------------------------------------------------------------------------------------------
import random
users = [random.choice(list(set(Data['UserID']))) for x in range(20)]
top_n = 10
for x in range(len(users)):
    print(x)
    run(x)
    print(res)
res.to_csv('./data/booktuijian.csv',index=False)

