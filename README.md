# Damn Vulnerable GraphQL Application
Damn Vulnerable GraphQL Application is an intentionally vulnerable implementation of Facebook's GraphQL technology, to learn and practice GraphQL Security.


<p align="center">
  <img src="https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application/blob/master/static/images/dvgql_logo.png?raw=true" width="alt="DVGA"/>
</p>

# Table of Contents
* [About DVGA](#about)
* [Operation Modes](#operation-modes)
* [Scenarios](#scenarios)
* [Prerequisites](#prerequisites)
* [Installation](#installation)
  * [Installation - Docker](#docker)
  * [Installation - Server](#server)
* [Screenshots](#screenshots)
* [Maintainers](#maintainers)
* [Mentions](#mentions)
* [Disclaimer](#disclaimer)
* [License](#license)

# About DVGA
Damn Vulnerable GraphQL is a deliberately weak and insecure implementation of GraphQL that provides a safe environment to attack a GraphQL application, allowing developers and IT professionals to test for vulnerabilities.

DVGA has numerous flaws, such as Injections, Code Executions, Bypasses, Denial of Service, and more. See the full list under the [Scenarios](#scenarios) section.

# Operation Modes
DVGA supports Beginner and Expert level game modes, which will change the exploitation difficulty.

# Scenarios
* **Denial of Service**
  * Batch Query Attack
  * Deep Recursion Query Attack
  * Resource Intensive Query Attack
* **Information Disclosure**
  * GraphQL Introspection
  * GraphiQL Interface
  * GraphQL Field Suggestions
  * Server Side Request Forgery
* **Code Execution**
  * OS Command Injection #1
  * OS Command Injection #2
* **Injection**
  * Stored Cross Site Scripting
  * HTML Injection
* **Authorization Bypass**
  * GraphQL Interface Protection Bypass
  * GraphQL Query Deny List Bypass
* **Miscellaneous**
  * GraphQL Query Weak Password Protection
  * Arbitrary File Write // Path Traversal

# Prerequisites
The following Python3 libraries are required:
* Python3
* Flask
* Flask-SQLAlchemy
* Graphene
* Graphene-SQLAlchemy

See [requirements.txt](requirements.txt) for dependencies.


# Installation
## Docker
### Clone the repository
`git clone git@github.com:dolevf/Damn-Vulnerable-GraphQL-Application.git && cd Damn-Vulnerable-GraphQL-Application`

### Build the Docker image
`docker build -t dvga .`

### Create a container from the image
`docker run -t -p 5000:5000 -e WEB_HOST=0.0.0.0 dvga`

In your browser, navigate to http://localhost:5000

Optionally, if you need the application to bind on a specific port or interface, use the following command:
`docker run -e WEB_HOST=0.0.0.0 -e WEB_PORT=8080 -t -p 8080:8080 dvga`


# Server
### Navigate to /opt
`cd /opt/`

### Clone the repository
`git clone git@github.com:dolevf/Damn-Vulnerable-GraphQL-Application.git && cd Damn-Vulnerable-GraphQL-Application`

### Install Requirements
`pip3 install -r requirements.txt`

### Run application
`python3 app.py`

In your browser, navigate to http://localhost:5000.

# Screenshots
![DVGA](https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application/blob/master/static/screenshots/index.png)
![DVGA](https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application/blob/master/static/screenshots/solution.png)
![DVGA](https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application/blob/master/static/screenshots/pastes.png)
![DVGA](https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application/blob/master/static/screenshots/create.png)

# Maintainers
* Dolev Farhi
* Connor McKinnon

# Mentions
TBA

# Disclaimer
DVGA is highly insecure, and as such, should not be deployed on internet facing servers. By default, the application is listening on 127.0.0.1 to avoid misconfigurations.

DVGA is intentionally flawed and vulnerable, as such, it comes with no warranties. By using DVGA, you take full responsibility for using it.

# License
It is distributed under the MIT License. See LICENSE for more information.

