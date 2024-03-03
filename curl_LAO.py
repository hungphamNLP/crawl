import requests
import json 
from urllib.parse import urlencode,quote
from io import BytesIO
import pycurl
import argparse
from fake_useragent import UserAgent
import os
ua = UserAgent()
headers_ = {'User-Agent': ua.random}


def get_domain(json_file):
    with open(json_file,'r',encoding='utf-8') as file:
        data = json.load(file)
    data = data['content']
    domain = []
    for sub_content in data:
        domain.append(sub_content['Domain'])
    return domain


def get_feature(url,limit=10000):
    params = {'limit': limit}
    response = requests.get(url, params=params,headers=headers_)
    if response.status_code == 200:
        obj = response.json()
    
    data_feature = []
    for sub_obj in obj:
        feature = {"Id":sub_obj.get("Id"),"fullname":sub_obj.get("fullname"),"editfullname":sub_obj.get("editfullname")}
        data_feature.append(feature)
    return data_feature



def check_download(foldername):
    file_path = './download/'+foldername+'.zip'
    return os.path.exists(file_path)


def curl_download(url,domain,folderId,foldername,startdate,enddate):
    foldername_endcode = quote(foldername, safe='')
    encoded_params = url+'/'+domain+'/'+folderId+'/'+foldername_endcode+'/'+startdate+'/'+enddate
    print(encoded_params)
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(curl.URL, encoded_params)
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()
    response_code = curl.getinfo(curl.RESPONSE_CODE)
    curl.close()
    if response_code == 200:
        # Get the downloaded content from the buffer
        downloaded_content = buffer.getvalue()

        # Save the content to a file or process it as needed
        with open('download/'+foldername+'.zip', 'wb') as file:
            file.write(downloaded_content)
    else:
        print(f"Error: HTTP response code {response_code}")
        with open('500_error.txt', 'a') as file:
            file.write("\n"+encoded_params)


def run_main(url_all_folder,url_download_file,domain,startdate,enddate):
    try:
        data_feature = get_feature(url_all_folder)
    except:
        print("error")
    for data in data_feature:
        folderId = data["Id"]
        if data['fullname'] is not None:
            foldername = data['fullname']
        else:
            foldername =  data['editfullname']
        print(foldername)
        try:
            if (check_download(foldername)==True):
                print("file exists")
                continue
            else:
                curl_download(url_download_file,domain,folderId,foldername,startdate,enddate)
            # break
        except:
            print("download error")
            continue

 
        


if __name__ =='__main__':
    url = "https://tt-api.eoffice.la/api/FolderIncoming/getallfolder"
    print(get_feature(url))
    # url ='https://tt-api.eoffice.la/api/IncomingAPI/folderdownload'
    # domain = 'monre.eoffice.la'
    # Id = 'f97c0533395c54f6188c50d98bfc91cb'
    # foldername = 'ນາງ ອາມອນລັດ ມະນີຜົນ'
    # rs = curl_download(url,domain,Id,foldername,startdate,enddate)
    # print(rs)
    parser = argparse.ArgumentParser()
    parser.add_argument('--url_list_folder',type=str,required=True,help = 'choose url')
    parser.add_argument('--url_download_folder',type=str,required=True,help = 'choose url')
    arg = parser.parse_args()


    domain_file ='listdomain-tt-api.json'
    startdate ='2021-1-1'
    enddate ='2024-3-3'
    list_domain = get_domain(domain_file)
    
    for domain in list_domain:
        run_main(arg.url_list_folder,arg.url_download_folder,domain,startdate,enddate)