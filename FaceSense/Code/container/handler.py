# from boto3 import client as boto3_client
# import pickle
import torch
# import torchvision
import torchvision.transforms as transforms
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models
import json
import numpy as np
# import argparse
import os
import boto3
import build_custom_model
from PIL import Image
import base64

def face_recognition_handler(event, context):
	aws_access_key_id = os.environ['aws_access_key_id']
	aws_secret_access_key = os.environ['aws_secret_access_key']
	key = event["path"][1:]
	dir_path = "/tmp/"
	VIDEO_PATH = f"{dir_path}{key}"
	IMAGE_PATH = str(dir_path) + event["path"][1:-5]+ ".png"

	print(type(event), type(event["body"]), key, dir_path)
	s3_frame_target_bucket = "framesfromimages"
	dynamoDbClient = boto3.client('dynamodb',region_name='us-east-1', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
	s3_target_bucket = "ccinputvideobucket"
	
	# Load the saved model
	labels_dir = "checkpoint/labels.json"
	model_path = "checkpoint/model_vggface2_best.pth"
    # read labels
	with open(labels_dir) as f:
		labels = json.load(f)
		print(f"labels: {labels}")
	
	device = torch.device('cpu')
	model = build_custom_model.build_model(len(labels)).to(device)
	model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu'))['model'])
	print("Model Loaded")

	# get the base64 encoded string
	vid_b64 = json.loads(event["body"])["video"]
	# convert it into bytes  
	vid_bytes = base64.b64decode(vid_b64.encode('utf-8'))
	fh = open(VIDEO_PATH, 'wb')
	fh.write(vid_bytes)
	fh.close()

	# extract the frame from the video
	os.system("ffmpeg -i " + VIDEO_PATH + " -r 1 " + IMAGE_PATH)
	
	# convert bytes data to PIL Image object
	img = Image.open(IMAGE_PATH)
	print("Image Loaded")

	# resize image to 160x160
	newsize = (160, 160)
	img = img.resize(newsize)

	# get the face recognition result from the model
	img_tensor = transforms.ToTensor()(img).unsqueeze_(0).to(device)
	print("Image Tensor Created Loaded")
	outputs = model(img_tensor)
	_, predicted = torch.max(outputs.data, 1)
	result = labels[np.array(predicted.cpu())[0]]
	img_name = f"{result}-{key}.png"
	img_and_result = f"({img_name}, {result})"
	print(f"Image and its recognition result is: {img_and_result}")

	# Write the video to the S3 bucket
	s3 = boto3.resource('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
	s3.meta.client.upload_file(VIDEO_PATH, s3_target_bucket, key)
	print("Wrote file to S3 Bucket:", s3_target_bucket)

	# write the frame to the S3 bucket
	s3.meta.client.upload_file(IMAGE_PATH, s3_frame_target_bucket, result + event["path"][1:-5]+ ".png")
	print("Wrote file to S3 Bucket:", s3_frame_target_bucket)

	# Get the student details from dynamoDB
	row = dynamoDbClient.get_item(
    TableName = 'student-academic-info',
    Key = {
        'name': {'S': result}
    })
	db_result = ""
	if "Item" not in row:
		db_result = "Not Found"
	else:
		db_result = row["Item"]["name"]["S"] + ", " + row["Item"]["major"]["S"] + ", " + row["Item"]["year"]["S"]
	
	# return response
	return {
        'statusCode': 200,
        'body': json.dumps(db_result)
    }
