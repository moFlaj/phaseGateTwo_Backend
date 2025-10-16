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
        performSignup("09233217123", "testuser@example.com", "John Doe");
    }

    @Test
    void shouldReturnOtp_whenNewUserSignsUp() throws Exception {
        VerifyUserResponse result = performSignup("348012345678", "john@example.com", "John Doe");
        assertThat(result.getVerificationCode()).isNotBlank();
    }

    @Test
    void shouldConfirmSignupWithOtp() throws Exception {
        VerifyUserResponse otpResp = performSignup("348012345678", "john@example.com", "John Doe");
        confirmSignupAndGetJwt(otpResp);
    }

    @Test
    void shouldFailSignup_whenUserAlreadyExists() throws Exception {
        VerifyUserResponse firstSignup = performSignup("348012345678", "john@example.com", "John Doe");
        confirmSignupAndGetJwt(firstSignup);

        // duplicate signup
        mockMvc.perform(post("/api/auth/signup")
                        .contentType("application/json")
                        .content(asJson(new SignUpRequest("348012345678", "John Doe", "john@example.com"))))
                .andExpect(status().isConflict());
    }

    @Test
    void shouldReturnOtp_whenExistingUserVerifies() throws Exception {
        VerifyUserResponse signupResp = performSignup("348012345678", "john@example.com", "John Doe");
        confirmSignupAndGetJwt(signupResp);

        VerifyUserRequest verifyReq = new VerifyUserRequest();
        verifyReq.setPhoneNumber(signupResp.getPhoneNumber());

        String resp = mockMvc.perform(post("/api/auth/verify")
                        .contentType("application/json")
                        .content(asJson(verifyReq)))
                .andExpect(status().isOk())
                .andReturn().getResponse().getContentAsString();

        VerifyUserResponse result = objectMapper.readValue(resp, VerifyUserResponse.class);
        assertThat(result.getPhoneNumber()).isEqualTo(signupResp.getPhoneNumber());
        assertThat(result.getVerificationCode()).isNotBlank();
    }

    @Test
    void shouldFailConfirmation_withInvalidOtp() throws Exception {
        VerifyUserResponse signupResp = performSignup("348012345679", "jane@example.com", "Jane Doe");

        OtpValidationRequest invalid = new OtpValidationRequest(signupResp.getPhoneNumber(), "9999999999");

        mockMvc.perform(post("/api/auth/signup/confirm")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(asJson(invalid)))
                .andExpect(status().isBadRequest());
    }

    @Test
    void shouldReturnJwt_afterValidConfirmation() throws Exception {
        VerifyUserResponse otpResp = performSignup("348012345680", "mike@example.com", "Mike Doe");
        String jwt = confirmSignupAndGetJwt(otpResp);
        assertThat(jwt).isNotBlank().startsWith("ey");
    }

    @Test
    void shouldDenyAccessToSecuredEndpoint_withoutJwt() throws Exception {
        mockMvc.perform(get("/api/profile/view"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void shouldAllowAccessToSecuredEndpoint_withValidJwt() throws Exception {
        String jwt = signupAndGetJwt("348012345681", "lisa@example.com", "Lisa Doe");

        mockMvc.perform(get("/api/profile/view")
                        .header("Authorization", "Bearer " + jwt))
                .andExpect(status().isOk());
    }
}
