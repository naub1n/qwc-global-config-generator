QWC GlobalConfigGenerator
====================

Generates config file `tenantConfig.json` for each tenant.

GlobalConfigGenerator is based on `jsonmerge` package.


Setup
-----

Create a GlobalConfigGenerator config file `globalConfig.json` (see below).


Configuration
-------------

Example `tenantConfig.json`:
```json
{
  "$schema": "https://github.com/naub1n/qwc-global-config-generator/raw/master/schemas/qwc-global-config-generator.json",
  "service": "global-config-generator",
  "config": {
    "config_generator_service_url": "http://qwc-config-service:9090"
  },
  "common_config": {
    "config-generator-service": {
      "$schema": "https://github.com/qwc-services/qwc-config-generator/raw/master/schemas/qwc-config-generator.json",
      "service": "config-generator",
      "config": {
        "default_qgis_server_url": "http://qwc-qgis-server/ows/",
        "config_db_url": "postgresql:///?service=qwc_configdb",
        "permissions_default_allow": true,
        "qgis_projects_base_dir": "/data/default",
        "qgis_projects_scan_base_dir": "/data/default/scan",
        "qgis_projects_gen_base_dir": "/data/default/gen",
        "qwc2_base_dir": "/qwc2"
      },
      "themesConfig": {},
      "services": []
    },
    "qwc2config": {
      "searchServiceUrl": "http://localhost:5011/",
      "searchDataServiceUrl": "http://localhost:5011/geom/",
      "editServiceUrl": "http://localhost:5012/"
    }
  },
  "specific_configs": [
    {
      "tenant": "default"
    },
    {
      "tenant": "test",
      "config-generator-service": {
        "themesConfig": {
          "defaultMapCrs": "EPSG:2154"
        }
      },
      "qwc2config": {
        "searchServiceUrl": "http://localhost:50020/"
      }
    }
  ]
}
```
What GlobalConfigGenerator do ?
-----

### GlobalConfigGenerator steps to create `tenantConfig.json`
1. GlobalConfigGenerator read each `tenant` name in `specific_configs` key.
2. GlobalConfigGenerator take data of `config-generator-service` sub-key in `common_config` key.
3. For each tenant GlobalConfigGenerator read data of `config-generator-service` sub-key in `specific_configs` key.
4. GlobalConfigGenerator apply merge strategy for each similar keys between `common_config` key and `specific_configs` key
5. GlobalConfigGenerator export `tenantConfig.json` file in tenant directory.

### GlobalConfigGenerator steps to create QWC2 `config.json`
1. GlobalConfigGenerator read each `tenant` name in `specific_configs` key.
2. GlobalConfigGenerator take data of `qwc2config` sub-key in `common_config` key.
3. For each tenant GlobalConfigGenerator read data of `qwc2config` sub-key in `specific_configs` key.
4. GlobalConfigGenerator apply merge strategy for each similar keys between `common_config` key and `specific_configs` key
5. GlobalConfigGenerator export `config.json` file in tenant directory.

### GlobalConfigGenerator steps to create QWC2 `index.html`
1. GlobalConfigGenerator read each `tenant` name in `specific_configs` key. 
2. GlobalConfigGenerator read and copy `index.html` in each tenant directory

### GlobalConfigGenerator rules
GlobalConfigGenerator use JSON schema specification to specify the merge strategy.

#### For `config-generator-service`
Merge schema used is [merge_schema_for_config_generator.json](schemas/merge_schema_for_config_generator.json)

Default strategy:
* All items in `services` key are merged by `name` key.
* All items in `items` key are appended.
* All items in `defaultBackgroundLayers` key are appended.
* All items in `defaultSearchProviders` key are appended.

#### For `qwc2config`
Merge schema used is [merge_schema_for_qwc2_config.json](schemas/merge_schema_for_qwc2_config.json)

Default strategy:
* No strategy used

What should I do ?
-----
1. Create a `globalConfig.json` file in root of `config-in` directory.
   1. Add data to `common_config` key. 
      1. Add data to `config-generator-service` key.
Read [qwc-config-generator-service description](https://github.com/qwc-services/qwc-config-generator/blob/master/README.md) to see all data which can be added.

      2. Add data to `qwc2config` key
</br>Read [QWC2 application configuration description](https://github.com/qgis/qwc2-demo-app/blob/master/doc/src/qwc_configuration.md#application-configuration-the-configjson-and-jsappconfigjs-files) and [config.json](https://github.com/qwc-services/qwc-docker/blob/master/volumes/config-in/default/config.json) file to see all data which can be added.

   2. Add data to `specific_configs` key

        One tenant name is minimal requirement. you can add this data :
        ```json
        {
          "tenant": "default"
        }
        ```
        Add all subkeys you want to add or modify in `config-generator-service` key or `qwc2config` key.
        
        You should respect json tree!! Add all parents keys before the specific key you want to modify.
        
        Exemple : If you want to modify `defaultMapCrs` key in a tenant, you should add `themesConfig` parent key like:
        ```json
        {
          "tenant": "TheTenantNameIWantToModify",
          "config-generator-service": {
            "themesConfig": {
              "defaultMapCrs": "EPSG:2154"
            }
          }
        }
        ```
2. Create an `index.html` file in root of `config-in` directory.
</br>Use default [index.html](https://github.com/qwc-services/qwc-docker/blob/master/volumes/config-in/default/index.html) file or create yours.


Usage
-----

### Service

Set the `INPUT_CONFIG_PATH` environment variable to the base directory where for the configuration files are that should be read by the ConfigGenerator (default: `config-in/`).

*NOTE:* the ConfigGenerator's docker user (`www-data`) needs to have write permissions to the directory defined in `INPUT_CONFIG_PATH`!

Base URL:

    http://localhost:5010/

Generate configs for all tenant:

    curl -X POST "http://localhost:5010/generate_configs?"



Development
-----------

Create a virtual environment:

    virtualenv --python=/usr/bin/python3 --system-site-package .venv

Activate virtual environment:

    source .venv/bin/activate

Install requirements:

    pip install -r requirements.txt

Set the INPUT_CONFIG_PATH environment variable (default: config-in).

    export INPUT_CONFIG_PATH=../qwc-docker/volumes/config-in

Configure environment:

    echo FLASK_ENV=development >.flaskenv

Start local service:

    python server.py

