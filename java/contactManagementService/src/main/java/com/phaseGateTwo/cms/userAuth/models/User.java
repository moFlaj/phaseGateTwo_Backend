package com.phaseGateTwo.cms.userAuth.models;

import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Data
@NoArgsConstructor
@Document(collection = "users")
public class User {
    @Id
    private String userId;      // Mongo generated id
    private String phoneNumber;
    private String fullName;
    private String email;
}
