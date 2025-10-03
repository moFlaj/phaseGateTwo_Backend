package com.phaseGateTwo.cms.userAuth.controllers;

import com.phaseGateTwo.cms.common.BaseIntegrationTest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.OtpValidationRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.SignUpRequest;
import com.phaseGateTwo.cms.userAuth.dtos.requests.VerifyUserRequest;
import com.phaseGateTwo.cms.userAuth.dtos.responses.VerifyUserResponse;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

public class AuthIntegrationTest extends BaseIntegrationTest {

    @Test
    void signup_shouldReturnOk() throws Exception {

        SignUpRequest req = new SignUpRequest();
        req.setEmail("testuser@example.com");
        req.setPhoneNumber("09233217123");
        req.setFullName("John Doe");


        mockMvc.perform(post("/api/auth/signup")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.verificationCode").exists()); // assuming your response includes OTP
    }

    @Test
    void shouldReturnOtp_whenNewUserSignsUp() throws Exception {
        SignUpRequest req = new SignUpRequest( "348012345678", "John Doe", "john@example.com");

        String resp = mockMvc.perform(
                        post("/api/auth/signup")
                                .contentType("application/json")
                                .content(asJson(req)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        VerifyUserResponse result = objectMapper.readValue(resp, VerifyUserResponse.class);

        assertThat(result.getPhoneNumber()).isEqualTo("348012345678");
        assertThat(result.getVerificationCode()).isNotBlank();
    }

    @Test
    void shouldConfirmSignupWithOtp() throws Exception {
        SignUpRequest req = new SignUpRequest( "348012345678", "John Doe", "john@example.com");

        String resp = mockMvc.perform(post("/api/auth/signup")
                        .contentType("application/json")
                        .content(asJson(req)))
                .andReturn().getResponse().getContentAsString();
        VerifyUserResponse otpResp = objectMapper.readValue(resp, VerifyUserResponse.class);

        // confirm
        OtpValidationRequest confirm = new OtpValidationRequest(
                otpResp.getPhoneNumber(),
                otpResp.getVerificationCode()
        );

        mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType("application/json")
                        .content(asJson(confirm)))
                .andExpect(status().isOk());
    }

    @Test
    void shouldFailSignup_whenUserAlreadyExists() throws Exception {
        SignUpRequest req = new SignUpRequest( "348012345678", "John Doe", "john@example.com");
        String resp = mockMvc.perform(post("/api/auth/signup")
                        .contentType("application/json")
                        .content(asJson(req)))
                .andReturn().getResponse().getContentAsString();
        VerifyUserResponse signupResp = objectMapper.readValue(resp, VerifyUserResponse.class);

        OtpValidationRequest validate = new OtpValidationRequest(signupResp.getPhoneNumber(), signupResp.getVerificationCode());

        mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType("application/json")
                        .content(asJson(validate)))
                .andExpect(status().isOk());


        mockMvc.perform(post("/api/auth/signup")
                        .contentType("application/json")
                        .content(asJson(req)))
                .andExpect(status().isConflict());
    }

    @Test
    void shouldReturnOtp_whenExistingUserVerifies() throws Exception {
        SignUpRequest req = new SignUpRequest( "348012345678", "John Doe", "john@example.com");
        String resp = mockMvc.perform(post("/api/auth/signup")
                        .contentType("application/json")
                        .content(asJson(req)))
                .andReturn().getResponse().getContentAsString();
        VerifyUserResponse signupResp = objectMapper.readValue(resp, VerifyUserResponse.class);

        OtpValidationRequest validate = new OtpValidationRequest(signupResp.getPhoneNumber(), signupResp.getVerificationCode());

        mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType("application/json")
                        .content(asJson(validate)))
                .andExpect(status().isOk());

        VerifyUserRequest request = new VerifyUserRequest();
        request.setPhoneNumber(req.getPhoneNumber());

        resp = mockMvc.perform(post("/api/auth/verify")
                        .contentType("application/json")
                        .content(asJson(request)))
                .andReturn().getResponse().getContentAsString();
        VerifyUserResponse result = objectMapper.readValue(resp, VerifyUserResponse.class);

        assertThat(result.getPhoneNumber()).isEqualTo(signupResp.getPhoneNumber());
        assertThat(result.getVerificationCode()).isNotBlank();
    }

    @Test
    void shouldFailConfirmation_withInvalidOtp() throws Exception {
        SignUpRequest req = new SignUpRequest("348012345679", "Jane Doe", "jane@example.com");

        String resp = mockMvc.perform(post("/api/auth/signup")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req)))
                .andReturn().getResponse().getContentAsString();

        VerifyUserResponse signupResp = objectMapper.readValue(resp, VerifyUserResponse.class);

        OtpValidationRequest invalid = new OtpValidationRequest(signupResp.getPhoneNumber(), "9999999999");

        mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(invalid)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void shouldReturnJwt_afterValidConfirmation() throws Exception {
        SignUpRequest req = new SignUpRequest("348012345680", "Mike Doe", "mike@example.com");

        String resp = mockMvc.perform(post("/api/auth/signup")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req)))
                .andReturn().getResponse().getContentAsString();

        VerifyUserResponse otpResp = objectMapper.readValue(resp, VerifyUserResponse.class);

        OtpValidationRequest confirm = new OtpValidationRequest(
                otpResp.getPhoneNumber(),
                otpResp.getVerificationCode()
        );

        String jwt = mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(confirm)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        assertThat(jwt).isNotBlank();
        assertThat(jwt).startsWith("ey");
    }

    @Test
    void shouldDenyAccessToSecuredEndpoint_withoutJwt() throws Exception {
        mockMvc.perform(get("/api/profile/view"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void shouldAllowAccessToSecuredEndpoint_withValidJwt() throws Exception {
        // Step 1: signup + confirm to get a JWT
        SignUpRequest req = new SignUpRequest("348012345681", "Lisa Doe", "lisa@example.com");

        String resp = mockMvc.perform(post("/api/auth/signup")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(req)))
                .andReturn().getResponse().getContentAsString();
        VerifyUserResponse otpResp = objectMapper.readValue(resp, VerifyUserResponse.class);

        OtpValidationRequest confirm = new OtpValidationRequest(
                otpResp.getPhoneNumber(),
                otpResp.getVerificationCode()
        );

        String jwt = mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(confirm)))
                .andReturn().getResponse().getContentAsString();

        // Step 2: call secured endpoint with Authorization header
        mockMvc.perform(get("/api/profile/view")
                        .header("Authorization", "Bearer " + jwt))
                .andExpect(status().isOk());
    }

}
