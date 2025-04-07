FROM confluentinc/cp-kafka-connect:7.5.5

# Copy the connector jar
COPY build/libs/product-event-generator-1.0.jar /usr/share/java/kafka-connect-source/

# Set the plugin path to include the connector
ENV CONNECT_PLUGIN_PATH="/usr/share/java,/usr/share/confluent-hub-components,/usr/share/java/kafka-connect-source"

# Ensure the target directory is writable
RUN mkdir -p /etc/kafka-connect/secrets && \
    chmod -R 777 /etc/kafka-connect/*

# Expose the REST API port
EXPOSE 8083

