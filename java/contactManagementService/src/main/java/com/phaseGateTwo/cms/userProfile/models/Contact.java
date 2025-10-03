package com.phaseGateTwo.cms.userProfile.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "contacts")
@Data
public class Contact {
    @Id
    private String contactId;
    private String fullName;
    private String email;
    private String phone;
    private String userId;

}
