# Flexible Load Simulator

Flexible Load Simulator (FLS) for the Automatic Trading Platform (ATP) of the GOFLEX Project. FLS allows to create and manage a variety of simulated loads.

**Note**: the following commands should be executed from within the root of this repository.

## API

Detailed documentation of the API can be found by navigating to the root of the server. For example, if server is running on `port 5000` of `localhost`, then API docs can be accessed by navigating to `http://localhost:5000`.

### Generate Static API Docs

```bash
# generate static api docs which will be copied to the docker image during next command
cd apidocs && bundle exec middleman build --clean && cd -
```

## Installation

We describe how to setup and launch FLS using a)- docker, b)- from scratch.

### Installation using docker

It's very easy to setup and run the app with docker. All you need to do is build a docker image, then either run it in a container locally or push the image to a remote server and run it there. You must install `docker` and `docker-compose` both locally and on remote server if not installed already. 

* Install Docker on [Ubuntu 16](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-16-04) or [Ubuntu 18](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-18-04)

* Install Docker Compose

  ```bash
  sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
  sudo chmod +x /usr/local/bin/docker-compose
  docker-compose --version
  ```````

#### Build docker image

```bash
docker-compose build
```

#### Push docker image to a remote private docker registry

```bash
# one-time login to private docker registry
docker login repo.treescale.com # it will ask for username and password

docker-compose push
```

#### On remote server, pull and run docker image from private registry

```bash
# copy docker-compose.yml to remote server
scp docker-compose.yml <username>@<remote-server-address>:/remote/dir/path

# login to remote server and navigate to the directory containing docker-compose.yml
ssh <username>@<remote-server-address>
cd /remote/dir/path

# one-time login to private docker registry
docker login repo.treescale.com # you will need to install docker if not installed already

docker-compose pull
```

Alternatively, you can perform one-time login to the private docker registry on the remote server as shown above, then
directly deploy container from your local machine as follows:
```bash
# Note: you must be logged in to the private docker registry to run these commands
cat docker-compose | ssh <username>@<remote-server-address> "docker-compose -f - pull"
cat docker-compose | ssh <username>@<remote-server-address> "docker-compose -f - up -d"
```

#### Remove unnecessary docker images from remote server

```bash
ssh <username>@<remote-server-address> "docker system prune -f"
```

#### Run docker Image in a container

```bash
# launch a container by navigating to the directory containing docker-compose.yml and running this command
docker-compose -d up

# attach to the running container
docker attach fls-server-container

# detach from the running container
CTRL-p, CTRL-q
```

After the container is up and running, the FLS server can be accessed on `port 5000`.

### Manually run with `uwsgi`

Start uwsgi from command line

```bash
uwsgi -s flsserver.sock --http 0.0.0.0:5000 --module main --callable app
```
Start uwsgi with `ini` file

```bash
uwsgi --ini uwsgi-http.ini
```


### Installation from scratch

First, we need to install JModelica from source. From within the root of this repository, run the following commands to install JModelica into `~/JModelica`.

  ```bash
  cd scripts && bash installJModelica.sh /path/to/install/dir
  ```

When testing JModelica, you might get the following error

>      AttributeError: KeepLastStream instance has no attribute 'close'

To fix this problem add the following method to `KeepLastStream` class in `/path/to/JModelica/Python/pymodelica/compiler_logging.py` ([ref](http://www.jmodelica.org/27909)):

  ```python
  def close(self):
    self.stream.close()
  ```

Setup virtual environment

  ```bash
  sudo pip install virtualenv
  virtualenv .venv
  ```

Set JModelica environment variables in `virtualenvironment`. **Please set `JMODELICA_HOME` to the correct install location.**

  ```bash
  tee -a .venv/bin/activate << END

  # JModelica
  export JMODELICA_HOME=/path/to/JModelica
  export JAVA_HOME=/usr/lib/jvm/java-8-oracle
  export IPOPT_HOME=\$JMODELICA_HOME/CoinIpoptBuild
  export SUNDIALS_HOME=\$JMODELICA_HOME/ThirdParty/Sundials
  export PYTHONPATH=\$PYTHONPATH:\$JMODELICA_HOME/Python
  export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:\$IPOPT_HOME/lib:\$SUNDIALS_HOME/lib:\$JMODELICA_HOME/ThirdParty/CasADi/lib
  export SEPARATE_PROCESS_JVM=\$JAVA_HOME
  END
  ```

Also unset JModelica environment variables on `deactivate`

  ```bash
  sed -i '/deactivate () {/a \
      # JModelica \
      unset JAVA_HOME \
      unset JMODELICA_HOME \
      unset IPOPT_HOME \
      unset SUNDIALS_HOME \
      unset PYTHONPATH \
      unset LD_LIBRARY_PATH \
      unset SEPARATE_PROCESS_JVM \
  ' .venv/bin/activate
  ```

Activate virtual environment

  ```bash
  sudo apt install libmysqlclient-dev
  source .venv/bin/activate
  ```

Install required packages

  ```bash
  pip install -r requirements.txt
  ```

Create the required MySQL database. Run this inside MySQL shell

  ```mysql
  create database flsdb;
  ```

## Usage

Start the simulator program

  ```bash
  python app.py
  
  # access over internet
  python app.py --host 0.0.0.0
  
  # full list of command line arguments
  python app.py --profile prod --host 0.0.0.0 --port 5000 --db-url mysql://username:password@host:port/db --create-fmus

  ```

Here `--host` defaults to `localhost`, and `--port` defaults to `5000`.

## Tips

How to de-activate virtual environment

  ```bash
  deactivate
  ```

Set environment variables in pycharm (because pycharm is a desktop app which is not a child of shell and env vars are defined in shell only)

  ```bash
  JAVA_HOME=/usr/lib/jvm/java-8-oracle
  JMODELICA_HOME=/home/username/JModelica
  IPOPT_HOME=/home/username/JModelica/CoinIpoptBuild
  SUNDIALS_HOME=/home/username/JModelica/ThirdParty/Sundials
  PYTHONPATH=:/home/username/JModelica/Python
  LD_LIBRARY_PATH=:/home/username/JModelica/CoinIpoptBuild/lib:/home/username/JModelica/ThirdParty/Sundials/lib:/home/username/JModelica/ThirdParty/CasADi/lib
  SEPARATE_PROCESS_JVM=/usr/lib/jvm/java-8-oracle
  ```


## Theory behind simulation of electric loads

The following appliance models have been implemented in Modelica:

### Basic On-Off Models

1. _**On-off Model**_: This model has a certain fixed power consumption rate p<sub>on</sub> when active.

2. _**Exponential Decay Model**_: The power consumption rate follows an exponential decay curve, dropping from the initial surge power p<sub>peak</sub> to a stable power p<sub>active</sub> at a decay rate &lambda;.

  &emsp;&emsp; p(t) = p<sub>active</sub> + (p<sub>peak</sub> - p<sub>active</sub>)e<sup>-&lambda;t</sup>

3. _**Logarithmic Growth Model**_: The power consumption rate follows a logarithmic growth curve, starting with a level p<sub>base</sub> and a growth rate &lambda;.

  &emsp;&emsp; p(t) = p<sub>base</sub> + &lambda; &middot; lnt

The table below lists several example loads for simulation in our app. Other loads can be crated by varying the parameter combination within the allowed range.

| Load Name | Modelica Model | Parameters |
| --- | --- | --- |
| Lamp | On-Off | p<sub>on</sub>=40 |
| Toaster | Exponential Decay | p<sub>peak</sub>=1470, p<sub>active</sub>=1433, &lambda;=0.02 |
| Coffee Maker | Exponential Decay | p<sub>peak</sub>=990, p<sub>active</sub>=905, &lambda;=0.045 |
| Refrigerator | Exponential Decay | p<sub>peak</sub>=650.5, p<sub>active</sub>=126.19, &lambda;=0.27 |
| Air Conditioner | Logarithmic Growth | p<sub>base</sub>=2120.46, &lambda;=13.78 |
| Heat Pump | SISO Linear System | A=-0.01, B=0.002, C=1, D=0 |


## References

- [http://sites.psu.edu/symbolcodes/codehtml/#math](http://sites.psu.edu/symbolcodes/codehtml/#math)
- [https://www.keynotesupport.com/websites/greek-letters-symbols.shtml](https://www.keynotesupport.com/websites/greek-letters-symbols.shtml)
- [https://github.com/miguelgrinberg/REST-auth](https://github.com/miguelgrinberg/REST-auth)