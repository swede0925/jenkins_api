#!/usr/bin/env python
# -*- coding:utf-8 -*-

import requests
from .common import copy_dict, ClientError, AuthError, ValidationError, ServerError

class jenkinsapi:
    DEFAULT_HEADERS = {'Content-Type': 'text/xml; charset=utf-8'}

    def __init__(self, jenkins_url=None, username=None, password=None, token=None):
        self.jenkins_url = jenkins_url
        self._session = requests.Session()

        if token:
            self._session.auth = token, ''
        elif username and password:
            self._session.auth = username, password

    def _get_url(self, endpoint):
        """
        :param endpoint:
        :return:
        """
        return '{}/{}'.format(self.jenkins_url, endpoint)

    def http_request(self, verb, endpoint, query_data={}, post_data=None, files=None, **kwargs):
        """
        Make an HTTP request to the jenkins server.
        :param verb:
        :param endpoint:
        :param query_data:
        :param post_data:
        :param files:
        :param kwargs:
        :return:
        """
        url = self._get_url(endpoint)
        params = {}
        copy_dict(params, query_data)
        copy_dict(params, kwargs)

        # We need to deal with json vs. data when uploading files
        if files:
            data = None
            json = post_data
        else:
            data = post_data
            json = None

        result = self._session.request(verb, url, json=json, data=data, params=params,
                                       files=files, headers=self.DEFAULT_HEADERS)
        self.__check_response(result)
        return result

    def http_get(self, endpoint, query_data={}, **kwargs):
        """
        Make a GET request to the jenkins server.
        :param endpoint:
        :param query_data:
        :param kwargs:
        :return:
        """
        result = self.http_request('get', endpoint, query_data=query_data, **kwargs)
        return result

    def http_post(self, endpoint, query_data={}, post_data={}, files=None,
                  **kwargs):
        """
        Make a POST request to the jenkins server.
        :param endpoint:
        :param query_data:
        :param post_data:
        :param files:
        :param kwargs:
        :return:
        """
        result = self.http_request('post', endpoint, query_data=query_data,
                                   post_data=post_data, files=files, **kwargs)
        return result

    def http_put(self, endpoint, query_data={}, post_data=None, files=None,
                 **kwargs):
        """
        Make a PUT request to the jenkins server.
        :param endpoint:
        :param query_data:
        :param post_data:
        :param files:
        :param kwargs:
        :return:
        """
        result = self.http_request('put', endpoint, query_data=query_data,
                                   post_data=post_data, files=files, **kwargs)
        return result

    def http_delete(self, endpoint, **kwargs):
        """
        Make a PUT request to the jenkins server.
        :param endpoint:
        :param kwargs:
        :return:
        """
        return self.http_request('delete', endpoint, **kwargs)

    @staticmethod
    def __check_response(res):
        """
        Analyse response status and return or raise exception
        :param res:
        :return:
        """
        if res.status_code < 300:
            # OK, return http response
            pass
        elif res.status_code == 400:
            # Validation error
            raise ValidationError("Response: {} {}".format(res.status_code, res.reason))
        elif res.status_code in (401, 403):
            # Auth error
            raise AuthError("Response: {} {}".format(res.status_code, res.reason))
        elif res.status_code < 500:
            # Other 4xx, generic client error
            raise ClientError("Response: {} {}".format(res.status_code, res.reason))
        else:
            # 5xx is server error
            raise ServerError("Response: {} {}".format(res.status_code, res.reason))

    def get_job_info(self, job_name, depth=0):
        """
        获取job信息
        :param job_name:
        :param depth:
        :return:
        """
        JOB_INFO_ENDPOINT = 'job/%s/api/json' % job_name
        resp = self.http_get(JOB_INFO_ENDPOINT, query_data={'depth': depth})
        return resp.json()

    def enable_job(self, job_name):
        """
        Enable Jenkins job.
        :param job_name:
        :return:
        """
        ENABLE_JOB_ENDPOINT = 'job/%s/enable' % job_name
        self.http_post(ENABLE_JOB_ENDPOINT)

    def disable_job(self, job_name):
        """
        Disable Jenkins job.
        :param job_name:
        :return:
        """
        DISABLE_JOB_ENDPOINT = 'job/%s/disable' % job_name
        self.http_post(DISABLE_JOB_ENDPOINT)

    def get_job_config(self, job_name):
        """
        获取Jenkins job配置
        :param job_name:
        :return:
        """
        CONFIG_JOB_ENDPOINT = 'job/%s/config.xml' % job_name
        resp = self.http_get(CONFIG_JOB_ENDPOINT)
        return resp.content

    def reconfig_job(self, job_name, config_xml):
        """
        改变Jenkins job配置
        :param job_name:
        :param config_xml:
        :return:
        """
        CONFIG_JOB_ENDPOINT = 'job/%s/config.xml' % job_name
        self.http_post(CONFIG_JOB_ENDPOINT, post_data=config_xml.encode('utf-8'))

    def create_job(self, job_name, config_xml):
        """
        创建新的Jenkins job
        :param job_name:
        :param config_xml:
        :return:
        """
        CREATE_JOB_ENDPOINT = 'createItem'
        self.http_post(CREATE_JOB_ENDPOINT, query_data={'name': job_name}, post_data=config_xml.encode('utf-8'))

    def delete_job(self, job_name):
        """
        删除job
        :param job_name:
        :return:
        """
        DELETE_JOB_ENDPOINT = 'job/%s/doDelete' % job_name
        self.http_post(DELETE_JOB_ENDPOINT)

    def rename_job(self, from_name, to_name):
        """
        重命名jenkins job
        :param from_name:
        :param to_name:
        :return:
        """
        RENAME_JOB_ENDPOINT = 'job/%s/doRename' % from_name
        self.http_post(RENAME_JOB_ENDPOINT, query_data={'newName': to_name})

    def copy_job(self, from_name, to_name):
        """
        复制jenkins job
        :param from_name:
        :param to_name:
        :return:
        """
        COPY_JOB_ENDPOINT = 'createItem'
        self.http_post(COPY_JOB_ENDPOINT, query_data={'from': from_name, 'name': to_name, 'mode': 'copy'})

    def get_info(self):
        """
        获取所有项目信息
        :return:
        """
        INFO_ENDPOINT = 'api/json'
        resp = self.http_get(INFO_ENDPOINT)
        return resp.json()

    def get_jobs(self):
        """
        获取所有job信息
        :return:
        """
        return self.get_info()['jobs']

    def get_jobs_name(self):
        """
        获取所有job名字
        :return:
        """
        jobs_list = [item['name'] for item in self.get_jobs()]
        return jobs_list

    def get_views(self):
        """
        获取所有Views信息
        :return:
        """
        return self.get_info()['views']

    def get_views_name(self):
        """
        获取所有View名字
        :return:
        """
        views_List = [item['name'] for item in self.get_views()]
        return views_List

    def get_view_jobs(self, view_name):
        """
        获取指定View下所有的job
        :param view_name:
        :return:
        """
        VIEW_JOBS_ENDPOINT = 'view/%s/api/json' % view_name
        resp = self.http_get(VIEW_JOBS_ENDPOINT, query_data={'tree': 'jobs[url,color,name]'})
        return resp.json()['jobs']

    def get_view_config(self, view_name):
        """
        获取View配置信息
        :param view_name:
        :return:
        """
        CONFIG_VIEW_ENDPOINT = 'view/%s/config.xml' % view_name
        resp = self.http_get(CONFIG_VIEW_ENDPOINT)
        return resp.content

    def create_view(self, view_name, config_xml):
        """
        创建新的View
        :param view_name:
        :param config_xml:
        :return:
        """
        CREATE_VIEW_ENDPOINT = 'createView'
        self.http_post(CREATE_VIEW_ENDPOINT, query_data={'name': view_name}, post_data=config_xml.encode('utf-8'))

    def reconfig_view(self, view_name, config_xml):
        """
        重置View配置
        :param view_name:
        :param config_xml:
        :return:
        """
        CONFIG_VIEW_ENDPOINT = 'view/%s/config.xml' % view_name
        self.http_post(CONFIG_VIEW_ENDPOINT, post_data=config_xml.encode('utf-8'))

    def delete_view(self, view_name):
        """
        删除View
        :param view_name:
        :return:
        """
        DELETE_VIEW_ENDPOINT = 'view/%s/doDelete' % view_name
        self.http_post(DELETE_VIEW_ENDPOINT)

    def get_build_info(self, job_name, build_number, depth=0):
        """
        获取Jenkins build的信息
        :param job_name:
        :param build_number:
        :param depth:
        :return:
        """
        BUILD_INFO_ENDPOINT = 'job/%s/%d/api/json' % (job_name, build_number)
        resp = self.http_get(BUILD_INFO_ENDPOINT, query_data={'depth': depth})
        return resp.json()

    def build_job(self, job_name, parameters=None):
        """
        触发jenkins job,可以带参数
        :param name:
        :param parameters: parameters for job, or ``None``, ``dict``
        :param token:
        :return:
        """
        BUILD_JOB_ENDPOINT = 'job/%s/build' % job_name
        BUILD_WITH_PARAMS_JOB_ENDPOINT = 'job/%s/buildWithParameters' % job_name
        if parameters:
            self.http_post(BUILD_WITH_PARAMS_JOB_ENDPOINT, query_data=parameters)
        else:
            self.http_post(BUILD_JOB_ENDPOINT)

    def stop_build(self, job_name, number):
        """
        停止Jenkins build
        :param job_name:
        :param number:
        :return:
        """
        STOP_BUILD_ENDPOINT = 'job/%s/%s/stop' % (job_name, number)
        self.http_post(STOP_BUILD_ENDPOINT)

    def get_build_console_output(self, job_name, number):
        """
        获取Jenkins build日志
        :param job_name:
        :param number:
        :return:
        """
        BUILD_CONSOLE_OUTPUT_ENDPOINT = 'job/%s/%d/consoleText' % (job_name, number)
        resp = self.http_get(BUILD_CONSOLE_OUTPUT_ENDPOINT)
        return resp.text

    def delete_build(self, job_name, number):
        """
        删除Jenkins build
        :param job_name:
        :param number:
        :return:
        """
        DELETE_BUILD_ENDPOINT = 'job/%s/%s/doDelete' % (job_name, number)
        self.http_post(DELETE_BUILD_ENDPOINT)

    def get_queue_info(self, depth=0):
        """
        获取排队信息
        :return: list of job dictionaries,
        """
        Q_INFO_ENDPOINT = 'queue/api/json'
        resp = self.http_get(Q_INFO_ENDPOINT, query_data={'depth': depth})
        return resp.json()['items']

    def get_queue_item(self, item_number, depth=0):
        """
        Get information about a queued item (to-be-created job).
        :param item_number:
        :param depth:
        :return:
        """
        Q_ITEM_ENDPOINT = 'queue/item/%d/api/json' % item_number
        resp = self.http_get(Q_ITEM_ENDPOINT, query_data={'depth': depth})
        return resp.json()

    def cancel_queue(self, id):
        """
        取消排队任务
        :param id:
        :return:
        """
        CANCEL_QUEUE_ENDPOINT = 'queue/cancelItem'
        try:
            self.http_post(CANCEL_QUEUE_ENDPOINT, query_data={'id': id})
        except Exception:
            pass
