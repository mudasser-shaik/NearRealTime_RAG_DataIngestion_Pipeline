package com.kafka.connect;

import org.apache.kafka.connect.data.Schema;
import org.apache.kafka.connect.source.SourceRecord;
import org.apache.kafka.connect.source.SourceTask;

import com.fasterxml.jackson.databind.ObjectMapper;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import java.io.IOException;
import java.util.*;

public class ProductEventSourceTask extends SourceTask {
    private static final Logger log = LoggerFactory.getLogger(ProductEventSourceTask.class);
    private String topic;
    private int counter = 0;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private Random random = new Random();

    @Override
    public String version() {
        return "1.0";
    }

    @Override
    public void start(Map<String, String> props) {
        topic = props.get("topic");
    }

    @Override
    public List<SourceRecord> poll() throws InterruptedException {
        List<SourceRecord> records = new ArrayList<>();
        Map<String, Object> productEvent = generateProductEvent();

        try {
            // Convert to JSON string
            String jsonValue = objectMapper.writeValueAsString(productEvent);
            SourceRecord record = new SourceRecord(
                    null, null, topic, null,
                    Schema.STRING_SCHEMA, String.valueOf(counter++),
                    Schema.STRING_SCHEMA, jsonValue
            );
            records.add(record);
        } catch (IOException e) {
            throw new RuntimeException("Failed to serialize product event", e);
        }

        Thread.sleep(500);  // Simulating event generation delay
        return records;
    }

    private Map<String, Object> generateProductEvent() {
        List<String> articleTypes = List.of("shoes", "sweater", "hat", "shorts", "gloves", "socks", "boots");
        List<String> sizes = List.of("small", "medium", "large", "extra large");
        List<String> fashionTypes = List.of("formal", "core", "fashion", "business casual");
        List<String> brands = List.of("Hagar", "De Banke", "Rockhill", "Calvin Klein", "Polo Ralph Lauren");
        List<String> colors = List.of("blue", "red", "purple", "black", "green", "pink", "white");
        List<String> genders = List.of("male", "female");
        List<String> ageGroups = List.of("adult", "infant");
        List<String> seasons = List.of("spring", "summer", "fall", "winter");

        Map<String, Object> event = new HashMap<>();
        event.put("store_id", random.nextInt(50));
        event.put("product_id", random.nextInt(999999));
        event.put("count", random.nextInt(20) + 1);
        event.put("articleType", articleTypes.get(random.nextInt(articleTypes.size())));
        event.put("size", sizes.get(random.nextInt(sizes.size())));
        event.put("fashionType", fashionTypes.get(random.nextInt(fashionTypes.size())));
        event.put("brandName", brands.get(random.nextInt(brands.size())));
        event.put("baseColor", colors.get(random.nextInt(colors.size())));
        event.put("gender", genders.get(random.nextInt(genders.size())));
        event.put("ageGroup", ageGroups.get(random.nextInt(ageGroups.size())));
        event.put("price", Math.round((random.nextDouble() * 100) * 100.0) / 100.0);
        event.put("season", seasons.get(random.nextInt(seasons.size())));

        return event;
    }

    @Override
    public void stop() {
        // No resources to clean up
    }
}
