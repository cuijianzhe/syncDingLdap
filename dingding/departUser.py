from dingding.departInfo import *

class getdepartUser(dingUserSync):
    def get_depart_user(self, depart_id):
        '''
        获取组里面全部的人员name和userid
        :param depart_id:
        :return:
        '''
        if not self.token:
            self.token = self.get_token()
        param_dict = {
            'access_token': self.token,
            'department_id': depart_id
        }
        url = DING_URL + '/user/simplelist'
        depart_user_res = json.loads(requests.get(url, param_dict).text)
        if depart_user_res.get('errcode') == 0:
            #返回值实例：[{'name': '宫琳', 'userid': '054940691023503691'}, {'name': '张浩', 'userid': '084637391724299533'}]
            return depart_user_res.get('userlist')

