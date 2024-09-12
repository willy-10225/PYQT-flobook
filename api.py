import requests
import os
import json
from dataclasses import dataclass
from typing import List, Dict
from io import BytesIO

env_value = os.environ.get('flobook_monitor_sensor_log_http_serveraddress')

def urlget(url:str)-> dict:
    try:
        response = requests.get(url)
        # 检查请求是否成功
        if response.status_code == 200:
            # 解析 JSON 数据
            return response.json()
        else:
            return {'error':str(response.status_code)}
    except Exception as ex:
        return {'error':str(ex)}
    
def urlpost(url: str, data: dict = None, files: dict = None):
    try:
        response = requests.post(url, json=data, files=files)
        # 检查请求是否成功
        if response.status_code == 200:
            try:
                # 尝试解析 JSON 数据
                return response.json()
            except requests.exceptions.JSONDecodeError:
                # 解析失败时，返回响应内容用于调试
                return { 'response': response.text}
        else:
            return {'error': str(response.status_code)}
    except Exception as ex:
        return {'error':str(ex)}


def AddProjectInit()->Dict[str, Dict[str, str]]:
    return urlget(env_value.replace('Transfer','AddProjectInit'))

def UiProjectmailvsid()->Dict:
    return urlget(env_value.replace('Transfer','UiProjectmailvsid'))

def ProjectListInit(id:int)->List[Dict]:
    return urlpost(env_value.replace('Transfer','ProjectListInit'),{"id":id})

def GetUserId()-> int:
    return urlpost(env_value.replace('Transfer','GetUserId'),{"User": os.getlogin()})

@dataclass
class AddProjectPayload:
    projectType: str
    customerName: str
    product: str
    domain: str
    industryType: str
    projectName: str
    projectDescription: str
    checkPoint: str
    startTime: str  # 确保日期格式为 "YYYY/MM/DD HH:MM:SS"
    closeTime: str  # 确保日期格式为 "YYYY/MM/DD HH:MM:SS"
    projectCreater: str
    executor: str
    teammates: str
    software: str
    fileNames: str
    fileDescriptions: str
    security: str
    status: str  
def AddProject(payload: dict) -> str:
    # 直接使用字典，不需要 __dict__
    empty_file = BytesIO()
    files = {
        'file': ('', empty_file)  # 这里的第一个参数为文件名，可以留空
    }
    for key, value in payload.items():
        files[key] = (None, value)
        
    return urlpost(env_value.replace('Transfer', 'AddProject'), files=files)

@dataclass
class ModifyProjectPayload:
    customerName: str                # 客户名称
    closeTime: str                   # 项目关闭时间，ISO 8601 格式
    deal: str                        # 交易信息
    projectDescription: str          # 项目描述
    executor: str                    # 执行者
    domain: List[str]                # 领域列表
    id: int                          # 项目ID
    industryType: List[str]          # 行业类型列表
    product: str                     # 产品名称
    security: str                    # 安全性信息
    software: List[str]              # 软件列表
    startTime: str                   # 项目开始时间，ISO 8601 格式
    status: str                      # 项目状态
    projectName: str                 # 项目名称
    teammates: List[str]             # 团队成员列表
    projectType: List[str]           # 项目类型列表
    manager: str   
def ModifyProject(payload:dict)-> str:
    return urlpost(env_value.replace('Transfer','ModifyProject'),payload)

@dataclass
class DeleteProjectPayload:
    id: int          # 要删除的项目ID
    userName: str    # 执行删除操作的用户名
def DeleteProject(payload: dict)-> str:
    return urlpost(env_value.replace('Transfer','DeleteProject'), payload)