create script for make testing mre easier 

project dir:

-Script
---main
---flow [which contain the flow manager[scenario], and flow files]
-----flow manager
---utils[which contains all utils of this script: mapping / dependencies / using config(generating tokens)]
---config (generating tokens) if needed
---model contains the scenario points (product/plan/api/product plan price) / we are think to make them .py
---save .yaml/.json (it have the scenario connection {{response from api create}} to {{product request}} etc...)

for all scenario we want to send (the scenario[flow],list of its model, token if needed, the yaml or xml file  we will save in)

our project dgate[which is all in java] --> our script should be python

util are handle the models [mapping see who will create first according to dependencies]

-------------------------------

Calls your Java system's endpoints in a chain (sequence).
Each response is needed as part of the next request (n → n+1).
If a user wants to manually POST at step (n+1) without having to manually call all the previous ones (1 → n), the script should automatically handle all previous calls behind the scenes.
It should reuse responses automatically for the next calls.
Support POST and GET.
----------

Example:
Call /endpoint1 → Get response f
Call /endpoint2, send f → Get response g
Call /endpoint3, send g → etc.
-------------

[img.png](API Request Editor.png)

[img_1.png](Full Scenario View.png)

----------

the yaml will be some thing like this:
name: "User Registration Flow"
id: reg_flow_123
description: "A test scenario to validate the complete user registration process"
version: 1.0
created_at: "2025-04-30T10:15:30Z"
updated_at: "2025-04-30T11:32:14Z"
environment:
test_email: "test@example.com"
test_password: "securePassword123"
verification_code: "123456"
base_url: "https://api.example.com"
requests:
- name: "Create User"
  method: POST
  url: "{{env.base_url}}/users"
  headers:
  Content-Type: "application/json"
  Accept: "application/json"
  body: |
  {
  "email": "{{env.test_email}}",
  "password": "{{env.test_password}}"
  }
  save_as: "user_data"
  assertions:
    - type: "status_code"
      value: 201
    - type: "json_path"
      path: "$.id"
      exists: true
- name: "Verify Email"
  method: POST
  url: "{{env.base_url}}/verify"
  headers:
  Content-Type: "application/json"
  Accept: "application/json"
  body: |
  {
  "user_id": "{{user_data.id}}",
  "code": "{{env.verification_code}}"
  }
  save_as: "verification_result"
  assertions:
    - type: "status_code"
      value: 200
    - type: "json_path"
      path: "$.status"
      equals: "verified"
- name: "Login User"
  method: POST
  url: "{{env.base_url}}/login"
  headers:
  Content-Type: "application/json"
  Accept: "application/json"
  body: |
  {
  "email": "{{env.test_email}}",
  "password": "{{env.test_password}}"
  }
  save_as: "login_data"
  assertions:
    - type: "status_code"
      value: 200
    - type: "json_path"
      path: "$.token"
      exists: true
------------------------

but it will be generally created for all scenario [flow]

------------------------

