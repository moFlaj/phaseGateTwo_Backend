package com.phaseGateTwo.cms.userAuth.config;


import com.phaseGateTwo.cms.userAuth.models.Otp;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.data.mongodb.core.index.Index;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class MongoIndexes implements ApplicationListener<ContextRefreshedEvent> {

    private final MongoTemplate mongoTemplate;

    public MongoIndexes(MongoTemplate mongoTemplate) {
        this.mongoTemplate = mongoTemplate;
    }

    @Override
    public void onApplicationEvent(ContextRefreshedEvent event) {
        Index ttlIndex = new Index()
                .on("createdAt", Sort.Direction.ASC)
                .expire(Duration.ofMinutes(5)); // TTL 5 min

        mongoTemplate.indexOps(Otp.class).createIndex(ttlIndex);
    }
}
