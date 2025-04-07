package com.kafka.connect;

import org.apache.kafka.common.config.ConfigDef;
import org.apache.kafka.connect.source.SourceConnector;
import org.apache.kafka.connect.source.SourceTask;
import java.util.List;
import java.util.Map;

public class ProductEventSourceConnector extends SourceConnector {
    private String topic;

    @Override
    public void start(Map<String, String> props) {
        topic = props.get("topic");
    }

    @Override
    public Class<? extends SourceTask> taskClass() {
        return ProductEventSourceTask.class;
    }

    @Override
    public List<Map<String, String>> taskConfigs(int maxTasks) {
        return List.of(Map.of("topic", topic));
    }

    @Override
    public void stop() {}

    @Override
    public ConfigDef config() {
        return new ConfigDef().define("topic", ConfigDef.Type.STRING, ConfigDef.Importance.HIGH, "Topic to publish to");
    }

    @Override
    public String version() {
        return "1.0";
    }
}
