---
title: API Reference

#language_tabs: # must be one of https://git.io/vQNgJ
#  - shell
#  - python

toc_footers:
  - <a href='#'>Flexible Load Simulator (FLS)</a>
  - A part of the <a href='www.goflex-project.eu'>GOFLEX project</a>

#includes:
#  - errors

search: true
---

# Introduction

Welcome to the Flexible Load Simulator (FLS). On this page you can find the REST API details, which allows to manage a variety of simulated loads supported by FLS. For each endpoint, the page describes the required parameters and provides an example. The navigation panel to left lists all the endpoints divided into groups. The endpoints in a group can be revealed by clicking on the group name (e.g., clicking on User Management).

<aside class="notice">
In the code examples, replace 'localhost' with the server address where FLS is running!
</aside>

# User Management

## Register New User

```shell
  curl -X POST -H "Content-Type: application/json" \
  -d '{"username":"username", "password":"password", "first_name":"test", "last_name":"user", "email":"test@email.com"}' \
  "http://localhost:5000/api/v1.0/users"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "auth": {
      "exp": "Fri, 21 Dec 2018 20:01:32 GMT", 
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NsYWltcyI6eyJyb2xlcyI6WyJlbmQtdXNlciJdfSwianRpIjoiNjNjZGUwY2UtM2ZmNy00MDczLWE0ZDctYzgwZThiNDhhNTQ4IiwiZXhwIjoxNTQ1NDIyNDkyLCJmcmVzaCI6ZmFsc2UsImlhdCI6MTU0NTQxODg5MiwidHlwZSI6ImFjY2VzcyIsIm5iZiI6MTU0NTQxODg5MiwiaWRlbnRpdHkiOiJ1c2VybmFtZSJ9.43LaTPUezJSbly4akK8rkZrZui47FyCNmDf6o9Kl9LU"
    }, 
    "user": {
      "devices": [], 
      "email": "test@email.com", 
      "first_name": "test", 
      "id": 14, 
      "last_name": "user", 
      "max_devices": 10, 
      "no_of_devices": 0, 
      "roles": [
        {
          "description": null, 
          "name": "end-user"
        }
      ], 
      "username": "username"
    }
  }, 
  "msg": "new user created", 
  "status": "success"
}

```

This endpoint is used to register a new user.

### HTTP Request

`POST http://localhost:5000/api/v1.0/users`

### Request Body (JSON)

Parameter | Description
--------- | -----------
username | The unique user name
password | The password required to login the user or request a new token
first_name | Given Name
last_name | Surname
email | Unique email address

## Login / New Token

```shell
  curl -X POST --user username:password "http://localhost:5000/api/v1.0/users/login"
```

> The above command returns the following JSON response:

```json
{
  "exp": "Fri, 21 Dec 2018 18:59:36 GMT", 
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2NsYWltcyI6eyJyb2xlcyI6WyJlbmQtdXNlciIsImFkbWluIl19LCJqdGkiOiIxNjhjOTA3OS1kOTMzLTQ5YTQtOWViYi0zMWYwMzk5ZjUwN2UiLCJleHAiOjE1NDU0MTg3NzYsImZyZXNoIjpmYWxzZSwiaWF0IjoxNTQ1NDE1MTc2LCJ0eXBlIjoiYWNjZXNzIiwibmJmIjoxNTQ1NDE1MTc2LCJpZGVudGl0eSI6ImFkbWluIn0.DB8IzqJHgT-ICeOKKa3eS_hysEhfAvYUx3QsDHa7y4M", 
  "username": "admin"
}
```

This endpoint is used to login a user or get a new token.

### HTTP Request

`POST http://localhost:5000/api/v1.0/users/login`

<aside class="success">
Remember — you must login before making any of the API calls below!
</aside>

## Add a Role

```shell
  curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"username":"username", "role":"admin"}' \
  "http://localhost:5000/api/v1.0/users/add_role"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "updated_roles": [
      {
        "description": null, 
        "name": "end-user"
      }, 
      {
        "description": null, 
        "name": "admin"
      }
    ]
  }, 
  "msg": "added 'admin' role for 'username'", 
  "status": "success"
}
```

This endpoint is used to add a new role to a user.

### HTTP Request

`POST http://localhost:5000/api/v1.0/users/add_role`

### Request Body (JSON)

Parameter | Description
--------- | -----------
username | The user name whose roles are to be modified
role | one of ("admin", "developer", "end-user")

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

<aside class="warning">
Only admins can call this API
</aside>

## Revoke a Role

```shell
  curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"username":"username", "role":"admin"}' \
  "http://localhost:5000/api/v1.0/users/revoke_role"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "updated_roles": [
      {
        "description": null, 
        "name": "end-user"
      }
    ]
  }, 
  "msg": "revoked 'admin' role from 'username'", 
  "status": "success"
}
```

This endpoint is used to revoke a given role from a user.

### HTTP Request

`POST http://localhost:5000/api/v1.0/users/revoke_role`

### Request Body (JSON)

Parameter | Description
--------- | -----------
username | The user name whose roles are to be modified
role | one of ("admin", "developer", "end-user")

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## Get User Details

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:5000/api/v1.0/users"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "devices": [], 
    "email": "admin@email.com", 
    "first_name": "Admin", 
    "id": 13, 
    "last_name": "User", 
    "max_devices": 10, 
    "no_of_devices": 0, 
    "roles": [
      {
        "description": null, 
        "name": "end-user"
      }, 
      {
        "description": null, 
        "name": "admin"
      }
    ], 
    "username": "admin"
  }, 
  "msg": "user found", 
  "status": "success"
}
```

This endpoint to get details of the currently logged in user

### HTTP Request

`GET http://localhost:5000/api/v1.0/users`

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## Update User

```shell
  curl -X PUT -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"password":"new-password", "first_name":"new-first-name", "last_name":"new-last-name", "email":"new-mail@email.com"}' \
  "http://localhost:5000/api/v1.0/users"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "user": {
      "devices": [], 
      "email": "new-mail@email.com", 
      "first_name": "new-first-name", 
      "id": 13, 
      "last_name": "new-last-name", 
      "max_devices": 10, 
      "no_of_devices": 0, 
      "roles": [
        {
          "description": null, 
          "name": "end-user"
        }, 
        {
          "description": null, 
          "name": "admin"
        }
      ], 
      "username": "admin"
    }
  }, 
  "status": "success"
}
```

This endpoint is used to update a user.

### HTTP Request

`PUT http://localhost:5000/api/v1.0/users`

### Request Body (JSON)

Parameter | Description
--------- | -----------
password | New password
first_name | New given name
last_name | New Surname
email | New Unique email address

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## Delete User

```shell
  curl -X DELETE -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:5000/api/v1.0/users"
```

> The above command returns the following JSON response:

```json
{
  "msg": "deleted user with username: 'admin'", 
  "status": "success"
}
```

This endpoint is used to delete a user.

### HTTP Request

`DELETE http://localhost:5000/api/v1.0/users`

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## Get ALL Users Details

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:5000/api/v1.0/users/all"
```

> The above command returns the following JSON response:

```json
{
  "data": [
    {
      "devices": [
        {
          "device_id": "98c8b94fbf8a408eabbc8b0d98097bf7", 
          "device_model": {
            "model_name": "ExponentialDecay", 
            "params": {
              "lambda": 0.045, 
              "p_active": 905, 
              "p_peak": 990
            }
          }, 
          "device_name": "CoffeeMaker", 
          "device_state": "active", 
          "id": 15, 
          "user_id": 6
        }
      ], 
      "email": "localhost", 
      "first_name": "GoFLEX", 
      "id": 6, 
      "last_name": "User", 
      "max_devices": 10, 
      "no_of_devices": 1, 
      "roles": [
        {
          "description": null, 
          "name": "admin"
        }
      ], 
      "username": "goflex-foa"
    }, 
    {
      "devices": [], 
      "email": "muhaftab@cs.aau.dk", 
      "first_name": "Muhammad", 
      "id": 12, 
      "last_name": "Aftab", 
      "max_devices": 10, 
      "no_of_devices": 0, 
      "roles": [
        {
          "description": null, 
          "name": "end-user"
        }, 
        {
          "description": null, 
          "name": "admin"
        }
      ], 
      "username": "muhaftab"
    }, 
    {
      "devices": [], 
      "email": "test@email.com", 
      "first_name": "test", 
      "id": 14, 
      "last_name": "user", 
      "max_devices": 10, 
      "no_of_devices": 0, 
      "roles": [
        {
          "description": null, 
          "name": "end-user"
        }
      ], 
      "username": "username"
    }, 
    {
      "devices": [], 
      "email": "admin@email.com", 
      "first_name": "test", 
      "id": 15, 
      "last_name": "user", 
      "max_devices": 10, 
      "no_of_devices": 0, 
      "roles": [
        {
          "description": null, 
          "name": "end-user"
        }, 
        {
          "description": null, 
          "name": "admin"
        }
      ], 
      "username": "admin"
    }
  ], 
  "msg": "found 4 users", 
  "status": "success"
}
```

This endpoint gets details of all users

### HTTP Request

`GET http://localhost:5000/api/v1.0/users/all`

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

<aside class="warning">
Only admins can call this API
</aside>

# Simulated Devices

## Supported Devices

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:5000/api/v1.0/devices/types/available"
```

> The above command returns the following JSON response:

```json
{
  "data": [
    {
      "name": "OnOff", 
      "params": {
        "p_on": {
          "default": 100, 
          "max": 5000, 
          "min": 0
        }
      }
    }, 
    {
      "name": "ExponentialDecay", 
      "params": {
        "lambda": {
          "default": 0, 
          "max": 10, 
          "min": -10
        }, 
        "p_active": {
          "default": 100, 
          "max": 5000, 
          "min": 0
        }, 
        "p_peak": {
          "default": 100, 
          "max": 5000, 
          "min": 0
        }
      }
    }, 
    {
      "name": "LogarithmicGrowth", 
      "params": {
        "lambda": {
          "default": 0, 
          "max": 10, 
          "min": -10
        }, 
        "p_base": {
          "default": 100, 
          "max": 5000, 
          "min": 0
        }
      }
    }, 
    {
      "name": "SISOLinearSystem", 
      "params": {
        "A": {
          "default": -0.01, 
          "max": -0.01, 
          "min": -0.01
        }, 
        "B": {
          "default": 0.02, 
          "max": 0.02, 
          "min": 0.02
        }, 
        "C": {
          "default": 1, 
          "max": 1, 
          "min": 1
        }, 
        "D": {
          "default": 0, 
          "max": 0, 
          "min": 0
        }
      }
    }
  ], 
  "msg": "found 4 available models", 
  "status": "success"
}
```

This endpoint gets the list of simulated loads implemented in FLS.

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/types/available`

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## Example Devices

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:5000/api/v1.0/devices/types/examples"
```

> The above command returns the following JSON response:

```json
{
  "data": [
    {
      "device_name": "Lamp", 
      "model_name": "OnOff", 
      "params": {
        "p_on": 40
      }
    }, 
    {
      "device_name": "Toaster", 
      "model_name": "ExponentialDecay", 
      "params": {
        "lambda": 0.02, 
        "p_active": 1433, 
        "p_peak": 1470
      }
    }, 
    {
      "device_name": "CoffeeMaker", 
      "model_name": "ExponentialDecay", 
      "params": {
        "lambda": 0.045, 
        "p_active": 905, 
        "p_peak": 990
      }
    }, 
    {
      "device_name": "Refrigerator", 
      "model_name": "ExponentialDecay", 
      "params": {
        "lambda": 0.27, 
        "p_active": 126.19, 
        "p_peak": 650.5
      }
    }, 
    {
      "device_name": "AirConditioner", 
      "model_name": "LogarithmicGrowth", 
      "params": {
        "lambda": 13.78, 
        "p_base": 2120.46
      }
    }, 
    {
      "device_name": "HeatPump", 
      "model_name": "SISOLinearSystem", 
      "params": {
        "A": -0.01, 
        "B": 0.002, 
        "C": 1, 
        "D": 0
      }
    }
  ], 
  "msg": "found 6 example devices", 
  "status": "success"
}
```

Returns an example list of devices whose parameters are already set.

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/types/examples`

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## Create New Simulated Device

```shell
  curl -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_name": "CoffeeMaker1", "model_name": "ExponentialDecay", "params": {"lambda": 0.045, "p_active": 905, "p_peak": 990 }}' \
  "http://localhost:5000/api/v1.0/devices"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "device_id": "ea97f9d5732e49549a78bd209ddb3afa", 
    "device_model": {
      "model_name": "ExponentialDecay", 
      "params": {
        "lambda": 0.045, 
        "p_active": 905, 
        "p_peak": 990
      }
    }, 
    "device_name": "CoffeeMaker1", 
    "device_state": "active", 
    "id": 16, 
    "user_id": 12
  }, 
  "msg": "created new device", 
  "status": "success"
}
```

Start simulating a new device for the given user

### HTTP Request

`POST http://localhost:5000/api/v1.0/devices`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_name | A user-defined valid string 
model_name | One of the available models supported by FLS
params | The required model parameters as JSON


<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## User's Simulated Devices

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices"
```

> The above command returns the following JSON response:

```json
{
  "data": [
    {
      "device_id": "ea97f9d5732e49549a78bd209ddb3afa", 
      "device_model": {
        "model_name": "ExponentialDecay", 
        "params": {
          "lambda": 0.045, 
          "p_active": 905, 
          "p_peak": 990
        }
      }, 
      "device_name": "CoffeeMaker", 
      "device_state": "active", 
      "id": 16, 
      "user_id": 12
    }
  ], 
  "msg": "device found for muhaftab", 
  "status": "success"
}
```

Returns list of all simulated devices for a user if `device_id` not provided in request body else return only requested
device

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices`

### Optional Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | Device Id if the user want ot retrieve only a single device else not needed

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

## All Simulated Devices for All Users

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:5000/api/v1.0/devices/all"
```

> The above command returns the following JSON response:

```json
{
  "data": [
    {
      "device_id": "98c8b94fbf8a408eabbc8b0d98097bf7", 
      "device_model": {
        "model_name": "ExponentialDecay", 
        "params": {
          "lambda": 0.045, 
          "p_active": 905, 
          "p_peak": 990
        }
      }, 
      "device_name": "CoffeeMaker", 
      "device_state": "active", 
      "id": 15, 
      "user_id": 6
    }, 
    {
      "device_id": "ea97f9d5732e49549a78bd209ddb3afa", 
      "device_model": {
        "model_name": "ExponentialDecay", 
        "params": {
          "lambda": 0.045, 
          "p_active": 905, 
          "p_peak": 990
        }
      }, 
      "device_name": "CoffeeMaker", 
      "device_state": "active", 
      "id": 16, 
      "user_id": 12
    }
  ], 
  "msg": "found 2 devices in db", 
  "status": "success"
}
```

Returns list of all simulated devices for all users

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/all`

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token
</aside>

<aside class="warning">
Only admins can call this API
</aside>


## Update a Simulated Device

```shell
  curl -X PUT -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>", device_name": "CoffeeMaker2", "model_name": "ExponentialDecay", "params": {"lambda": 0.145, "p_active": 205, "p_peak": 390 }}' \
  "http://localhost:5000/api/v1.0/devices"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "device_id": "ea97f9d5732e49549a78bd209ddb3afa", 
    "device_model": {
      "model_name": "ExponentialDecay", 
      "params": {
        "lambda": 0.145, 
        "p_active": 205, 
        "p_peak": 390
      }
    }, 
    "device_name": "CoffeeMaker2", 
    "device_state": "active", 
    "id": 16, 
    "user_id": 12
  }, 
  "msg": "updated device", 
  "status": "success"
}
```

Modify an existing simulated device for a user

### HTTP Request

`PUT http://localhost:5000/api/v1.0/devices`

### Request Body (JSON)

Parameter   | Description
---------   | -----------
device_id   | The ID of the device to update
device_name | New device name for the device with given Id
model_name  | New model name for the device with given Id
params      | The updated model parameters as JSON

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>

## Delete Simulated Device 

```shell
  curl -X DELETE -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices"
```

> The above command returns the following JSON response:

```json
{
  "msg": "deleted device with device_id 'ea97f9d5732e49549a78bd209ddb3afa'", 
  "status": "success"
}
```

Deletes a given device for a user

### HTTP Request

`DELETE http://localhost:5000/api/v1.0/devices`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | The ID of the device to delete

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>

## Active Simulated Devices 

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:5000/api/v1.0/devices/active"
```

> The above command returns the following JSON response:

```json
{
  "data": [
    {
      "device_id": "295370d9079744a7b74e02a1bf865acf", 
      "device_model": {
        "model_name": "ExponentialDecay", 
        "params": {
          "lambda": 0.045, 
          "p_active": 905, 
          "p_peak": 990
        }
      }, 
      "device_name": "CoffeeMaker1", 
      "device_state": "active", 
      "id": 17, 
      "user_id": 12
    }, 
    {
      "device_id": "a175b24f4b0349308bbbf049fb6487de", 
      "device_model": {
        "model_name": "ExponentialDecay", 
        "params": {
          "lambda": 0.045, 
          "p_active": 905, 
          "p_peak": 990
        }
      }, 
      "device_name": "CoffeeMaker2", 
      "device_state": "active", 
      "id": 18, 
      "user_id": 12
    }
  ], 
  "msg": "found 2 active devices for 'muhaftab'", 
  "status": "success"
}
```

Returns list of active (running) simulated devices for a user

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/active`

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token.
</aside>

## Simulated Device State

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices/state"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "power_state": "active"
  }, 
  "msg": "device power state fetched", 
  "status": "success"
}
```

Get the on/off or active/inactive status for the given device

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/state`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | The ID of the device whose status is to be retrieved

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>

## Start Simulated Device

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices/start"
```

> The above command returns the following JSON response:

```json
{
  "msg": "turned on device with device_id '295370d9079744a7b74e02a1bf865acf'", 
  "status": "success"
}
```

Turn on a simulated device

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/start`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | The ID of the device to turn on

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>

## Stop Simulated Device

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices/stop"
```

> The above command returns the following JSON response:

```json
{
  "msg": "turned off device with device_id '295370d9079744a7b74e02a1bf865acf'", 
  "status": "success"
}
```

Turn off a simulated device

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/stop`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | The ID of the device to turn off

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>

## Simulated Device Energy

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices/energy"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "energy": 0.059076393615
  }, 
  "msg": "fetched device energy consumption since start of current simulation session", 
  "status": "success"
}
```

Get the energy consumption (kWh or Wh) for the given device since start of current simulation session.

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/energy`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | The ID of the device whose energy consumption is to be retrieved

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>

## Simulated Device Live Power

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices/live_power"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "live_power": 905.0
  }, 
  "msg": "fetched device live power consumption directly from simulation (i.e., not from db)", 
  "status": "success"
}
```

Get the live power consumption for the given device.

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/live_power`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | The ID of the device whose live power consumption is to retrieved

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>

## Historical Power Consumption

```shell
  curl -X GET -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -d '{"device_id": "<DEVICE_ID>"}' \
  "http://localhost:5000/api/v1.0/devices/consumption"
```

> The above command returns the following JSON response:

```json
{
  "data": {
    "consumption": [
     {
        "energy": 0.0872319, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:39:47 GMT"
      }, 
      {
        "energy": 0.0897458, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:39:57 GMT"
      }, 
      {
        "energy": 0.0922597, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:40:07 GMT"
      }, 
      {
        "energy": 0.0947736, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:40:17 GMT"
      }, 
      {
        "energy": 0.0972875, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:40:27 GMT"
      }, 
      {
        "energy": 0.0998014, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:40:37 GMT"
      }, 
      {
        "energy": 0.102315, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:40:47 GMT"
      }, 
      {
        "energy": 0.104829, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:40:57 GMT"
      }, 
      {
        "energy": 0.132733, 
        "power": 905.0, 
        "status": true, 
        "timestamp": "Sat, 22 Dec 2018 00:42:47 GMT"
      }
    ]
  }, 
  "msg": "fetched 54 consumption data records for device with device_id '295370d9079744a7b74e02a1bf865acf'", 
  "status": "success"
}

```

Get historical power consumption data for a device

### HTTP Request

`GET http://localhost:5000/api/v1.0/devices/consumption`

### Request Body (JSON)

Parameter | Description
--------- | -----------
device_id | The ID of the device whose historical consumption data is to be retrieved

<aside class="notice">
In the <code>curl</code> example, you need to change &lt;ACCESS_TOKEN&gt; with a valid token and &lt;DEVICE_ID&gt; with the actual device.
</aside>



# Errors

The FLS API uses the following error codes:

Error Code | Meaning
---------- | -------
400 | Bad Request -- Your request is invalid.
401 | Unauthorized -- Your API key is wrong.
403 | Forbidden -- The requested resource is hidden for administrators only.
404 | Not Found -- The specified resource could not be found.
405 | Method Not Allowed -- You tried to access a resource with an invalid method.
406 | Not Acceptable -- You requested a format that isn't json.
410 | Gone -- The resource requested has been removed from our servers.
418 | I'm a teapot.
429 | Too Many Requests -- You're making too many requests! Slow down!
500 | Internal Server Error -- We had a problem with our server. Try again later.
503 | Service Unavailable -- We're temporarily offline for maintenance. Please try again later.
