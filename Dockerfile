FROM muhaftab/jmodelica:2.0
LABEL vendor="GOFLEX"
LABEL maintainer="muhaftab@cs.aau.dk"

# ENV is available inside the container
ENV PORT 5000
ENV FLS_PROFILE  container

# JModelica
#ENV JMODELICA_HOME /opt/jmodelica
#ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64
#ENV IPOPT_HOME=/opt/ipopt
ENV JMODELICA_HOME /root/JModelica
ENV JAVA_HOME /usr/lib/jvm/java-8-oracle
ENV IPOPT_HOME ${JMODELICA_HOME}/CoinIpoptBuild
ENV SUNDIALS_HOME ${JMODELICA_HOME}/ThirdParty/Sundials
ENV PYTHONPATH ${PYTHONPATH}:${JMODELICA_HOME}/Python
ENV LD_LIBRARY_PATH ${LD_LIBRARY_PATH}:${IPOPT_HOME}/lib:${SUNDIALS_HOME}/lib:${JMODELICA_HOME}/ThirdParty/CasADi/lib
ENV SEPARATE_PROCESS_JVM=${JAVA_HOME}

# Set the working directory to /app
WORKDIR /app

# Copy the required files into the container at /app
ADD main.py /app/main.py
ADD requirements.txt /app/requirements.txt
ADD resources /app/resources
ADD uwsgi-http.ini /app/uwsgi.ini
ADD app /app/app
ADD apidocs/build /app/static

# Install packages
RUN pip install -r requirements.txt

# Create a mount point on the native host.
VOLUME /tmp

# Port available to the world outside this container
EXPOSE ${PORT}

# Start the application when the container launches
RUN echo "#!/bin/bash \n python main.py --host 0.0.0.0 --port ${PORT} --log-level INFO --create-fmus" > ./entrypoint.sh
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
#ENTRYPOINT ["python", "main.py", "--host", "0.0.0.0", "--port", "echo ${port}", "--create-fmus"]
