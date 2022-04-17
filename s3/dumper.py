import os

import boto3
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

if os.path.isfile('.env'):
    load_dotenv(dotenv_path='.env', verbose=True, override=True)

s3 = boto3.resource(service_name='s3',
                    region_name=os.environ.get('REGION_NAME'),
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))
TARGET = [buck.name for buck in s3.buckets.all()][0]
if not os.path.isdir(TARGET):
    os.makedirs(name=TARGET)
my_bucket = s3.Bucket(TARGET)
keys = [obj.key for obj in my_bucket.objects.all()]


def downloader(file: str):
    path, filename = os.path.split(file)
    target_path = TARGET + os.path.sep + path.replace(' ', '_')
    if not os.path.isdir(target_path):
        os.makedirs(target_path)
    my_bucket.download_file(file, f'{target_path}{os.path.sep}{filename}')


with ThreadPoolExecutor(max_workers=10) as executor:
    list(tqdm(iterable=executor.map(downloader, keys),
              total=len(keys), desc=f'Downloading files from {TARGET}',
              unit='files', leave=True))
