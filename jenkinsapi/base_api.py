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
        JOB_INFO_ENDPOINT = 'job/%s/api/json?depth=%s' % (job_name, depth)
        resp = self.http_get(JOB_INFO_ENDPOINT)
        return resp.json()

    def get_build_info(self, job_name, build_number, depth=0):
        """
        获取job第number次信息
        :param job_name:
        :param build_number:
        :param depth:
        :return:
        """
        JOB_BUILD_INFO_ENDPOINT = 'job/%s/%d/api/json?depth=%s' % (job_name, build_number, depth)
        resp = self.http_get(JOB_BUILD_INFO_ENDPOINT)
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
        Get configuration of existing Jenkins job.
        :param job_name:
        :return:
        """
        CONFIG_JOB_ENDPOINT = 'job/%s/config.xml' % job_name
        resp = self.http_get(CONFIG_JOB_ENDPOINT)
        return resp.content

    def reconfig_job(self, job_name, config_xml):
        """
        Change configuration of existing Jenkins job.
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

    def get_jobs_info(self):
        """
        获取所有项目信息
        :return:
        """
        INFO_ENDPOINT = 'api/json'
        resp = self.http_get(INFO_ENDPOINT)
        return resp.json()

    def get_jobs_name(self):
        """
        获取所有项目信息
        :return:
        """
        jobs_list = []
        for item in self.get_jobs_info()['jobs']:
            jobs_list.append(item['name'])
        return jobs_list
