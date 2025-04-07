FROM openjdk:8-jdk

# install python and pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

# install pyspark packages \
RUN pip3 install pyspark==3.5.5

# Download Kafka and MongoDB connectors
RUN wget -P /opt/spark/jars/ https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.2.0/kafka-clients-3.2.0.jar
RUN wget -P /opt/spark/jars/ https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.4.1/mongo-spark-connector_2.12-10.4.1.jar

# Set the Spark classpath
ENV SPARK_CLASSPATH="/opt/spark/jars/*"

# set the working directory
WORKDIR /app

# Copy the application code into the container
COPY src/main/python/main.py /app

# Set the entrypoint
ENTRYPOINT ["spark-submit" , "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0,org.mongodb.spark:mongo-spark-connector_2.12:3.0.1", "--master", "local[*]", "main.py"]