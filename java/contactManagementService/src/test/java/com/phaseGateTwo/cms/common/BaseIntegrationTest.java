package com.phaseGateTwo.cms.common;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.annotation.Import;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.containers.MongoDBContainer;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.context.ApplicationContext;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("test")
@Testcontainers
public abstract class BaseIntegrationTest {

    @Autowired
    protected MockMvc mockMvc;

    @Autowired
    protected ObjectMapper objectMapper;

    @Autowired
    protected MongoTemplate mongoTemplate;

    @Autowired
    protected ApplicationContext applicationContext;


    @Autowired
    private org.springframework.core.env.Environment env;


    // start MongoDB Testcontainer once for all tests
    static MongoDBContainer mongo = new MongoDBContainer("mongo:7.0.23");

    static {
        mongo.start();
    }

    @DynamicPropertySource
    static void mongoProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.data.mongodb.uri", mongo::getReplicaSetUrl);
    }

    // Utility method to serialize any object into JSON
    protected String asJson(Object obj) throws Exception {
        return objectMapper.writeValueAsString(obj);
    }

    // Clean DB before each test
    @BeforeEach
    void cleanDatabase() {
        mongoTemplate.getDb().drop();
    }

    @BeforeEach
    void printContextPath() {
        System.out.println(">>> Context path = " + env.getProperty("server.servlet.context-path"));
    }



    @BeforeEach
    void printBeans() {
        String[] beans = applicationContext.getBeanDefinitionNames();
        System.out.println(">>> Beans loaded in test: ");
        for (String bean : beans) {
            if (bean.toLowerCase().contains("security")) {
                System.out.println("   - " + bean);
            }
        }
    }



}
