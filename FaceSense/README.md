# CSE546-Cloud-Computing-Project-2

## PaaS using Amazon Web Services

### Team Members
- Aditya Deepak Bhat (1222133796)
- Radhika Kulkarni (1222165776)
- Swarali Chine (1222583687)

In this project, we aim to build a real-time face recognition application which is serverless and uses Function as a Service model of cloud computing. We are using Raspberry Pi as the edge device to record videos and we are utilizing AWS Lambda based PaaS. The aim is to recognize the faces in the captured videos and return the person’s information, by querying the database, to the device. 

The following AWS services were used in this project: AWS Lambda, API Gateway, Simple Storage Service (S3), and DynamoDB.
Please refer to the report for more details.

## Setup Details and Execution Steps

* Lambda Functions Used:
    - faceRecognitionFromContainer

* S3 Buckets used:
    - Input Video Bucket - ccinputvideobucket 
    - Image Frame and Result Bucket - framesfromimages

* DynamoDB Table used:
    - student-academic-info

* API Gateway:
    - https://w97zrvuvtb.execute-api.us-east-1.amazonaws.com/dev/{video_file_name}

### Requirements
- Docker
- Python3.6+

### Training the deep learning model
- For the training, we have used the provided AMI (ID: ami-ami-016931ea066955c9d, Name: CSE546-2022Spring-project2, Region: us-east-1).
- We captured images of all 3 team members from the Pi's camera.
- Train the customized model using the following command:
    python3 train_face_recognition.py –-data_dir <YOUR_IMAGE_PATH> --num_epochs <num_epochs>
- The weights of the model that has best validation accuracy will be stored in "checkpoint/model_vggface2_best.pth", the labels are stored in "checkpoint/labels.json".

### Setup of the Lambda function using the container image of the deep learning model 
- Copy the models and checkpoint of the trained deep learning model
- Create the docker image using the Dockerfile with the following command:
```
docker build -t aditya-bhat/face-recognition .
```
- Upload the saved image to AWS ECR.
- Create and deploy a lambda function using the image uploaded.

### Setup on the raspberry Pi
- Setup the Pi with the camera connected.
- Use record_video_and_send_API_request.py (sample command given below) to record videos and send the request to the API Gateway endpoint.

### Testing the application:

* API Gateway Endpoint URL - https://w97zrvuvtb.execute-api.us-east-1.amazonaws.com/dev/{video_file_name}

* command to test the application on the pi:
```
python3 record_video_and_send_API_request.py \
 --BASE_URL "https://w97zrvuvtb.execute-api.us-east-1.amazonaws.com/dev/" \
 --NUM_CLIPS 600 \
 --CLIP_LENGTH 0.5
```
