# Base image: Jupyter Notebook
FROM jupyter/base-notebook:latest

USER root

# ------------------------------
# 1️⃣ Install Java (required by Spark) and wget
# ------------------------------
RUN apt-get update && \
    apt-get install -y openjdk-11-jdk wget && \
    rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# ------------------------------
# 2️⃣ Install Spark 3.4.1 with Hadoop 3
# ------------------------------
RUN wget https://archive.apache.org/dist/spark/spark-3.4.1/spark-3.4.1-bin-hadoop3.tgz && \
    tar xvf spark-3.4.1-bin-hadoop3.tgz -C /opt && \
    mv /opt/spark-3.4.1-bin-hadoop3 /opt/spark && \
    rm spark-3.4.1-bin-hadoop3.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$SPARK_HOME/bin:$PATH

# ------------------------------
# 3️⃣ Install Python packages: PySpark, Delta Lake, findspark
# ------------------------------
RUN pip install --no-cache-dir pyspark==3.4.1 delta-spark findspark

# ------------------------------
# 4️⃣ Set permissions back to default Jupyter user
# ------------------------------
USER $NB_UID

# ------------------------------
# 5️⃣ Set working directory
# ------------------------------
WORKDIR /home/jovyan/work
