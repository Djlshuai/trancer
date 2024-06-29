import ssl
from qcloudsms_py import SmsMultiSender, SmsSingleSender
from qcloudsms_py.httpclient import HTTPError

def send_sms_single(phone_num_list,template_id, template_param_list):
     appid = 0
     appkey = 0
     sms_sign = '0'
     sender = SmsSingleSender(appid, appkey)
     try :
         response = sender.send_with_param(86,phone_num_list,template_id,template_param_list,sign=sms_sign)
     except HTTPError as e:
         response = {'result':'1000','errmsg':"网络异常发送失败"}
     return response


