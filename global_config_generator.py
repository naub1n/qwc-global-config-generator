import os
import json
import urllib
import requests

from collections import OrderedDict
from jsonmerge import merge
from global_config_logger import Logger


class GlobalConfigGenerator:
    """GlobalConfigGenerator class
    Generate tenantConfig.json, index.html and config.json for each tenant in config-in folder
    """

    def __init__(self, config_in_path, logger):
        """Constructor

        :param str config_in_path: GlobalConfigGenerator config-in path
        :param Logger logger: Application logger
        """
        self.config_in_path = config_in_path
        self.logger = Logger(logger)

        self.config_file = os.path.join(
            self.config_in_path, 'globalConfig.json'
        )

        self.index_file = os.path.join(
            self.config_in_path, 'index.html'
        )

        self.config = self.read_config()
        self.html = self.read_index_html()

        if self.config:
            global_generator_config = self.config.get('config', {})
            self.config_generator_service_url = global_generator_config.get('config_generator_service_url',
                                                                            'http://qwc-config-service:9090')

    def get_logger(self):
        return self.logger

    def read_config(self):
        if not os.path.exists(self.config_file):
            msg = "Config file '%s' does not exist." % self.config_file
            self.logger.error(msg)
            return

        try:
            with open(self.config_file, encoding='utf-8') as f:
                # parse config JSON with original order of keys
                config = json.load(f, object_pairs_hook=OrderedDict)

        except Exception as e:
            msg = "Error loading GlobalConfigGenerator config:\n%s" % e
            self.logger.error(msg)
            return

        return config

    def read_index_html(self):
        if not os.path.exists(self.index_file):
            msg = "Index file '%s' does not exist." % self.index_file
            self.logger.error(msg)
            return

        try:
            with open(self.index_file, encoding='utf-8') as f:
                html = f.read()

        except Exception as e:
            msg = "Error loading 'index.html' :\n%s" % e
            self.logger.error(msg)
            return

        return html

    def create_tenant_config_file(self, tenant, common_config, specific_config, outputfile, schema={}):
        tenant_path = os.path.join(self.config_in_path, tenant)
        tenant_output_file = os.path.join(tenant_path, outputfile)
        # Merge two json files
        merged_config = merge(common_config, specific_config, schema)
        # Creates dirs if not exists
        os.makedirs(tenant_path, exist_ok=True)
        # Write config
        with open(tenant_output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_config, f, ensure_ascii=False, indent=4)

        self.logger.info("%s merged for tenant '%s'" % (outputfile, tenant))
        self.logger.debug("Merged %s path is '%s'" % (outputfile, tenant_output_file))

    def create_tenant_index_file(self, tenant):
        try:
            tenant_path = os.path.join(self.config_in_path, tenant)
            tenant_output_file = os.path.join(tenant_path, 'index.html')
            with open(tenant_output_file, 'w') as f:
                f.write(self.html)

            self.logger.info("index.html created for tenant '%s'." % tenant)
            self.logger.debug("index.html path is '%s'" % tenant_output_file)

        except Exception as e:
            msg = "Error writing 'index.html' :\n%s" % str(e)
            self.logger.error(msg)

    def write_configs(self):
        specific_configs = self.config.get('specific_configs', [])
        common_config = self.config.get('common_config', {})
        for specific_config in specific_configs:
            tenant = specific_config.get('tenant', '')
            if tenant:
                common_cfggensrv_data = common_config.get('config-generator-service', {})
                specific_cfggensrv_data = specific_config.get('config-generator-service', {})
                cfggensrv_schema = self.merge_schema_for_config_generator()
                # Add tenant info
                specific_cfggensrv_data['config'] = specific_cfggensrv_data.get('config', {})
                specific_cfggensrv_data['config'].update(tenant=tenant)
                #Create qwc-config-generator file : tenantConfig.json
                self.create_tenant_config_file(tenant,
                                               common_cfggensrv_data,
                                               specific_cfggensrv_data,
                                               'tenantConfig.json',
                                               cfggensrv_schema)

                common_qwc2config_data = common_config.get('qwc2config', {})
                specific_qwc2config_data = specific_config.get('qwc2config', {})
                # Create qwc2 file : config.json
                self.create_tenant_config_file(tenant, common_qwc2config_data, specific_qwc2config_data, 'config.json')

                # Create qwc2 file : index.html
                self.create_tenant_index_file(tenant)

                # Generate configs and permissions with qwc-config-generator-service
                self.generate_tenant_config(tenant)

            else:
                msg = "'tenant' parameter missing or empty. 'tenant' parameter should be present in each specific config."
                self.logger.error(msg)

    def generate_tenant_config(self, tenant):
        try:
            response = requests.post(
                urllib.parse.urljoin(
                    self.config_generator_service_url,
                    "generate_configs?tenant=" + tenant))

            if 'CRITICAL' in response.text:
                msg = "Unable to generate service configurations for tenant '%s' : \n%s" % (tenant, str(response.text))
                self.logger.error(msg)
            else:
                msg = "Config files and permissions generated for tenant '%s'." % tenant
                self.logger.info(msg)

        except Exception as e:
            msg = "unable to generate config file : %s" % str(e)
            self.logger.error(msg)

    def merge_schema_for_config_generator(self):
        schema = {
            "properties": {
                "services": {
                    "mergeStrategy": "arrayMergeById",
                    "mergeOptions": {"idRef": "name"}
                }
            }
        }

        return schema

