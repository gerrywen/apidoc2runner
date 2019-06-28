import json
import logging
import os
import re

from apidoc2runner import utils
from apidoc2runner.parser import parse_value_from_type


class apidocParser(object):
    def __init__(self, apidoc_testcase_file):
        self.apidoc_testcase_file = apidoc_testcase_file

    def read_apidoc_data(self):
        """
        读取json数据
        :return:
        """
        with open(self.apidoc_testcase_file, encoding='utf-8', mode='r') as file:
            apidoc_data = json.load(file)

        return apidoc_data

    def parse_data(self):
        """
        加载 apidoc 数据到 json 测试对象
        """
        logging.info("Start to generate JSON testset.")
        #  读取json数据
        apidoc_data = self.read_apidoc_data()
        # 提取apidoc item数据
        result = self.parse_items(apidoc_data, None)
        return result

    def parse_items(self, items, folder_name=None):
        """
        解析每个items数据
        :param items:
        :param folder_name:
        :return:
        """
        result = []
        for folder in items:
            # 解析每个请求接口items
            api = self.parse_each_item(folder)
            api[1]["folder_name"] = folder_name if not api[1]['folder_name'] else api[1]['folder_name']
            result.append(api)
        return result

    def parse_header(self, request_header):
        """
        头部数据解析处理
        :param request_header:
        :return:
        """
        headers = {}
        if ("fields" in request_header.keys()) and (len(request_header["fields"]) > 0):
            if (("Header" in request_header["fields"].keys()) and
                    (len(request_header["fields"]["Header"])) > 0):
                for header in request_header["fields"]["Header"]:
                    header_keys = header.keys()
                    if ("field" in header_keys) and ("defaultValue" in header_keys):
                        _value = header["defaultValue"]
                        _value = self.apidoc2env(_value)
                        headers[header["field"]] = _value
        return headers

    def parse_body(self, parameters):
        """
        请求参数解析
        :param parameters:
        :return:
        """
        body = {}
        # 记录需要包装成数组的对象
        object_list = []

        for parameter in parameters:
            type = parameter['type']
            _obj = self.get_field_value(parameter)
            # value值处理
            _value = _obj["value"]
            _value = self.apidoc2env(_value)
            key_value = _obj["key"].split('.')[-1]

            _value = ("${ENV(" + key_value + ")}") if not _value else _value
            if type == 'String' and len(_value) <= 0:
                continue
            # 对象处理
            key_list = _obj["key"].split(".")
            # 数组对象
            if type == 'Object[]':
                body[_obj["key"]] = {}
                object_list.append(_obj["key"])
            elif type == 'Object':
                body[_obj["key"]] = {}
            elif type == 'String' and len(key_list) > 1:
                body[key_list[0]].update({key_list[1]: _value})
            else:
                body[_obj["key"]] = _value
        # print(object_list)
        for key in body:
            if key in object_list:
                body[key] = [body[key]]
        return body

    def parse_success_fields(self, response_success):
        """
        解析返回结果
        :param response_success:
        :return:
        """
        validate = []
        extract = []
        output = []
        if ("fields" in response_success.keys()) and (len(response_success["fields"]) > 0):
            # 判断响应的字段是成功的还是失败的
            if (("Success 200" in response_success["fields"].keys()) and
                    (len(response_success["fields"]["Success 200"])) > 0):
                for item in response_success["fields"]["Success 200"]:
                    # 提取code status_code
                    item_keys = item.keys()
                    if ("field" in item_keys) and ("defaultValue" in item_keys) and \
                            (item["field"] == 'code'
                             or item["field"] == 'status_code'
                             or item["field"] == 'message'):
                        default_value = item["defaultValue"] if not item["type"] == "Number" else int(
                            item["defaultValue"])
                        validate.append({
                            "eq": ["content." + item["field"], default_value]
                        })
                    else:
                        field = item['field'].replace('.', '_')
                        output.append(field)
                        extract.append({
                            field: "content." + item["field"]
                            # item["field"]: "" if not ("defaultValue" in item.keys()) else item["defaultValue"]
                        })
        return {"validate": validate, "extract": extract, "output": output}

    def apidoc2env(self, _value):
        """
        apidoc的环境变量参数名转py环境变量名
        :param _value:
        :return:
        """
        value_split = _value.split("}}", 1)
        _url = ''
        if len(value_split) > 1:
            _url = value_split[1]
        p1 = re.compile(r'{{(.*?)}}', re.S)  # 最小匹配
        value_list = re.findall(p1, _value)
        if len(value_list) > 0:
            _value = "${ENV(" + value_list[0] + ")}"
            _value += _url
        return _value

    def parse_uri_env(self, url):
        """
        获取接口地址
        :param url:
        :return:
        """
        url_split = url.split(")}", 1)
        _url = url
        if len(url_split) > 1:
            _url = url_split[1]
        p1 = re.compile(r'{{(.*?)}}', re.S)  # 最小匹配
        value_list = re.findall(p1, _url)
        if len(value_list) > 0:
            url_list = _url.split('/')[:-1]
            url_list.append("${ENV(" + value_list[0] + ")}")
            _url = '/'.join(url_list)

        return _url

    def parse_each_item(self, item):
        """ parse each item in apidoc to testcase in httprunner
        """
        # 测试用例配置信息
        config = {}
        config["name"] = item["title"]
        parse_uri = item['url'].replace('/', '_')[1:]
        config["id"] = parse_uri

        # test用例数据
        api = {}
        api["name"] = item["group"] + "/" + parse_uri

        # api["variables"] = []

        request = {}
        request["method"] = item["type"]

        # 请求地址【必填】
        url = "${ENV(BASE_URL)}" + self.parse_uri_env(item["url"])
        # 判断头部是否需要有传值
        if "header" in item.keys():
            request["headers"] = self.parse_header(item["header"])

        # 判断请求体是否传值
        body = {}
        if "parameter" in item.keys():
            request_parameter = item['parameter']
            if ("fields" in request_parameter.keys()) and (len(request_parameter["fields"]) > 0):
                if (("Parameter" in request_parameter["fields"].keys()) and
                        (len(request_parameter["fields"]["Parameter"])) > 0):
                    body = self.parse_body(request_parameter["fields"]["Parameter"])

        # 判断是post请求还是get请求
        if request['method'] == ("GET" or "get"):
            request["url"] = url.split("?")[0]
            request["data"] = body
        else:
            request["url"] = url
            request["json"] = body

        # 返回值处理
        sccess_info = self.parse_success_fields(item["success"])
        api["request"] = request
        api["validate"] = sccess_info['validate']
        api["folder_name"] = item["group"]
        # todo: 传值数据结构待完善
        # api["extract"] = sccess_info['extract']
        # config["output"] = sccess_info['output']

        api_test = [config, api]
        return api_test

    def save(self, data, output_dir, output_file_type="json"):
        count = 0
        output_dir = os.path.join(output_dir, "api")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for each_api in data:
            count += 1
            try:
                api_uri = each_api[0]['id']
            except:
                api_uri = str(count)
            file_name = api_uri + "." + output_file_type

            folder_name = each_api[1].pop("folder_name")
            if folder_name:
                folder_path = os.path.join(output_dir, folder_name)
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                # 文件输入写入路径
                file_path = os.path.join(folder_path, file_name)
            else:
                # 文件输入写入路径
                file_path = os.path.join(output_dir, file_name)
            # 判断文件路径是否存在
            if os.path.isfile(file_path):
                logging.error("{} file had exist.".format(file_path))
                continue
            # 判断输出类型
            test_api = [
                {"config": each_api[0]},
                {"test": each_api[1]}
            ]
            if output_file_type == "json":
                utils.dump_json(test_api, file_path)
            else:
                utils.dump_yaml(test_api, file_path)

    def get_field_value(self, _obj):
        """
        获取字段key-value值
        :param _obj:
        :return:
        """
        obj_keys = _obj.keys()
        obj = {}
        # 判断是否存在字段
        if "field" in obj_keys:
            defalut_key = "defaultValue"
            obj = {"key": _obj["field"], "value": "" if not (defalut_key in obj_keys) else _obj[defalut_key]}
        return obj
