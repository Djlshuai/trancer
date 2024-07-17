# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging
from trancer import local_settings

def create_bucket(bucket,region="ap-guangzhou"):
# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
    region = region      # 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket

    config = CosConfig(Region=region, SecretId=local_settings.TENCENT_COS_ID, SecretKey=local_settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    client.create_bucket(
        Bucket=bucket,
        ACL='public-read'
    )
    cors_config = {
        'CORSRule': [
            {
                'AllowedOrigin': '*',
                'AllowedMethod': ['GET', 'PUT', 'HEAD', 'POST', 'DELETE'],
                'AllowedHeader': "*",
                'ExposeHeader': "*",
                'MaxAgeSeconds': 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )

def upload_file(bucket, region, file_object, key):
    config = CosConfig(Region=region, SecretId=local_settings.TENCENT_COS_ID, SecretKey=local_settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file_object,  # 文件对象
        Key=key  # 上传到桶之后的文件名
    )

    # https://wangyang-1251317460.cos.ap-chengdu.myqcloud.com/p1.png

    return "https://{}.cos.{}.myqcloud.com/{}".format(bucket, region, key)

def delete_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=local_settings.TENCENT_COS_ID, SecretKey=local_settings.TENCENT_COS_KEY)
    client = CosS3Client(config)

    response = client.delete_object(
        Bucket=bucket,
        Key=key  # 上传到桶之后的文件名
    )

def delete_file_list(bucket, region, key_list):
    config = CosConfig(Region=region, SecretId=local_settings.TENCENT_COS_ID, SecretKey=local_settings.TENCENT_COS_KEY)
    client = CosS3Client(config)
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects
    )

def credential(bucket, region):
    """ 获取cos上传临时凭证 """

    from sts.sts import Sts

    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 5,
        # 固定密钥 id
        'secret_id': local_settings.TENCENT_COS_ID,
        # 固定密钥 key
        'secret_key': local_settings.TENCENT_COS_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],

    }
    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict