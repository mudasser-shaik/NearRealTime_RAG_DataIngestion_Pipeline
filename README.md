## RAG Data pipeline - near Real Time
The near real-time RAG ingestion pipeline designed to efficiently process events from Kafka, transform and embed them using advanced embedding models, and store the results in a vector database. 
The project leverages various technologies including Kafka, Spark/Apache Beam, OpenAI/Huggingface's BERT, and MongoDB-Atlas to create a robust and scalable solution for event ingestion and processing.

### Architecture Overview:
The architecture consists of the following key components:

1. Event Producer - Kafka Connect: 
   1. This component is responsible for producing events into the Kafka topic. It acts as a bridge between the data source and Kafka, ensuring that events are continuously streamed into the system.
2. Data Store - Kafka: 
   1. Kafka serves as the central messaging system where all events are stored temporarily. It allows for high-throughput and fault-tolerant event streaming, enabling the pipeline to handle large volumes of data efficiently.
3. ETL - Spark / Apache Beam: 
   1. This component is responsible for extracting, transforming, and loading (ETL) the data from Kafka. It processes the incoming events in real-time, applying necessary transformations to prepare the data for embedding.
4. Embedding Model - OpenAI/Huggingface's BERT: 
   1. After the ETL process, the transformed data is passed to the embedding model. This model generates vector embeddings for the events, capturing their semantic meaning and enabling advanced search and retrieval capabilities.
5. Vector Database - MongoDB: 
   1. Finally, the embedded data is stored in MongoDB, which serves as a vector database. This allows for efficient storage and retrieval of high-dimensional data, facilitating quick access to the embedded events for downstream applications.

The overview of the near real-time RAG ingestion pipeline, highlighting the flow of data from event production to storage in a vector database. By utilizing Kafka for event streaming, Spark/Apache Beam for ETL, and BERT for embedding, this pipeline is designed to handle real-time data processing efficiently and effectively.
![Architecture Diagram.png](src%2Fmain%2Fpython%2Fresources%2FArchitecture_diagram.png)

### Prerequisites
#### Kafka connect Deployment:
For this example poc we use Kafkaconnect - `Standalone mode` , for Prod use `Distributed mode`.
For details about deploying and managing Confluent Platform in a Kubernetes environment, see [Confluent for Kubernetes](https://docs.confluent.io/operator/current/) .

##### How does your Data pipeline react to Handling errors ?
1. Fail fast and abort
2. Silently Ignore the bad messages.
3. Alert and Route messages to a dead letter queue.

Ideology, `Fail-Fast` is a common practice for handling errors. Sometimes you may want to stop processing as soon as an error occurs.
Perhaps encountering bad data is a symptom of problems upstream that must be resolved, and there’s no point in continuing to try processing other messages.

In real life the better option is (3. Alert and Route messages to a dead letter queue) 

i.e, Valid messages are processed as normal, and the pipeline keeps on running. 
Invalid messages can then be inspected from the dead letter queue, and ignored or fixed and reprocessed as required.
Kafka connect has the parameter 

```shell
errors.tolerance = all
errors.deadletterqueue.topic.name = topic-deadletterqueue
errors.deadletterqueue.topic.replication.factor = 3
errors.deadletterqueue.context.headers.enable = true

```
[Kafka-connect deep dive error handling dead letter queues](https://www.confluent.io/blog/kafka-connect-deep-dive-error-handling-dead-letter-queues/?session_ref=https://www.google.com/&_ga=2.154346360.1369169704.1741979164-580332930.1741979164&_gl=1*yu9tfc*_gcl_au*MTQ4NTc0NjczOS4xNzQxOTc5MTY0*_ga*NTgwMzMyOTMwLjE3NDE5NzkxNjQ.*_ga_D2D3EGKSGD*MTc0MTk3OTE2NC4xLjAuMTc0MTk3OTE2NC42MC4wLjA.)

###### **Steps:**
1. Recording the failure reason for a message: `Message headers`
2. Recording the failure reason for a message: `Log` and created `logbased-alerts`
3. Monitor DLQ topic
4. Processing messages from a DLQ topic


## Create Topic 
```shell
 kcat -b localhost:29092 -C -t product-updates -p 1 -r 1
```

## Schema registry 
Json Schema of product-updates : 
1. Schema : [product_schema.json](src%2Fmain%2Fpython%2Fresources%2Fproduct_schema.json)
2. namespace : `product`
3. topic name : `product-updates`

## Kafka connect - Datagen connector 
DataGen to generate the stream of events 

Run the connector: 
```shell
curl -X POST http://localhost:8083/connectors -H "Content-Type: application/json" -d @src/main/python/resources/datagen-product-config.json
```

Check status :
```shell
curl http://localhost:8083/connectors/datagen-products/status
```
Expected Result:
```shell
{"name":"datagen-products","connector":{"state":"RUNNING","worker_id":"connect:8083"},"tasks":[{"id":0,"state":"RUNNING","worker_id":"connect:8083"}],"type":"source"}% 
```

If you need to manage this connector in the future, here are some useful commands:
- To pause: `curl -X PUT http://localhost:8083/connectors/datagen-products/pause`
- To resume: `curl -X PUT http://localhost:8083/connectors/datagen-products/resume`
- To restart: `curl -X POST http://localhost:8083/connectors/datagen-products/restart`
- To delete: `curl -X DELETE http://localhost:8083/connectors/datagen-products`

Check if the connector `datagen` exists :
```shell
 curl http://localhost:8083/connector-plugins
```

### Kafka Connect Product Connector
```shell
 curl -X POST -H "Content-Type: application/json" --data @product-event-generator/src/main/java/resources/product-event-generator-config.json http://localhost:8083/connectors
```
Output :
```shell
{"name":"product-event-generator","config":{"connector.class":"com.kafka.connect.ProductEventSourceConnector","tasks.max":"1","topic":"product_events","key.converter":"org.apache.kafka.connect.storage.StringConverter","value.converter":"org.apache.kafka.connect.json.JsonConverter","value.converter.schemas.enable":"false","name":"product-event-generator"},"tasks":[],"type":"source"}
```

#### Run the connector in Docker Compose
Here is an example of how to run the kafka-connect-datagen connector with the provided `docker-compose.yml` file. If you want to use a different Docker image tag, be sure to modify appropriately in the `docker-compose.yml` file.

```shell
docker-compose up -d \
--build curl -X POST -H "Content-Type: application/json" \
--data @src/main/python/resources/datagen-product-config.json http://localhost:8083/connectors
```

```shell
docker-compose exec connect kafka-console-consumer \
--topic product --bootstrap-server kafka:29092  \
--property print.key=true --max-messages 5 --from-beginning
```

### Troubleshoot 
1. Check if the port 8083 is not available. `lsof -i :8083`
2. Inspect the Docker container `docker container inspect connect`
3. Check if the Kafka connect cluster is running 
    ```shell
        % curl -s http://localhost:8083/ || echo "Kafka Connect is not running"
        {"version":"7.6.0-ce","commit":"5d842885c76a15f7","kafka_cluster_id":"q-ulh2GlR7Glkp-UEQAzYg"}
   ```


## Run Spark job in Kuberenetes cluster

1. Create Docker image for the Spark application - [Dockerfile](Dockerfile)
2. Build the Docker image
   ```shell
        docker build -t spark-rag-ingest-pipeline:1.0.0 -f Dockerfile .
    ```
3. Push the Docker image to the Docker hub registry
   1. Create a Repo: To create a repository in Docker Hub, you'll need to follow these steps:
      1. First, if you haven't already, create a Docker Hub account at https://hub.docker.com/
      2. Once you have an account, you can create a repository in two ways:
         A. Through the Docker Hub website:
         - Log in to Docker Hub
         - Click on "Create Repository" button
         - Choose a name for your repository
         - Set the visibility (Public or Private)
         - Add a description (optional)
         - Click "Create"
         B. Using the Docker CLI:
         - Run the following command to create a repository:
         ```shell
            docker login
            docker tag spark-rag-ingest-pipeline:1.0.0 mudasser78/spark-rag-ingest-pipeline:1.0.0
            docker push mudasser78/spark-rag-ingest-pipeline:1.0.0
         ```
      3. The repository will be automatically created when you push your first image - [mudasser78/spark-rag-ingest-pipeline](https://hub.docker.com/repository/docker/mudasser78/spark-rag-ingest-pipeline/general) 
      4. Important notes:
         - Public repositories are free and unlimited
         - Private repositories may have limitations depending on your account type
         - Repository names should be lowercase
         - Valid characters are: letters, numbers, hyphens (-), and underscores (_)
4. Deploy the Spark application in the Kubernetes cluster
2. Submit the Spark job to the Kubernetes cluster
3. Monitor the Spark job in the Kubernetes cluster

```shell
kubectl apply -f spark-job.yaml
```