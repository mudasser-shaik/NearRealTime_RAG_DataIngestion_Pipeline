package com.kafka.connect;

import org.apache.kafka.connect.source.SourceRecord;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import java.util.List;
import java.util.Map;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

public class ProductEventSourceTaskTest {

    private ProductEventSourceTask task;

    @BeforeEach
    public void setUp() {
        task = new ProductEventSourceTask();
        task.start(Map.of("topic", "test-topic"));
    }

    @Test
    public void testPoll() throws InterruptedException {
        List<SourceRecord> records = task.poll();
        assertNotNull(records);
        SourceRecord record = records.get(0);
        assertEquals("test-topic", record.topic());
        assertNotNull(record.value());
    }
}