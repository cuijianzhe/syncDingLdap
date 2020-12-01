import requests
import json

DING_URL = "https://oapi.dingtalk.com"
class dingUserSync:

    def __init__(self):
        self.__DING_USER = 'ding10c6dd0d17f230c535c2f4657eb6378f'
        self.__DING_SECRET = '5qeXi5u0uq9yY1ZKwbn9eIrz7aOc8Nwdw_v4X2qWuhfnwzXNcTJQAP5gaU5DkX4L'
        self.headers = {'Content-Type': 'application/json;charset=utf-8'}
        self.token = ''
    def get_token(self):
        url = DING_URL + '/gettoken'
        param_dict = {
            'appkey': self.__DING_USER,
            'appsecret': self.__DING_SECRET,
        }

        ding_res = requests.get(url,param_dict,headers=self.headers).json()
        if ding_res.get('errcode') == 0:
            return ding_res.get('access_token')
        else:
            raise ding_res.get('errmsg')
    def get_depart_info(self):
        '''
        获取部门全部信息
        例：{'createDeptGroup': True, 'name': '何层组', 'id': 381056019, 'autoAddUser': True, 'parentid': 127811237}
        :return:
        '''
        if not self.token:
            self.token = self.get_token()
        url = DING_URL + '/department/list'
        ding_ret = requests.get(url, {'access_token': self.token}).json()
        if ding_ret.get('errcode') == 0:
            '''
            {'createDeptGroup': True, 'name': '石家庄一年级组', 'id': 402133352, 'autoAddUser': True, 'parentid': 143433704}
            '''
            return ding_ret.get('department')
        else:
            raise '错误信息为：%s，' % ding_ret.get('errmsg')

    def get_depart_id(self):
        depart_info = {}
        if not self.token:
            self.token = self.get_token()
        for depart in self.get_depart_info():
            depart_id, depart_name = depart.get('id'), depart.get('name')
            depart_info[depart_name] = depart_id
        return depart_info




