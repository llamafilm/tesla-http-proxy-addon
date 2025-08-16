"""Constants"""

SCOPES = 'openid offline_access vehicle_device_data vehicle_cmds vehicle_charging_cmds energy_device_data energy_cmds'
AUDIENCES = {
    'North America, Asia-Pacific': 'https://fleet-api.prd.na.vn.cloud.tesla.com',
    'Europe, Middle East, Africa': 'https://fleet-api.prd.eu.vn.cloud.tesla.com',
    'China'                      : 'https://fleet-api.prd.cn.vn.cloud.tesla.cn'
}
TESLA_AUTH_ENDPOINTS = {
    'North America, Asia-Pacific': 'https://auth.tesla.com',
    'Europe, Middle East, Africa': 'https://auth.tesla.com',
    'China'                      : 'https://auth.tesla.cn'
}
TESLA_AK_ENDPOINTS = {
    'North America, Asia-Pacific': 'https://tesla.com',
    'Europe, Middle East, Africa': 'https://tesla.com',
    'China'                      : 'https://tesla.cn'
}
