package com.phaseGateTwo.cms.common;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.phaseGateTwo.cms.userAuth.dtos.requests.OtpValidationRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.SignUpRequest;
import com.phaseGateTwo.cms.userAuth.dtos.responses.VerifyUserResponse;
import org.junit.jupiter.api.BeforeEach;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import org.springframework.data.mongodb.core.MongoTemplate;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.junit.jupiter.Testcontainers;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
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


    static MongoDBContainer mongo = new MongoDBContainer("mongo:7.0.23");

    static {
        mongo.start();
    }

    @DynamicPropertySource
    static void mongoProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.data.mongodb.uri", mongo::getReplicaSetUrl);
    }

    // Serialize any object into JSON
    protected String asJson(Object obj) throws Exception {
        return objectMapper.writeValueAsString(obj);
    }

    // Clean DB before each test
    @BeforeEach
    void cleanDatabase() {
        mongoTemplate.getDb().drop();
    }

    // --- 🔹 NEW HELPERS BELOW 🔹 ---

    /**
     * Handles the signup request and returns the verification response.
     */
    protected VerifyUserResponse performSignup(String phone, String email, String fullName) throws Exception {
        SignUpRequest request = new SignUpRequest(phone, fullName, email);

        String response = mockMvc.perform(post("/api/auth/signup")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(request)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        VerifyUserResponse verifyResponse = objectMapper.readValue(response, VerifyUserResponse.class);
        assertThat(verifyResponse.getPhoneNumber()).isEqualTo(phone);
        assertThat(verifyResponse.getVerificationCode()).isNotBlank();

        return verifyResponse;
    }

    /**
     * Confirms OTP verification and returns a JWT token string.
     */
    protected String confirmSignupAndGetJwt(VerifyUserResponse otpResponse) throws Exception {
        OtpValidationRequest confirm = new OtpValidationRequest(
                otpResponse.getPhoneNumber(),
                otpResponse.getVerificationCode()
        );

        String jwt = mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(confirm)))
                .andExpect(status().isOk())
                .andReturn()
                .getResponse()
                .getContentAsString();

        assertThat(jwt).isNotBlank().startsWith("ey");
        return jwt;
    }

    /**
     * Utility wrapper that does both signup + confirm → returns JWT.
     */
    protected String signupAndGetJwt(String phone, String email, String fullName) throws Exception {
        VerifyUserResponse otpResponse = performSignup(phone, email, fullName);
        return confirmSignupAndGetJwt(otpResponse);
    }
}
