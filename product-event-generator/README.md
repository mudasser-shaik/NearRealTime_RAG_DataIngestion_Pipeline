## Kafka Connect : Product Event Generator
This is a simple application that generates product events and sends them to a Kafka topic. 
The product events are generated at random intervals and are sent to the Kafka topic `product-events`. The product events are generated in the following format:
```json
{
  "product_id": 196444,
  "store_id": 17,
  "count": 5,
  "price": 71.13,
  "size": "extra large",
  "ageGroup": "adult",
  "gender": "female",
  "season": "summer",
  "fashionType": "fashion",
  "brandName": "Hagar",
  "baseColor": "black",
  "articleType": "shorts"
}
```

## Steps to run the application
1. Clone the repository
2. Build the application using the following command:
```bash
   gradle clean build
```
3. Run the application using the following command:
```bash
   java -jar build/libs/product-event-generator-0.0.1-SNAPSHOT.jar
```
4. Create a Docker image using the following command:
```bash
   docker build -t product-event-generator .
```

5. Copy the JAR File to the Mounted plugins/ Directory
Ensure your JAR file is inside the plugins directory before starting Docker Compose:
```bash
  cp build/libs/product-event-generator-1.0.jar ../plugins/
```
6. Start the Docker Compose
```bash
  docker-compose up
```
7. Verify the connector is running
```bash
  curl -X GET http://localhost:8083/connectors/product-event-generator/status
```

```bash
curl http://localhost:8083/connector-plugins | jq

  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   507  100   507    0     0   8464      0 --:--:-- --:--:-- --:--:--  8593
[
  {
    "class": "com.kafka.connect.ProductEventSourceConnector",
    "type": "source",
    "version": "1.0"
  }
]
```

8. Deploy the connector - product-event-generator
```bash
curl -X POST -H "Content-Type: application/json" --data @src/main/java/resources/product-event-generator-config.json http://localhost:8083/connectors
```
Expected Result:
```json
{
  "name": "product-event-generator",
  "config": {
    "connector.class": "com.kafka.connect.ProductEventSourceConnector",
    "tasks.max": "1",
    "topic": "product_events",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "name": "product-event-generator"
  },
  "tasks": [],
  "type": "source"
}
```

### How to deploy the kafka connector to Kubernetes
1. Create a Dockerfile for the Kafka Connector - [Dockerfile](Dockerfile)
2. Build the Docker image for the Kafka connector using the following command:
   ```bash 
     docker build -t kafka-connect-product-event-generator:latest .
   ```
3. Create the Kubernetes Deployment and Service YAML files for the Kafka connector. - [k8s-deploy.yaml](k8s-deploy.yaml)
   2.1. Create a ConfigMap to store the Kafka Connect configuration and connector configuration. - [config-map.yaml](config-map.yaml)
   2.2. Create a Deployment to run the Kafka connector. - [deployment.yaml](deployment.yaml)
   2.3. Create a Service to expose the Kafka connector. - [service.yaml](service.yaml)

4. Deploy the Kafka connector to the Kubernetes cluster.
   ```bash
    kubectl apply -f k8s-deploy.yaml
      ```
   or 
   ```bash
    kubectl apply -f config-map.yaml
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
   ```
3. Verify the Kafka connector is running.
   ```bash
     % kubectl get pods
        NAME                             READY   STATUS             RESTARTS        AGE
        kafka-connect-68c8778647-8dpcg   0/1     CrashLoopBackOff   203 (65s ago)   25h
   ```
   
4. Check the logs of the Kafka connector.
   ```bash
     kubectl logs kafka-connect-68c8778647-8dpcg
      kubectl describe pod kafka-connect-68c8778647-8dpcg

   ```
   
5. ```
4. Check the logs of the Kafka connector.
5. Scale up the Kafka connector to 3 replicas.
6. Monitor the Kafka connector.
