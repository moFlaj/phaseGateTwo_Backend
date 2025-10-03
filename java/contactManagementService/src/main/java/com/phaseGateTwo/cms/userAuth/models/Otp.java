package com.phaseGateTwo.cms.userAuth.models;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import java.util.Date;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "otps")
public class Otp {
    @Id
    private String phoneNumber;    // PK = phone (so one OTP doc per phone)
    private String otp;
    private Date createdAt = new Date(); // ✅ must be java.util.Date

    // signup fields — null for login OTPs, populated for signup flow
    private String pendingFullName;
    private String pendingEmail;
}