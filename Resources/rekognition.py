from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource
from config import Config
from mysql_connection import get_connection
from mysql.connector import Error

from datetime import datetime

import boto3


class DetectFaceResources(Resource) :

    def post(self) :

        file = request.files.get('photo')

        if file is None :
            return {'error' : '파일을 업로드 하세요'}, 400
         
        current_time = datetime.now()

        new_file_name = current_time.isoformat().replace(':', '_') + '.jpg' 
    
        file.filename = new_file_name

        s3 = boto3.client('s3',
                    aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY )

        try :
            s3.upload_fileobj(file, 
                              Config.S3_BUCKET,
                              file.filename,
                              ExtraArgs = {'ACL' : 'public-read' , 
                                           'ContentType' : 'image/jpeg'} )
        except Exception as e :
            print(e)
            return {'error' : str(e)}, 500
        

        label_list = self.detect_labels(new_file_name, Config.S3_BUCKET)

        return {"result" : "success",
                "labels" : label_list,
                "count" : len(label_list)}
    