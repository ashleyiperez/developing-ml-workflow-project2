#SerializeDataLambda:
import json
import boto3
import urllib
import base64

s3=boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    # TODO implement
    #Get the s3 address from the Step Function event input
    key = event['s3_key'] #TODO: fill in
    bucket = event['s3_bucket'] #TODO: fill in
    
    #Download the data from s3 to /tmp/image.png
    #TODO: fill in
    s3 = boto3.resource('s3') #from aws doc: https://boto3.amazonaws.com/v1/documentation/api/1.9.42/guide/s3-example-download-file.html
    s3.Bucket(bucket).download_file(key, '/tmp/image.png')
    
    #read the data from a file
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read())
        
    #pass data back to step function
    print("Event:", event.keys())
    
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
            
        }
    }

#ClassifyImageLambda:
import json
import sagemaker
import base64
from sagemaker.serializers import IdentitySerializer
from sagemaker.predictor import Predictor

#Fill this in with the name of your deployed model
ENDPOINT = "image-classification-2023-01-21-14-22-22-101"

def lambda_handler(event, context):
    #Decode the image data
    image = base64.b64decode(event["image_data"])
    
    #Instantiate a Predictor
    predictor = Predictor(ENDPOINT) ##TODO: fill in
    
    #For this model the IdentitySerializer needs to be "image/png"
    predictor.serializer = IdentitySerializer("image/png")
    
    #Make a prediction:
    inferences = predictor.predict(image)#TODO: fill in
    
    #return the data back to step function
    event["inferences"] = inferences.decode('utf-8')
    
    return {
        'statusCode': 200,
        'body': json.dumps(event)    }


#filterInferenceLambda:
import json
import re

THRESHOLD = 0.8

def lambda_handler(event, context):
    
    #Grab the inferences from the event
    inferences = event["inferences"]
    
    #inference_values = [int(x) for x in str(inferences).split() if x.isdigit()]
    inference_values = [float(v) for v in re.findall(r'[\d]*[.][\d]+', str(inferences))] #convert values in string to list from: https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
    #find floats: https://stackoverflow.com/questions/4289331/how-to-extract-numbers-from-a-string-in-python
    
    #Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(values > THRESHOLD for values in inference_values) #sample code from: https://thispointer.com/check-if-any-value-in-python-list-is-greater-than-a-value/
    #print(meets_threshold)
    
    #If our threshold is met, pass our data back out of the
    #Step Function, else, end the Step Function with an error
    if meets_threshold: 
        pass
    else:
        raise ValueError(inferences)
    
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }
